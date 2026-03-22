# Claude Code CLI Clone

A **local AI coding assistant** that mimics Claude Code's architect + worker pattern, running entirely on your hardware via Ollama.

```
User Input
    ↓
Architect AI  →  [explores code with tools]  →  Detailed Plan
    ↓
Worker AI  →  [reads files, writes code, verifies]  →  Result
```

**No cloud. No API keys. No cost. Just you, your GPU/CPU, and open-source AI models.**

---

## What Makes This Different

| Feature | vs. Aider | vs. ChatGPT |
|---------|-----------|-----------|
| Tool-calling loop | ✓ Smart exploration | ❌ Text only |
| Architect + Worker | ✓ Plan then execute | ❌ Single pass |
| Read before write | ✓ Forces sanity | ❌ Often guesses |
| Local only | ✓ Your data stays yours | ❌ Cloud dependent |
| Free | ✓ Forever | ❌ Paid API |

---

## Quick Start

### 1. Install Dependencies

```bash
cd ClaudeCodeCliClone
pip install -r requirements.txt
```

### 2. Pull AI Models (one-time)

```bash
# For CPU (Xeon, 64GB RAM)
ollama pull qwen2.5-coder:14b
ollama pull qwen2.5-coder:7b

# For GPU (RTX 5060 16GB)
ollama pull qwen2.5-coder:32b
ollama pull qwen2.5-coder:14b
```

### 3. Run It

```bash
python main.py /path/to/your/project
```

Or just use current directory:
```bash
python main.py
```

### 4. Give Instructions

```
> Add a login function to auth.py
> Create unit tests for the database module
> Fix the bug in line 45 of main.py
```

---

## Hardware Profiles

Switch instantly with `/profile`:

### CPU Profile (Your Current Hardware)
```
/profile cpu

Architect: qwen2.5-coder:14b   (4-6 tok/s, ~9 GB RAM)
Worker:    qwen2.5-coder:7b    (8-12 tok/s, ~4.5 GB RAM)
Total:     ~13.5 GB RAM used
```

### GPU Profile (When You Get RTX 5060)
```
/profile gpu

Architect: qwen2.5-coder:32b   (20-30 tok/s, fits in VRAM)
Worker:    qwen2.5-coder:14b   (50-70 tok/s, fully in VRAM)
Total:     ~27 GB VRAM used
```

---

## Available Commands

| Command | Purpose |
|---------|---------|
| `/help` | Show all commands |
| `/models` | Show current model config |
| `/profile cpu` | Switch to CPU profile |
| `/profile gpu` | Switch to GPU profile |
| `/set architect <model>` | Manually change architect model |
| `/set worker <model>` | Manually change worker model |
| `/set host <url>` | Change Ollama server address |
| `/clear` | Clear terminal |
| `/quit` | Exit |

### Examples

```bash
# Switch to GPU when you upgrade
/profile gpu

# Use a better reasoning model for architect
/set architect deepseek-r1:14b

# Use a faster worker for simple tasks
/set worker qwen2.5-coder:7b
```

---

## Model Selection Guide

### What Models Support Tool Calling?

✅ **Works great with this tool:**
- `qwen2.5-coder:*` — Best for code, native tool support
- `llama3.1:*` and `llama3.2:*` — Good, native tool support
- `mistral-nemo:*` — Fast, native tool support
- `deepseek-r1:*` — Explicit reasoning, smart planning

❌ **Does NOT work:**
- `codellama:*` — No tool calling
- `llama2:*` — Too old, no tool calling
- `mistral:*` (old) — No tool calling

### Quality Ranking (Best to Worst)

For **coding tasks**:
```
qwen2.5-coder > deepseek-coder-v2 > codellama > llama3.x
```

For **reasoning/planning** (Architect role):
```
deepseek-r1 > qwen2.5-coder > codellama
```

For **raw speed**:
```
7b-models > 14b-models > 32b-models
```

### Recommended Combinations

| Use Case | Architect | Worker |
|----------|-----------|--------|
| Fast iteration | `qwen2.5-coder:7b` | `qwen2.5-coder:7b` |
| Balanced | `qwen2.5-coder:14b` | `qwen2.5-coder:7b` |
| Maximum quality | `qwen2.5-coder:32b` | `qwen2.5-coder:14b` |
| Smart planning | `deepseek-r1:14b` | `qwen2.5-coder:7b` |

---

## How It Works

### Phase 1: Architect Plans

The Architect receives your request and **explores the codebase**:
- Lists directory structure with `list_directory`
- Reads relevant files with `read_file`
- Searches for patterns with `search_code`
- Runs commands to understand project structure

Then outputs a **precise implementation plan** with:
- Exact file paths
- Exact changes to make
- Order of changes
- How to verify success

### Phase 2: Worker Executes

The Worker receives the plan and **implements it methodically**:

1. **Reads** each file before touching it
2. **Plans** the exact changes needed
3. **Writes** complete files (never partial diffs)
4. **Verifies** with syntax checks and tests
5. **Reports** what was changed and how to verify

### Why This Reduces Errors

```
❌ Single model approach (Aider):
   → Reads some files, guesses the rest
   → Writes diffs (fragile, often wrong)
   → One chance to get it right

✅ Architect + Worker approach:
   → Architect forces 100% exploration first
   → Worker reads EVERY file before writing
   → Worker writes complete files (no guessing)
   → Verification step catches errors
```

---

## Configuration File

Settings are saved to `~/.claude_clone_config.json`:

```json
{
  "ollama_host": "http://localhost:11434",
  "architect_model": "qwen2.5-coder:14b",
  "worker_model": "qwen2.5-coder:7b",
  "context_window": 16384,
  "active_profile": "cpu",
  "max_iterations": 20
}
```

Edit manually or use `/set` commands to change.

---

## Performance Estimates

### Xeon E5-2690v4 (CPU only)

| Model | Tokens/sec | Memory | Good For |
|-------|-----------|--------|----------|
| 7b Q4_K_M | 8-12 | 4.5 GB | Fast drafts |
| 14b Q4_K_M | 4-6 | 9 GB | Balanced work |
| 32b Q4_K_M | 2-3 | 19 GB | Maximum quality |

**Example task:** Add 50-line feature
- Planning: 2-3 min (architect exploring)
- Implementation: 3-5 min (worker writing)
- **Total: 5-8 minutes**

### RTX 5060 (16 GB VRAM)

| Model | Tokens/sec | Memory | Good For |
|-------|-----------|--------|----------|
| 7b Q4_K_M | 80-100 | 4.5 GB | Ultra-fast |
| 14b Q4_K_M | 50-70 | 9 GB | Balanced & quick |
| 32b Q4_K_M | 20-30* | 18 GB | Best quality |

*Architect 32b partially offloads to CPU, still much faster than pure CPU.

**Example task:** Add 50-line feature
- Planning: 20-30 sec
- Implementation: 1-2 min
- **Total: ~2 minutes**

---

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, start the CLI Clone
python main.py /your/project
```

### "Model not found"
```bash
# Check what you have
ollama list

# Pull the missing model
ollama pull qwen2.5-coder:14b
```

### "Out of memory"
- Reduce context window: `/set context_window 8192`
- Use smaller models: `/set architect qwen2.5-coder:7b`
- Close other applications

### "Model makes lots of mistakes"
- Switch to a larger model: `/set architect qwen2.5-coder:32b`
- Use reasoning model: `/set architect deepseek-r1:14b`
- Give more specific instructions (include file paths)

### "Too slow on CPU"
- Use smaller models: `/set architect qwen2.5-coder:7b`
- Reduce context window: `/set context_window 8192`
- Upgrade GPU when possible 😊

---

## Architecture Details

### File Structure

```
ClaudeCodeCliClone/
├── main.py           # Entry point, REPL loop, command handling
├── agent.py          # ArchitectAgent & WorkerAgent classes
├── tools.py          # File/directory/command tools
├── prompts.py        # System prompts (THE MAGIC)
├── config.py         # Config management + hardware profiles
├── ui.py             # Terminal UI (rich formatting)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

### Tool Definitions

Both agents have access to:

- `read_file(path)` — Read file contents (max 150 KB)
- `write_file(path, content)` — Write complete file (replaces entire file)
- `list_directory(path, pattern)` — List files/dirs
- `search_code(query, path)` — Grep-like search across source files
- `run_command(command)` — Execute shell commands (tests, syntax checks, etc.)
- `create_directory(path)` — Create directories

### System Prompts

See `prompts.py`:
- **ARCHITECT_SYSTEM** — Forces exploration, then planning
- **WORKER_SYSTEM** — Enforces "read before write" discipline

These are the **key differentiators** from other tools. They're tuned to prevent the most common mistakes.

---

## Advanced Usage

### Custom Model Combinations

```bash
# Use the fastest architect, slowest worker (for quality)
/set architect qwen2.5-coder:7b
/set worker qwen2.5-coder:32b

# Use explicit reasoning for hard problems
/set architect deepseek-r1:32b

# Fall back to a generic model if you prefer
/set architect llama2-uncensored:13b
```

### Increase Context Window for Large Codebases

```bash
/set context_window 32768   # 32K tokens (uses more RAM)
```

### Reduce Max Iterations if Tool Loop Gets Stuck

```bash
/set max_iterations 10   # Default is 20
```

---

## Tips for Best Results

1. **Be specific** — Include file paths and line numbers
   ```
   ✓ "Add error handling to the fetch() function in api.py, around line 45"
   ✗ "Fix the code"
   ```

2. **Ask for one thing at a time** — Architect plans better with focused requests
   ```
   ✓ "Create a login form component"
   ✗ "Create login, register, forgot password, and 2FA"
   ```

3. **Let the Architect explore** — Don't rush the planning phase
   ```
   If it takes 2-3 minutes to plan, that's good.
   The Worker will execute faster and more accurately.
   ```

4. **Trust the tool loop** — If the model says it's reading a file, let it
   ```
   Don't interrupt unless there's an obvious infinite loop.
   The max_iterations safeguard prevents runaway.
   ```

5. **Check the Worker's output** — Review what was changed
   ```
   The result panel shows all changes made.
   Run tests afterward to verify: python -m pytest tests/
   ```

---

## Comparison with Aider

| Feature | Aider | Claude Clone |
|---------|-------|--------------|
| Planning phase | None | ✓ Full exploration |
| Architect role | None | ✓ Dedicated agent |
| Read before write | Sometimes | ✓ Always |
| Tool calling | Limited | ✓ Full suite |
| Diff-based edits | ✓ (can break) | ✗ Complete files |
| Local models | ✓ via Ollama | ✓ via Ollama |
| Code understanding | Good | ✓ Better (architect) |

---

## Future Improvements

Potential enhancements (not implemented):
- Streaming output for faster feedback
- Git integration (read diffs, create branches)
- Linter/formatter integration
- Multi-file refactoring with dependency tracking
- Test generation and execution
- Code review mode (critique without changing)

---

## License

Use freely. Open source. No restrictions.

---

## Questions?

Check `/help` in the CLI for quick reference.

Read `prompts.py` to understand how the architect and worker think.

Experiment with different model combinations — every hardware setup is different.

**Happy coding! 🚀**
