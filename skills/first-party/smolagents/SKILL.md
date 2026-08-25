---
name: smolagents
description: "Hugging Face `smolagents`: choosing CodeAgent vs ToolCallingAgent, the model backends (InferenceClientModel, LiteLLMModel, TransformersModel, OpenAIModel), defining tools with `@tool` or a `Tool` subclass, the sandbox choice for the Python that CodeAgent executes, managed-agent hierarchies, and memory/step surgery. Use when the user names smolagents, CodeAgent, ToolCallingAgent, or InferenceClientModel, when code contains `from smolagents`, or when running the `smolagent` CLI. Scope boundary: this covers the smolagents library only — an agent-building request with no framework chosen belongs to `build-agents`/`eve`, Pydantic AI to `building-pydantic-ai-agents`, LangChain/LangGraph to that pack, and Hub API scripting to `huggingface-tool-builder`/`hf-cli`."
metadata:
  priority: 7
  pathPatterns: []
  bashPatterns:
    - '\bsmolagent\b'
    - '\bpip install\b.*\bsmolagents\b'
  importPatterns:
    - 'from smolagents'
    - 'import smolagents'
  docs:
    - "https://huggingface.co/docs/smolagents/index"
    - "https://huggingface.co/docs/smolagents/guided_tour"
    - "https://huggingface.co/docs/smolagents/tutorials/secure_code_execution"
---

# smolagents

Verified against `huggingface/smolagents` @ `30bb1161` (`1.27.0.dev0`, main) and tag `v1.26.0` — the API surface below is identical in both. Agents are **synchronous**; there is no `arun`. Offload to a thread (`anyio.to_thread.run_sync(agent.run, task)`) inside async servers.

Extras gate everything: `[toolkit]` for `WebSearchTool`/`VisitWebpageTool` and `add_base_tools=True`; `[litellm]` `[openai]` `[transformers]` `[vllm]` `[mlx-lm]` `[bedrock]` for the matching model class; `[e2b]` `[docker]` `[modal]` `[blaxel]` for sandboxes; `[mcp]` for `MCPClient`; `[telemetry]` for OTel. `pip install 'smolagents[all]'` for everything.

## API currency — check these before trusting any tutorial

Most third-party smolagents material predates these renames. Names in the left column **do not exist**; importing them raises `ImportError`.

| Removed / stale | Current | Note |
|---|---|---|
| `HfApiModel`, `HfApiEngine` | `InferenceClientModel` | Only survives as a load-time shim in `from_hub`, which rewrites it and warns. |
| `ManagedAgent` | `managed_agents=[...]` kwarg | The wrapper class is gone; pass agents that have `name` + `description`. |
| `ReactCodeAgent`, `ReactJsonAgent` | `CodeAgent`, `ToolCallingAgent` | |
| `LiteLLMEngine`, `TransformersEngine` | `LiteLLMModel`, `TransformersModel` | "Engine" naming is dead throughout. |
| `agent.logs` | `agent.memory.steps` | `agent.logs` no longer exists — the published guided tour is stale here. |
| `RunResult.messages` | `RunResult.steps` | Deprecated since 1.22.0, emits `FutureWarning`. |

Still exported and current: `OpenAIServerModel`, `AzureOpenAIServerModel`, `AmazonBedrockServerModel` — these are plain aliases of `OpenAIModel` / `AzureOpenAIModel` / `AmazonBedrockModel`. Either name works; prefer the short one in new code.

## Pick the agent class

| | `CodeAgent` | `ToolCallingAgent` |
|---|---|---|
| Action format | Python source, executed | JSON tool call, validated |
| Executes arbitrary code | **Yes** — see Sandboxing | No |
| Good at | chaining, loops, data transforms, composing tool outputs | one atomic call per step, dispatching |
| Costs you | a sandbox decision, syntax/runtime errors | expressivity; every action must be a predefined tool |
| Extra knobs | `additional_authorized_imports`, `executor_type`, `code_block_tags` | `max_tool_threads` (parallel tool calls) |

Default to `CodeAgent` when steps compose; use `ToolCallingAgent` when each step is one API call and you want no code execution in the loop at all.

```python
from smolagents import CodeAgent, InferenceClientModel, WebSearchTool

agent = CodeAgent(
    tools=[WebSearchTool()],
    model=InferenceClientModel(),          # defaults to Qwen/Qwen3-Next-80B-A3B-Thinking
    additional_authorized_imports=["pandas"],
    max_steps=20,                          # default
    planning_interval=3,                   # re-plan every 3 steps; omit to disable planning
)
result = agent.run("...", additional_args={"df": df})   # additional_args land in the exec namespace
```

## Model backends

All take `model_id` plus arbitrary completion kwargs (`temperature`, `max_tokens`, …) forwarded to the provider. `REMOVE_PARAMETER` as a value strips a parameter the library would otherwise send.

| Class | Backend | Auth | Notes |
|---|---|---|---|
| `InferenceClientModel` | HF Inference Providers | `HF_TOKEN` env or `token=` | `provider="together"` etc. to pin a provider. |
| `LiteLLMModel` | 100+ providers via LiteLLM | provider env var or `api_key=` | Also the Ollama path: `model_id="ollama_chat/…"`, `api_base=`, and **set `num_ctx=8192`** — Ollama's 2048 default fails agent loops. |
| `OpenAIModel` | any OpenAI-compatible endpoint | `api_key=`, `api_base=` | Use for vLLM/LM Studio/OpenRouter servers. |
| `TransformersModel` | local `transformers` | none | `device_map=`, `torch_dtype=`, `max_new_tokens=4096`. `VLLMModel` / `MLXModel` are the local vLLM and Apple-MLX equivalents. |
| `AzureOpenAIModel` / `AmazonBedrockModel` | Azure / Bedrock | service env vars | Bedrock accepts a preconfigured boto3 `client=`. |

## Tools

Two forms. `@tool` for a plain function; subclass `Tool` when setup is expensive (`setup()` runs lazily on first call, not at init).

```python
from smolagents import tool, Tool

@tool
def most_downloaded(task: str) -> str:      # return type hint is MANDATORY
    """Return the most-downloaded Hub model for a task.

    Args:
        task: pipeline tag, e.g. "text-classification".
    """                                      # every arg needs an Args: line
    ...

class ModelDownloadTool(Tool):
    name = "model_download_tool"             # must be a valid Python identifier
    description = "..."                      # baked into the system prompt — write it for the LLM
    inputs = {"task": {"type": "string", "description": "..."}}
    output_type = "string"
    def forward(self, task: str) -> str: ...
```

Validation runs at **instantiation**, not class definition, so a broken `Tool` subclass fails at `ModelDownloadTool()`. Loading external tools: `Tool.from_hub(..., trust_remote_code=True)` and `ToolCollection.from_mcp({"url": ..., "transport": "streamable-http"}, trust_remote_code=True)` — both execute code they fetch; treat `trust_remote_code=True` as running an untrusted package.

Tool quality dominates agent quality. Put the argument format in the description (`'%m/%d/%y %H:%M:%S'`, not "a date"), `print()` diagnostics inside `forward`, and raise errors that say how to fix the call — the traceback goes into the agent's memory and is what it self-corrects from. Merging two tools that are always called together removes an LLM round trip and a failure point.

## Sandboxing — the part that matters

`CodeAgent` runs LLM-generated Python. `LocalPythonExecutor` (the default) is an AST interpreter, **not a sandbox** — its own docstring says so: *"It is not a security sandbox: for isolated execution of untrusted code, use a remote executor."* What it does block, verified:

| Attempt | Result |
|---|---|
| `import os` | `InterpreterError: Import of os is not allowed. Authorized imports are: [...]` |
| `random._os.system(...)` | `InterpreterError: Forbidden access to module: os` — submodule escapes are checked too |
| `open(...)`, `eval(...)`, `__import__(...)` | `InterpreterError: Forbidden function evaluation` |
| `while True: pass` | capped at 1,000,000 while-iterations / 10,000,000 ops / 30s wall clock |

Default allowlist is 11 stdlib modules: `collections datetime itertools math queue random re stat statistics time unicodedata`. Submodules are **not** implied — authorize `numpy.random` explicitly, or `numpy.*` for the whole subtree. What it does **not** stop: resource exhaustion through an import you allowed (Pillow writing a million images), or a novel escape. Anything reachable from the process — env vars, `~/.aws`, the network, the repo you are standing in — is in blast radius.

| `executor_type=` | Isolation | Cost | Choose when |
|---|---|---|---|
| `"local"` (default) | none — same process, same filesystem | free | Trusted model, trusted inputs, no untrusted text entering the loop. |
| `"docker"` | container | local daemon | You want real isolation without a vendor account. Set `mem_limit`, `pids_limit`, `cap_drop=["ALL"]`, `security_opt=["no-new-privileges"]`, run as `nobody`. |
| `"e2b"` | remote microVM | `E2B_API_KEY`, per-use | Untrusted input, no local daemon. |
| `"modal"` | remote sandbox | Modal account | Already on Modal. |
| `"blaxel"` | remote microVM, <25ms warm start | `BL_API_KEY`, `BL_WORKSPACE` | Latency-sensitive, many short runs. |

The moment the agent reads the open web, an issue tracker, or user-supplied documents, prompt injection is a live path to code execution — move off `"local"`.

```python
with CodeAgent(model=InferenceClientModel(), tools=[], executor_type="e2b") as agent:
    agent.run("...")      # the context manager (or agent.cleanup()) tears the sandbox down
```

**Remote executors only sandbox the code snippets**, not the agent. Secrets are deliberately not shipped to the sandbox, which is why `executor_type != "local"` + `managed_agents` raises `Exception: Managed agents are not yet supported with remote code execution.` To isolate a multi-agent system, run the whole program inside the sandbox instead and pass `HF_TOKEN` in as an env var.

## Multi-agent

A managed agent is any agent with `name` and `description` — the manager sees it as a tool.

```python
web_agent = CodeAgent(tools=[WebSearchTool()], model=model,
                      name="web_search_agent",
                      description="Runs web searches. Give it your query as an argument.")
manager = CodeAgent(tools=[], model=model, managed_agents=[web_agent])
```

`name` must be a valid Python identifier, and names must be unique across tools *and* managed agents. Missing either attribute raises `AssertionError: All managed agents need both a name and a description!`. Set `provide_run_summary=True` on the child to return its reasoning, not just its answer. Separate memories are the point — keep scraped page content out of the manager's context.

## Memory, steps, control

`agent.memory.steps` is a list of `TaskStep | ActionStep | PlanningStep`; `ActionStep` carries `model_output`, `code_action`, `observations`, `observations_images`, `error`.

| Need | Do |
|---|---|
| Replay a finished run | `agent.replay(detailed=False)` |
| Steps as dicts | `agent.memory.get_succinct_steps()` / `get_full_steps()` |
| All code the agent wrote | `agent.memory.return_full_code()` |
| Continue a conversation | `agent.run(task, reset=False)` |
| Mutate memory each step (e.g. drop old screenshots) | `step_callbacks=[fn]`, `fn(memory_step, agent)` |
| Drive one step at a time | append a `TaskStep`, loop `agent.step(ActionStep(step_number=n))` |
| Full run metadata | `return_full_result=True` → `RunResult(output, state, steps, token_usage, timing)` |
| Reject bad answers | `final_answer_checks=[fn]` — returning `False` logs and continues the run |
| Stop mid-run | `agent.interrupt()` (stops after the current step) |
| Trace to OTel | `SmolagentsInstrumentor().instrument()` from `smolagents[telemetry]` |

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `ImportError: cannot import name 'HfApiModel'` | Following pre-1.10 material | `InferenceClientModel` |
| `InterpreterError: Non-installed authorized modules: numpy` at agent construction | `additional_authorized_imports` names a package absent from the host env — it is an allowlist, not an installer | `pip install` it, or drop it from the list |
| `InterpreterError: Import of X is not allowed` mid-run | Not in the allowlist | Add `X` (and `X.sub` or `X.*` for submodules). `"*"` allows everything and logs a caution — that is the whole sandbox gone |
| `TypeHintParsingException: Tool return type not found` | `@tool` function has no return annotation | Add `-> str` |
| `DocstringParsingException: ... no description for the argument 'x'` | Missing `Args:` entry | Document every parameter |
| `TypeError: You must set an attribute output_type` | `Tool` subclass missing a class attribute; surfaces at instantiation | Set `name`, `description`, `inputs`, `output_type` |
| `OSError: could not get source code` on `@tool` | `@tool` calls `inspect.getsource` to serialize the tool, which fails in a REPL or `python -c` | Define tools in a real `.py` file when testing |
| `ModuleNotFoundError: Please install 'openai' extra ...` | Model class needs its extra | `pip install 'smolagents[openai]'` — same shape for litellm/transformers/e2b/docker/mcp |
| `Exception: Invalid Tool name 'my-tool'` | Hyphen / keyword | Use an identifier: `my_tool` |
| Agent never emits a parseable action | Model writes ```` ```python ```` but the default action tags are `<code>…</code>` | `code_block_tags="markdown"`, or use a stronger model |
| Ollama agent loops or truncates constantly | 2048-token default context | `num_ctx=8192` or higher on `LiteLLMModel` |
| `ValueError: 'stream_outputs' is set to True, but the model class implements no 'generate_stream'` | Backend cannot stream | Drop `stream_outputs=True` |
| Agent stops at `max_steps_error` | 20-step default | Raise `max_steps`, or simplify: fewer, fatter tools and a `planning_interval` |

## Scope boundaries

| Task | Skill |
|---|---|
| Scripting the Hub REST API / building reusable Hub CLI tools | `huggingface-tool-builder` |
| `hf` CLI — auth, repos, download, jobs, endpoints | `hf-cli` |
| Fine-tuning with TRL, on Jobs or locally | `huggingface-llm-trainer`, `trl-training` |
| Running GGUF/llama.cpp locally, quant selection | `huggingface-local-models` |
| ML in the browser / Node | `transformers-js` |
| Agent framework not yet chosen, or TypeScript | `build-agents` / `eve` |
| Pydantic AI, LangChain, LangGraph, Deep Agents | those packs |

This skill does not claim generic "build me an agent" requests — it fires on smolagents specifically.

## References

- `https://huggingface.co/docs/smolagents/` + `guided_tour` · `tutorials/secure_code_execution` · `tutorials/building_good_agents` · `tutorials/tools` · `tutorials/memory` · `tutorials/inspect_runs` · `examples/multiagents` · `reference/{agents,models,tools,python_executors}`
- Source of truth for every claim above — https://github.com/huggingface/smolagents: `src/smolagents/{agents,models,tools,local_python_executor,remote_executors}.py` and `docs/source/en/`
