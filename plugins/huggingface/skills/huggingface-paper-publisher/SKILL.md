---
name: huggingface-paper-publisher
description: Publish and manage research papers on Hugging Face Hub. Use to create markdown research-article drafts, check or GET-index a paper page, link arXiv IDs into model/dataset/Space READMEs, and generate citations. Claim authorship, POST-index, and paper search belong in the huggingface-papers skill.
compatibility: ChatGPT (web, desktop, mobile via plugins) and Codex (desktop, CLI, IDE).
metadata:
  host: chatgpt-codex
  ported_from: Cursor_Skills
---
# Overview

Tools for linking research papers to Hugging Face artifacts and drafting markdown articles. Indexing, authorship claims, and Hub paper search are implemented by Hub APIs documented in `huggingface-papers` — not by extra `paper_manager.py` subcommands.

## Integration with HF Ecosystem

- **Paper Pages**: discover papers at `https://huggingface.co/papers/{arxiv-id}`
- **arXiv Integration**: visiting or POST-indexing an arXiv ID creates/updates the page
- **Model/Dataset Linking**: connect papers through README links and YAML
- **Authorship Verification**: claim in the Hub UI or via `POST /api/settings/papers/claim` (`huggingface-papers`)
- **Research Article Template**: generate markdown drafts from bundled templates

# Version

1.0.0

# Dependencies

The included script uses PEP 723 inline dependencies. Prefer `uv run` over
manual environment setup.

- huggingface_hub>=0.26.0
- pyyaml>=6.0.3
- requests>=2.32.5
- python-dotenv>=1.2.1

# What `paper_manager.py` actually implements

| Command | Behavior |
|---|---|
| `index` | GET `https://huggingface.co/papers/{id}`. Reports exists / not indexed. Does **not** POST. |
| `check` | Same GET; returns JSON status |
| `link` | Downloads README, inserts arXiv link + optional citation, uploads (or opens a PR) |
| `create` | Writes a markdown article from `templates/{template}.md` |
| `info` | Fetches arXiv metadata |
| `citation` | Prints BibTeX / APA / MLA |
| `search` | Prints “coming soon” and a Hub search URL — do not treat as a working search |

**Not implemented** (do not invent these CLIs): `claim`, `check-authorship`, `list-my-papers`, `toggle-visibility`, `convert`, `validate`.

For claim / POST-index / paper JSON / daily papers, follow `huggingface-papers`.

# Usage Instructions

Scripts live in `scripts/` relative to this `SKILL.md`. `cd` there or pass the full path.

### Prerequisites

- Run scripts with `uv run`
- Set `HF_TOKEN` with write access for `link`

### Method 1: Check / GET-index a paper

```bash
uv run scripts/paper_manager.py check --arxiv-id "2301.12345"
uv run scripts/paper_manager.py index --arxiv-id "2301.12345"
```

`index` only GETs the paper URL. If the page is missing, visit `https://huggingface.co/papers/{arxiv-id}` or POST via `huggingface-papers`:

```bash
curl "https://huggingface.co/api/papers/index" \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"arxivId":"2301.12345"}'
```

### Method 2: Link paper to model / dataset / Space

```bash
uv run scripts/paper_manager.py link \
  --repo-id "username/model-name" \
  --repo-type "model" \
  --arxiv-id "2301.12345"
```

```bash
uv run scripts/paper_manager.py link \
  --repo-id "username/dataset-name" \
  --repo-type "dataset" \
  --arxiv-id "2301.12345"
```

```bash
uv run scripts/paper_manager.py link \
  --repo-id "username/model-name" \
  --repo-type "model" \
  --arxiv-ids "2301.12345,2302.67890,2303.11111"
```

```bash
uv run scripts/paper_manager.py link \
  --repo-id "username/model-name" \
  --repo-type "model" \
  --arxiv-id "2301.12345" \
  --citation "$(cat citation.txt)" \
  --create-pr
```

#### How Linking Works

When you add an arXiv paper link to a model or dataset README:

1. The Hub extracts the arXiv ID from the link
2. A tag `arxiv:<PAPER_ID>` is automatically added to the repository
3. Users can click the tag to view the Paper Page
4. The Paper Page shows all models/datasets citing this paper
5. Papers are discoverable through filters and search

### Method 3: Claim authorship (not in this script)

Use the Hub UI or the write API in `huggingface-papers`:

1. Open `https://huggingface.co/papers/{arxiv-id}`
2. Click your name in the author list → Claim authorship
3. Wait for verification

```bash
curl "https://huggingface.co/api/settings/papers/claim" \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"paperId":"2301.12345","claimAuthorId":"{AUTHOR_ENTRY_ID}","targetUserId":"{HF_USER_ID}"}'
```

Visibility (“show on profile”) is an account-settings toggle in the Hub UI, not a CLI in this skill.

### Method 4: Create a research-article draft

```bash
uv run scripts/paper_manager.py create \
  --template "standard" \
  --title "Your Paper Title" \
  --output "paper.md"
```

Available templates (files under `templates/`): `standard`, `modern`, `arxiv`, `ml-report`.

```bash
uv run scripts/paper_manager.py create \
  --template "modern" \
  --title "Fine-Tuning Large Language Models with LoRA" \
  --authors "Jane Doe, John Smith" \
  --abstract "$(cat abstract.txt)" \
  --output "paper.md"
```

There is no `convert` command. Edit the markdown; render HTML with your usual markdown toolchain or [tfrere/research-article-template](https://huggingface.co/spaces/tfrere/research-article-template).

### Paper Template Structure

```markdown
---
title: Your Paper Title
authors: Jane Doe, John Smith
affiliations: University X, Lab Y
date: 2025-01-15
arxiv: 2301.12345
tags: [machine-learning, nlp, fine-tuning]
---

# Abstract
Brief summary of the paper...

# 1. Introduction
Background and motivation...

# 2. Related Work
Previous research and context...

# 3. Methodology
Approach and implementation...

# 4. Experiments
Setup, datasets, and procedures...

# 5. Results
Findings and analysis...

# 6. Discussion
Interpretation and implications...

# 7. Conclusion
Summary and future work...

# References
```

### Commands Reference

```bash
uv run scripts/paper_manager.py index --arxiv-id "2301.12345"
uv run scripts/paper_manager.py check --arxiv-id "2301.12345"
uv run scripts/paper_manager.py info --arxiv-id "2301.12345" --format json
uv run scripts/paper_manager.py citation --arxiv-id "2301.12345" --format bibtex
```

```bash
uv run scripts/paper_manager.py link \
  --repo-id "username/repo-name" \
  --repo-type "model|dataset|space" \
  --arxiv-id "2301.12345" \
  [--citation "Full citation text"] \
  [--create-pr]
```

```bash
uv run scripts/paper_manager.py create \
  --template "standard|modern|arxiv|ml-report" \
  --title "Paper Title" \
  --output "filename.md" \
  [--authors "Author1, Author2"] \
  [--abstract "Abstract text"]
```

**Search:** do not run `paper_manager.py search`. Use `https://huggingface.co/papers?search=…` or the papers APIs in `huggingface-papers`.

### YAML Metadata Format

When linking papers to models or datasets, proper YAML frontmatter is required:

**Model Card Example:**

```yaml
---
language:
  - en
license: apache-2.0
tags:
  - text-generation
  - transformers
  - llm
library_name: transformers
---

# Model Name

This model is based on the approach described in [Our Paper](https://arxiv.org/abs/2301.12345).

## Citation

```bibtex
@article{doe2023paper,
  title={Your Paper Title},
  author={Doe, Jane and Smith, John},
  journal={arXiv preprint arXiv:2301.12345},
  year={2023}
}
```
```

**Dataset Card Example:**

```yaml
---
language:
  - en
license: cc-by-4.0
task_categories:
  - text-generation
  - question-answering
size_categories:
  - 10K<n<100K
---

# Dataset Name

Dataset introduced in [Our Paper](https://arxiv.org/abs/2301.12345).

For more details, see the [paper page](https://huggingface.co/papers/2301.12345).
```

The Hub automatically extracts arXiv IDs from these links and creates `arxiv:2301.12345` tags.

### Integration Examples

**Workflow 1: Publish new research**

```bash
uv run scripts/paper_manager.py create \
  --template "modern" \
  --title "Novel Fine-Tuning Approach" \
  --output "paper.md"
# Edit paper.md, submit to arXiv, then:
uv run scripts/paper_manager.py check --arxiv-id "2301.12345"
# POST-index if needed (huggingface-papers), then:
uv run scripts/paper_manager.py link \
  --repo-id "your-username/your-model" \
  --repo-type "model" \
  --arxiv-id "2301.12345"
# Claim authorship in the Hub UI or via huggingface-papers
```

**Workflow 2: Link an existing paper**

```bash
uv run scripts/paper_manager.py check --arxiv-id "2301.12345"
uv run scripts/paper_manager.py link \
  --repo-id "username/model-v1" --repo-type "model" --arxiv-id "2301.12345"
uv run scripts/paper_manager.py link \
  --repo-id "username/training-data" --repo-type "dataset" --arxiv-id "2301.12345"
uv run scripts/paper_manager.py link \
  --repo-id "username/demo-space" --repo-type "space" --arxiv-id "2301.12345"
```

**Workflow 3: Update a model card**

```bash
uv run scripts/paper_manager.py link \
  --repo-id "username/model-name" \
  --repo-type "model" \
  --arxiv-id "2301.12345" \
  --citation "Full citation for the paper"
```

The script adds YAML if missing, inserts the arXiv link, adds a citation block, and preserves existing content.

### Best Practices

1. **Paper indexing** — GET-check first; POST-index or visit the URL if 404. Include full citations on cards.
2. **Metadata** — YAML frontmatter, license, task tags on every card.
3. **Authorship** — claim only papers you authored; use the Hub UI / `huggingface-papers`.
4. **Repository linking** — link every related model, dataset, and Space; keep BibTeX in the README.
5. **Drafts** — use one template family per project; put code/data links in the article body.

### Advanced Usage

```bash
for arxiv_id in "2301.12345" "2302.67890" "2303.11111"; do
  uv run scripts/paper_manager.py link \
    --repo-id "username/model-name" \
    --repo-type "model" \
    --arxiv-id "$arxiv_id"
done
```

```bash
uv run scripts/paper_manager.py info --arxiv-id "2301.12345" --format json
uv run scripts/paper_manager.py citation --arxiv-id "2301.12345" --format bibtex
```

There is no `validate` command. After `link`, `hf download username/repo README.md` and inspect the card, or GET the paper page.

### Error Handling

- **Paper not found**: arXiv ID is wrong or the Hub page is not indexed yet — visit or POST-index
- **Permission denied**: `HF_TOKEN` lacks write access to the repository
- **Invalid YAML**: malformed README frontmatter
- **Rate limiting**: too many Hub/arXiv requests

### Troubleshooting

**Issue**: "Paper not found on Hugging Face"
- **Solution**: Visit `https://huggingface.co/papers/{arxiv-id}` or POST `/api/papers/index`

**Issue**: "arXiv tag not appearing"
- **Solution**: Ensure the README includes `https://arxiv.org/abs/{id}` or `https://huggingface.co/papers/{id}`

**Issue**: "Cannot link to repository"
- **Solution**: Verify `HF_TOKEN` has write permissions

**Issue**: "Template not found"
- **Solution**: Use `standard`, `modern`, `arxiv`, or `ml-report` and run from the skill directory

### Resources

- Paper Pages: [hf.co/papers](https://huggingface.co/papers)
- Model cards: [hf.co/docs/hub/model-cards](https://huggingface.co/docs/hub/en/model-cards)
- Dataset cards: [hf.co/docs/hub/datasets-cards](https://huggingface.co/docs/hub/en/datasets-cards)
- Research article template: [tfrere/research-article-template](https://huggingface.co/spaces/tfrere/research-article-template)
- Claim / POST-index APIs: `huggingface-papers` skill
