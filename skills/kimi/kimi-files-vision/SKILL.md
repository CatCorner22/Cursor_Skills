---
name: kimi-files-vision
description: Kimi multimodal inputs — Files API extraction, image and video in chat, and multi-file question answering.
type: prompt
whenToUse: When uploading PDFs or documents for Q&A, sending images or video to Kimi vision models, or building file-grounded agents.
disableModelInvocation: false
---

# Kimi files and vision

## Files API → Q&A pattern

Flow:

1. **Upload** file: `POST /v1/files` (purpose such as `file-extract` per docs).
2. **Reference** file id in a chat message or fetch extracted content via `GET /v1/files/{file_id}/content`.
3. **Ask** in Chat Completions with file content in context or via platform file message shapes.

Guides:

- File Q&A: https://platform.kimi.ai/docs/guide/use-kimi-api-for-file-based-qa.md
- Upload: https://platform.kimi.ai/docs/api/files-upload.md
- Content: https://platform.kimi.ai/docs/api/files-content.md

**Multi-file:** Upload each file; include all extracts in one conversation with clear filenames/labels so the model can cite sources.

## Vision in chat (images and video)

Supported on Kimi K3.1 Pro and Kimi K3.

Guide: https://platform.kimi.ai/docs/guide/use-kimi-vision-model.md

Input options:

- Base64 image/video parts in message `content` array
- Public URL references where supported
- File upload pipeline for large media

**Practices:**

- Label each asset (“Figure 1: architecture diagram”).
- Ask one primary question per image when debugging vision failures.
- For long video, prefer excerpts or key frames if latency matters.

## Long context (1M)

Do not dump entire extracts blindly — use structure:

1. Table of contents or section headers in the system message
2. Relevant extract only when possible (pre-chunk in your app)
3. Token estimate before multi-hundred-page PDFs

Skill: `kimi-context-cost-batch`

## PDF-specific help

https://platform.kimi.ai/docs/guide/ask-questions-about-pdf-content.md

## Cleanup

Delete unused uploads: `DELETE /v1/files/{file_id}` to avoid clutter and policy issues.
