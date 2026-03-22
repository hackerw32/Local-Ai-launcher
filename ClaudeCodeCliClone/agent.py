"""
Architect and Worker agents.

Architect  →  explores codebase, produces a detailed plan
Worker     →  reads the plan, uses tools to implement it, reports results
"""

from pathlib import Path
from typing import Optional
import ollama

from tools import ToolExecutor, TOOL_DEFINITIONS
from prompts import ARCHITECT_SYSTEM, WORKER_SYSTEM


class BaseAgent:
    """
    Runs the tool-calling loop for a given model.
    Each iteration:
      1. Call the model
      2. If it returns tool_calls → execute them, feed results back
      3. If it returns plain text → we are done, return that text
    """

    def __init__(
        self,
        model: str,
        client: ollama.Client,
        tool_executor: ToolExecutor,
        ui,
        role: str,
        max_iterations: int = 20,
    ):
        self.model = model
        self.client = client
        self.tools = tool_executor
        self.ui = ui
        self.role = role
        self.max_iterations = max_iterations

    def _chat(self, messages: list) -> ollama.ChatResponse:
        return self.client.chat(
            model=self.model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            options={
                "temperature": 0.1,   # Low temp = precise, deterministic
                "num_ctx": 16384,     # Large context for multi-file work
            },
        )

    def _run(self, messages: list) -> str:
        """Main agent loop. Returns the final text response."""
        for iteration in range(self.max_iterations):
            try:
                response = self._chat(messages)
            except Exception as e:
                self.ui.error(f"[{self.role}] Model call failed: {e}")
                return f"Error: {e}"

            msg = response.message

            # Always append the assistant message to history
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
            })

            # No tool calls → the agent is done
            if not msg.tool_calls:
                return msg.content or "(no response)"

            # Execute each tool call and feed results back
            for tc in msg.tool_calls:
                name = tc.function.name
                args = tc.function.arguments or {}

                self.ui.tool_call(self.role, name, args)
                result = self.tools.execute(name, args)
                self.ui.tool_result(result)

                messages.append({
                    "role": "tool",
                    "content": result,
                })

        return f"[{self.role}] Reached max iterations ({self.max_iterations}) without finishing."


class ArchitectAgent(BaseAgent):
    def __init__(self, model: str, client: ollama.Client, project_path: Path, ui):
        executor = ToolExecutor(project_path)
        super().__init__(model, client, executor, ui, role="Architect")
        self.project_path = project_path

    def create_plan(self, user_request: str, conversation_context: list) -> str:
        self.ui.section("Architect", f"model={self.model}")

        messages = [{"role": "system", "content": ARCHITECT_SYSTEM}]

        # Include recent conversation context (last 3 exchanges = 6 messages)
        if conversation_context:
            messages.extend(conversation_context[-6:])

        messages.append({
            "role": "user",
            "content": (
                f"Project root: {self.project_path}\n\n"
                f"User request:\n{user_request}\n\n"
                "Please explore the codebase with your tools and then produce a precise implementation plan."
            ),
        })

        return self._run(messages)


class WorkerAgent(BaseAgent):
    def __init__(self, model: str, client: ollama.Client, project_path: Path, ui):
        executor = ToolExecutor(project_path)
        super().__init__(model, client, executor, ui, role="Worker")
        self.project_path = project_path

    def execute_plan(self, plan: str, original_request: str) -> str:
        self.ui.section("Worker", f"model={self.model}")

        messages = [
            {"role": "system", "content": WORKER_SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Project root: {self.project_path}\n\n"
                    f"Original user request:\n{original_request}\n\n"
                    f"Implementation plan from Architect:\n{plan}\n\n"
                    "Implement the plan step by step. "
                    "Remember: read each file before modifying it, "
                    "write complete files only, and verify with run_command when possible."
                ),
            },
        ]

        return self._run(messages)
