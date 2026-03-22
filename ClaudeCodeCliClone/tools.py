"""
Tools available to both the Architect and Worker agents.
Each tool is safe, bounded, and returns clear error messages.
"""

import os
import subprocess
import fnmatch
from pathlib import Path

# Max sizes to protect against huge files flooding the context window
MAX_FILE_BYTES = 150_000   # 150 KB
MAX_OUTPUT_BYTES = 30_000  # 30 KB for command output

# Directories always skipped in listings
SKIP_DIRS = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env',
    '.idea', '.vscode', 'build', 'dist', '.gradle', '.dart_tool',
    'out', 'target', '.next', '.nuxt', 'coverage',
}


class ToolExecutor:
    def __init__(self, project_path: Path):
        self.project_path = project_path.resolve()

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.project_path / p
        return p.resolve()

    # ------------------------------------------------------------------
    # read_file
    # ------------------------------------------------------------------
    def read_file(self, path: str) -> str:
        try:
            p = self._resolve(path)
            if not p.exists():
                return f"ERROR: File not found: {path}"
            if not p.is_file():
                return f"ERROR: Not a file: {path}"
            size = p.stat().st_size
            if size > MAX_FILE_BYTES:
                return (f"ERROR: File too large ({size:,} bytes, max {MAX_FILE_BYTES:,}). "
                        f"Use search_code to find specific sections.")
            return p.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            return f"ERROR reading file: {e}"

    # ------------------------------------------------------------------
    # write_file
    # ------------------------------------------------------------------
    def write_file(self, path: str, content: str) -> str:
        try:
            p = self._resolve(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding='utf-8')
            return f"SUCCESS: Wrote {len(content):,} chars to {path}"
        except Exception as e:
            return f"ERROR writing file: {e}"

    # ------------------------------------------------------------------
    # list_directory
    # ------------------------------------------------------------------
    def list_directory(self, path: str = ".", pattern: str = "*") -> str:
        try:
            p = self._resolve(path)
            if not p.exists():
                return f"ERROR: Directory not found: {path}"
            if not p.is_dir():
                return f"ERROR: Not a directory: {path}"

            items = []
            for item in sorted(p.iterdir()):
                if item.name in SKIP_DIRS:
                    continue
                if not fnmatch.fnmatch(item.name, pattern):
                    continue
                if item.is_dir():
                    items.append(f"📁  {item.name}/")
                else:
                    kb = item.stat().st_size / 1024
                    items.append(f"📄  {item.name}  ({kb:.1f} KB)")

            if not items:
                return f"(empty directory: {path})"
            rel = os.path.relpath(p, self.project_path)
            return f"Directory: {rel}/\n" + "\n".join(items)
        except Exception as e:
            return f"ERROR listing directory: {e}"

    # ------------------------------------------------------------------
    # search_code
    # ------------------------------------------------------------------
    def search_code(self, query: str, path: str = ".") -> str:
        try:
            p = self._resolve(path)
            # Search across common source file types
            extensions = [
                '*.py', '*.kt', '*.java', '*.js', '*.ts', '*.tsx',
                '*.jsx', '*.html', '*.css', '*.xml', '*.json', '*.yaml',
                '*.yml', '*.go', '*.rs', '*.cpp', '*.c', '*.h',
            ]
            include_args = []
            for ext in extensions:
                include_args += ['--include', ext]

            cmd = ['grep', '-r', '-n', '-l'] + include_args + [query, str(p)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

            matching_files = [f for f in result.stdout.strip().split('\n') if f.strip()]
            if not matching_files:
                return f"No source files found containing: '{query}'"

            lines_out = [f"Files containing '{query}' ({len(matching_files)} found):"]
            for fpath in matching_files[:20]:
                rel = os.path.relpath(fpath, self.project_path)
                lines_out.append(f"\n{rel}:")
                # Show up to 6 matching lines per file
                grep = subprocess.run(
                    ['grep', '-n', query, fpath],
                    capture_output=True, text=True, timeout=5
                )
                for line in grep.stdout.strip().split('\n')[:6]:
                    lines_out.append(f"  {line}")

            return '\n'.join(lines_out)
        except subprocess.TimeoutExpired:
            return "ERROR: Search timed out"
        except Exception as e:
            return f"ERROR searching: {e}"

    # ------------------------------------------------------------------
    # run_command
    # ------------------------------------------------------------------
    BLOCKED_PATTERNS = [
        'rm -rf /', 'rmdir /s /q c:', 'mkfs', ':(){:|:&};:',
        'dd if=/dev/zero', '> /dev/sda',
    ]

    def run_command(self, command: str, timeout: int = 60) -> str:
        lower_cmd = command.lower()
        for blocked in self.BLOCKED_PATTERNS:
            if blocked in lower_cmd:
                return f"ERROR: Potentially destructive command blocked: {command}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = result.stdout + result.stderr
            if len(output) > MAX_OUTPUT_BYTES:
                output = output[:MAX_OUTPUT_BYTES] + "\n... [output truncated]"
            status = "OK" if result.returncode == 0 else f"FAILED (exit code {result.returncode})"
            return f"[{status}]\n{output}" if output.strip() else f"[{status}] (no output)"
        except subprocess.TimeoutExpired:
            return f"ERROR: Command timed out after {timeout}s: {command}"
        except Exception as e:
            return f"ERROR running command: {e}"

    # ------------------------------------------------------------------
    # create_directory
    # ------------------------------------------------------------------
    def create_directory(self, path: str) -> str:
        try:
            p = self._resolve(path)
            p.mkdir(parents=True, exist_ok=True)
            return f"SUCCESS: Created directory: {path}"
        except Exception as e:
            return f"ERROR creating directory: {e}"

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------
    def execute(self, tool_name: str, args: dict) -> str:
        dispatch = {
            'read_file':       lambda a: self.read_file(a.get('path', '')),
            'write_file':      lambda a: self.write_file(a.get('path', ''), a.get('content', '')),
            'list_directory':  lambda a: self.list_directory(a.get('path', '.'), a.get('pattern', '*')),
            'search_code':     lambda a: self.search_code(a.get('query', ''), a.get('path', '.')),
            'run_command':     lambda a: self.run_command(a.get('command', '')),
            'create_directory':lambda a: self.create_directory(a.get('path', '')),
        }
        if tool_name not in dispatch:
            return f"ERROR: Unknown tool '{tool_name}'. Available: {list(dispatch.keys())}"
        return dispatch[tool_name](args)


# ------------------------------------------------------------------
# Ollama tool definitions (sent with every API call)
# ------------------------------------------------------------------
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the complete contents of a file. "
                "You MUST call this before write_file on any file you intend to modify."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path, relative to project root or absolute",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write COMPLETE content to a file, replacing it entirely. "
                "Never write partial content. Never use '# ...' placeholders. "
                "You MUST call read_file first."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {
                        "type": "string",
                        "description": "Complete file content (not a diff, not partial)",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List the files and folders in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path (default: project root '.')",
                        "default": ".",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Glob filter, e.g. '*.py' or '*.kt' (default: '*')",
                        "default": "*",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Search for a text pattern across all source files in the project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text or grep-compatible pattern to search for",
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search in (default: project root '.')",
                        "default": ".",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Execute a shell command in the project directory. "
                "Use for: syntax checks (python -m py_compile), running tests, "
                "checking build output, listing file trees, etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to run",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Create a directory (and any missing parent directories).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to create"}
                },
                "required": ["path"],
            },
        },
    },
]
