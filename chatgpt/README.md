# ChatGPT compatibility staging

This branch stages a ChatGPT-compatible adaptation of the existing skill library. The original `skills/` contents and Cursor configuration are unchanged.

The export workflow reads public source pinned to commit `6f3febcd0490107ad7b300743b385f3db3f1169c`, inventories the 189 skill definitions, and exports their supporting files for review. It does not execute repository scripts, install dependencies, read secrets, deploy anything, enable the separate Python runtime plugins, or install a ChatGPT plugin. The workflow has read-only repository permissions and short artifact retention.

A generated compatibility package must distinguish instruction adapters, original reference material, external tool dependencies, and actual installation status. ChatGPT account installation requires the supported product surface and must not be claimed from a repository export or a memory entry alone.
