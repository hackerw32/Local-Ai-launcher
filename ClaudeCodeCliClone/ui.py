"""
Terminal UI — pretty output using 'rich' if available, plain text otherwise.
"""

import os
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.rule import Rule
    from rich.markdown import Markdown
    _console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    _console = None


# ANSI fallback colours (used when rich is not installed)
class _C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    BLUE   = "\033[34m"
    CYAN   = "\033[36m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    RED    = "\033[31m"
    MAGENTA= "\033[35m"


BANNER = r"""
 ██████╗██╗      ██████╗ ███╗   ██╗███████╗
██╔════╝██║     ██╔═══██╗████╗  ██║██╔════╝
██║     ██║     ██║   ██║██╔██╗ ██║█████╗
██║     ██║     ██║   ██║██║╚██╗██║██╔══╝
╚██████╗███████╗╚██████╔╝██║ ╚████║███████╗
 ╚═════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝
         Code CLI Clone  —  Local AI
"""


class UI:
    # ------------------------------------------------------------------
    # Banner & help
    # ------------------------------------------------------------------
    def print_banner(self):
        if HAS_RICH:
            _console.print(BANNER, style="bold cyan")
            _console.print(
                "[dim]Architect plans. Worker implements. All local, all yours.[/dim]\n"
            )
        else:
            print(_C.CYAN + _C.BOLD + BANNER + _C.RESET)
            print("  Architect plans. Worker implements. All local.\n")

    def print_help(self):
        help_text = """
Commands
────────
  /help                     Show this help
  /models                   Show current model config
  /set architect <model>    Change the Architect model
  /set worker <model>       Change the Worker model
  /set host <url>           Change the Ollama host
  /clear                    Clear the screen
  /quit  or  /exit          Exit

Examples
────────
  /set architect deepseek-r1:14b
  /set worker qwen2.5-coder:7b

Recommended models for your CPU (64 GB RAM)
────────────────────────────────────────────
  Architect (best quality):   qwen2.5-coder:32b   (~2-3 tok/s on CPU)
  Architect (good balance):   qwen2.5-coder:14b   (~4-6 tok/s on CPU)
  Architect (with reasoning): deepseek-r1:14b     (slower, smarter)
  Worker   (recommended):     qwen2.5-coder:7b    (~8-10 tok/s on CPU)

Install a model:   ollama pull qwen2.5-coder:14b
"""
        if HAS_RICH:
            _console.print(Markdown(help_text))
        else:
            print(help_text)

    # ------------------------------------------------------------------
    # Model listing & config
    # ------------------------------------------------------------------
    def print_models(self, available: list):
        if HAS_RICH:
            _console.print("\n[bold]Available Ollama models:[/bold]")
            for m in available:
                _console.print(f"  [cyan]•[/cyan] {m}")
            _console.print()
        else:
            print("\nAvailable Ollama models:")
            for m in available:
                print(f"  • {m}")
            print()

    def print_model_config(self, config):
        if HAS_RICH:
            _console.print(
                f"\n[bold]Configuration[/bold]\n"
                f"  Architect model : [cyan]{config.architect_model}[/cyan]\n"
                f"  Worker model    : [cyan]{config.worker_model}[/cyan]\n"
                f"  Ollama host     : [cyan]{config.ollama_host}[/cyan]\n"
                f"  Context window  : [cyan]{config.context_window}[/cyan] tokens\n"
            )
        else:
            print(f"\nConfiguration:")
            print(f"  Architect model : {config.architect_model}")
            print(f"  Worker model    : {config.worker_model}")
            print(f"  Ollama host     : {config.ollama_host}")
            print(f"  Context window  : {config.context_window} tokens\n")

    # ------------------------------------------------------------------
    # Section headers (Architect / Worker)
    # ------------------------------------------------------------------
    def section(self, title: str, detail: str = ""):
        if HAS_RICH:
            _console.print(Rule(f"[bold blue]{title}[/bold blue] [dim]{detail}[/dim]"))
        else:
            sep = "─" * 60
            print(f"\n{sep}")
            print(f"  {title}  {detail}")
            print(sep)

    # ------------------------------------------------------------------
    # Tool calls
    # ------------------------------------------------------------------
    def tool_call(self, agent: str, tool_name: str, args: dict):
        # Build a short, readable representation of the arguments
        args_repr = "  ".join(
            f"{k}={repr(v)[:60]}" for k, v in args.items() if k != "content"
        )
        if HAS_RICH:
            _console.print(
                f"  [dim cyan]⚙  {tool_name}[/dim cyan]"
                f"[dim]({args_repr})[/dim]"
            )
        else:
            print(f"  ⚙  {tool_name}({args_repr})")

    def tool_result(self, result: str):
        # Show only the first line so the terminal doesn't get flooded
        first = result.split('\n')[0].strip()
        if HAS_RICH:
            _console.print(f"     [dim green]↳ {first}[/dim green]")
        else:
            print(f"     ↳ {first}")

    # ------------------------------------------------------------------
    # Plan / Result panels
    # ------------------------------------------------------------------
    def plan(self, text: str):
        if HAS_RICH:
            _console.print(
                Panel(Markdown(text), title="[bold yellow]Plan[/bold yellow]",
                      border_style="yellow", padding=(1, 2))
            )
        else:
            print("\n" + "=" * 60)
            print(" PLAN")
            print("=" * 60)
            print(text)
            print("=" * 60)

    def result(self, text: str):
        if HAS_RICH:
            _console.print(
                Panel(Markdown(text), title="[bold green]Done[/bold green]",
                      border_style="green", padding=(1, 2))
            )
        else:
            print("\n" + "=" * 60)
            print(" RESULT")
            print("=" * 60)
            print(text)
            print("=" * 60)

    # ------------------------------------------------------------------
    # Status messages
    # ------------------------------------------------------------------
    def thinking(self, msg: str):
        if HAS_RICH:
            _console.print(f"[dim yellow]  ⟳  {msg}[/dim yellow]")
        else:
            print(f"  ... {msg}")

    def info(self, msg: str):
        if HAS_RICH:
            _console.print(f"[blue]ℹ  {msg}[/blue]")
        else:
            print(f"[INFO] {msg}")

    def warning(self, msg: str):
        if HAS_RICH:
            _console.print(f"[yellow]⚠  {msg}[/yellow]")
        else:
            print(f"[WARN] {msg}")

    def error(self, msg: str):
        if HAS_RICH:
            _console.print(f"[bold red]✗  {msg}[/bold red]")
        else:
            print(f"[ERROR] {msg}", file=sys.stderr)

    def success(self, msg: str):
        if HAS_RICH:
            _console.print(f"[bold green]✓  {msg}[/bold green]")
        else:
            print(f"[OK] {msg}")

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------
    def prompt(self) -> str:
        if HAS_RICH:
            return "\n[bold magenta]>[/bold magenta] "
        return "\n> "

    def clear(self):
        os.system("clear" if os.name != "nt" else "cls")
