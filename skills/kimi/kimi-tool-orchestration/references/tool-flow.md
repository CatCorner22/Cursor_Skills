# K3 large-inventory tool flow

```
Start
  tools = [search_tools, ...core]
  tool_choice = "required" (turn 1)
        |
        v
  Model calls search_tools
        |
        v
  Host searches registry -> inject system message with tools[]
        |
        v
  tool_choice = "auto"
        |
        v
  Model calls loaded tools -> host executes -> tool messages
        |
        v
  Repeat until no tool_calls (preserve reasoning_content each turn)
```

Cache tip: keep the initial system prompt and core tools stable across requests.
