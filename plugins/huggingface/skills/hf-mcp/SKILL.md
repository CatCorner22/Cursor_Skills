---
name: hf-mcp
description: Use Hugging Face Hub via MCP server tools when the Huggingface-skills (or equivalent) MCP namespace is connected. Search models, datasets, Spaces, and papers; inspect repos; invoke Gradio Spaces. If MCP is disconnected, use the hf-cli skill instead.
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Hugging Face MCP Server

Connect AI assistants to the Hugging Face Hub. Setup: https://huggingface.co/settings/mcp

## Use Cases & Examples

### Find the Best Model for a Task

```
User: "Find the best model for code generation"

1. hub_repo_search(repo_type="model", query="code", sort="trendingScore", limit=10)
2. hub_repo_details(repo_ids=["top-result-id"], include_readme=true)
```

### Compare Models from Different Providers

```
User: "Compare Llama vs Qwen for text generation"

1. hub_repo_search(repo_type="model", query="meta-llama", sort="downloads", limit=5)
2. hub_repo_search(repo_type="model", query="Qwen", sort="downloads", limit=5)
3. hub_repo_details(repo_ids=["meta-llama/Llama-3.2-1B", "Qwen/Qwen3-8B"], include_readme=true)
```

### Find Training Datasets

```
User: "Find datasets for sentiment analysis in English"

1. hub_repo_search(repo_type="dataset", query="sentiment", sort="downloads")
2. hub_repo_details(repo_ids=["top-dataset-id"], repo_type="dataset", include_readme=true)
```

### Discover AI Tools (MCP Spaces)

```
User: "Find a tool that can remove image backgrounds"

1. hub_repo_search(repo_type="space", query="background removal") or dynamic_space(operation="discover")
2. dynamic_space(operation="view_parameters", space_name="result-space-id")
3. dynamic_space(operation="invoke", space_name="result-space-id", parameters="{...}")
```

### Generate Images

```
User: "Create an image of a robot reading a book"

1. dynamic_space(operation="discover")  # See available tasks
2. gr1_z_image_turbo_generate(prompt="a robot sitting in a library reading a book, warm lighting, detailed")
```

### Research a Topic

```
User: "What are the latest papers on RLHF?"

1. hub_repo_search(query="reinforcement learning from human feedback") or hf papers search via hf-cli
2. hub_repo_details(repo_ids=["paper-linked-model"], include_readme=true)  # If paper links to models
```

### Learn How to Use a Library

```
User: "How do I fine-tune with LoRA using PEFT?"

1. Fetch docs with curl/WebFetch on https://huggingface.co/docs/peft (hf_doc_search / hf_doc_fetch are not in the live MCP catalog)
2. Or use hf-cli / the huggingface-llm-trainer skill for Jobs training
```

### Run a Quick GPU Job

```
User: "Run this Python script on a GPU"

# hf_jobs is not in the live MCP catalog — use hf-cli:
hf jobs uv run --flavor t4-small -s HF_TOKEN=$HF_TOKEN python -c "import torch; print(torch.cuda.is_available())"
```

### Train a Model on Cloud GPU

```
User: "Run my training script on an A10G"

# Use hf-cli / huggingface-llm-trainer, not a nonexistent hf_jobs MCP tool:
hf jobs uv run --flavor a10g-small -s HF_TOKEN=$HF_TOKEN python train.py
```

### Check Job Status

```
User: "What's happening with my training job?"

# hf_jobs is not in the live MCP catalog — use hf-cli:
hf jobs ps
hf jobs inspect <job-id>
hf jobs logs <job-id>
```

### Explore What's Trending

```
User: "What models are trending right now?"

hub_repo_search(repo_type="model", query="*", sort="trendingScore", limit=20)
```

### Get Model Card Details

```
User: "Tell me about Mistral-7B"

hub_repo_details(repo_ids=["mistralai/Mistral-7B-v0.1"], include_readme=true)
```

### Find Quantized Models

```
User: "Find GGUF versions of Llama 3"

hub_repo_search(repo_type="model", query="Llama 3 GGUF", sort="downloads", limit=10)
```

### Use a Gradio Space as a Tool

```
User: "Transcribe this audio file"

1. hub_repo_search(repo_type="space", query="speech to text transcription") or dynamic_space(operation="discover")
2. dynamic_space(operation="view_parameters", space_name="openai/whisper")
3. dynamic_space(operation="invoke", space_name="openai/whisper", parameters="{\"audio\": \"...\"}")
```

### Schedule Recurring Jobs

```
User: "Run this data sync every day at midnight"

# Not an MCP tool — use hf-cli:
hf jobs scheduled uv run --flavor cpu-basic --schedule "0 0 * * *" python sync.py
```

## Tool Selection Guide

| Goal | Tool |
|------|------|
| Find models / datasets / Spaces | `hub_repo_search` with `repo_type` |
| Get repo README/details | `hub_repo_details` |
| Browse Hub files | `hf_fs` |
| Learn library usage | Fetch official docs (no `hf_doc_*` tools in this catalog) |
| Run code on GPU/CPU | `hf-cli` (`hf jobs …`) — not MCP |
| Use Gradio apps as tools | `dynamic_space` |
| Generate images | `gr1_z_image_turbo_generate` or `dynamic_space` |
| Check auth | `hf_whoami` |

If the Huggingface-skills MCP namespace is disconnected or a named tool is missing, use the `hf-cli` skill instead of inventing tool names.

## Tips

- Use `sort="trendingScore"` to find what's popular now
- Use `sort="downloads"` to find battle-tested options
- Discover MCP-capable Spaces with `dynamic_space(operation="discover")`, not a `mcp=true` search flag
- Use `include_readme=true` in `hub_repo_details` for full model/dataset documentation
- For jobs accessing private repos, pass `-s HF_TOKEN=$HF_TOKEN` on the `hf jobs` CLI
- Use `dynamic_space(operation="discover")` to see all available Space-based tasks
