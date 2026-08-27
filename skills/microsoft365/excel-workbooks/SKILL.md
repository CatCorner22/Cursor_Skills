---
name: excel-workbooks
disable-model-invocation: true
description: "Build and debug Microsoft Excel workbooks: formulas, references, tables, charts, conditional formatting, basic pivot tables, and data validation. Use when working in Excel (.xlsx), spreadsheet homework, budgets, or lab data tables. Scope boundary: interpreting results in prose → `academic-writing`; Python/R analysis → `coding-ecosystem-primer`; Google Sheets → not this pack."
metadata:
  priority: 7
  pathPatterns:
    - '**/*.xlsx'
    - '**/*.xls'
    - '**/*.csv'
  promptSignals:
    phrases:
      - "excel formula"
      - "spreadsheet"
      - "pivot table"
      - "excel chart"
      - "vlookup"
      - "microsoft excel"
    allOf:
      - [excel, formula]
      - [spreadsheet, chart]
    anyOf:
      - "Microsoft Excel"
      - ".xlsx"
      - "XLOOKUP"
    minScore: 6
---
# Excel workbooks

**Rule:** One **row = one observation**; one **column = one variable**. Put raw data on one sheet; analysis on another; never merge cells in data ranges.

## Formula literacy

| Need | Function | Notes |
|---|---|---|
| Sum by condition | `SUMIFS`, `COUNTIFS` | Prefer over nested IF |
| Lookup | `XLOOKUP` (modern) or `INDEX/MATCH` | Lock ranges with `$` |
| Average / median | `AVERAGE`, `MEDIAN` | Watch blanks vs zeros |
| Text combine | `TEXTJOIN` | Delimiter control |
| Date math | `DATEDIF`, date − date | Store dates as dates, not text |
| If error | `IFERROR(expr, "")` | Don't hide real errors in homework |

**Absolute reference:** `$A$1` stays fixed when copying; `A1` moves.

## Excel Tables (Ctrl+T)

- Converts range to structured table → auto-fill formulas, filter buttons
- Table names enable readable formulas: `=SUM(Table1[Score])`
- New rows auto-extend formulas

## Charts for coursework

1. Select **labels + values** only (no blank rows)
2. Insert → recommended chart type:
   - **Bar/column:** compare categories
   - **Line:** time series
   - **Scatter:** relationship between two numeric variables
3. Chart title + axis labels with units
4. Remove chartjunk (3D, excessive gridlines)
5. Interpret in caption → **`academic-writing`** (name the claim; cite the sheet/range)

## Pivot tables (intro)

```
Insert → PivotTable → select clean table
Rows: category field | Values: numeric field (Sum/Average/Count)
Refresh after data changes: PivotTable Analyze → Refresh
```

## Conditional formatting

- Highlight duplicates, top/bottom N, color scales for heatmaps
- Don't use as substitute for analysis — label what rule means

## Data validation

- Restrict cell to list, number range, or date — useful for lab entry forms
- Data → Data Validation

## Common mistakes

| Mistake | Fix |
|---|---|
| Numbers stored as text | Text to Columns or `VALUE()` |
| VLOOKUP wrong column | Use XLOOKUP or verify col index |
| Chart shows wrong scale | Right-click axis → Format → bounds |
| CSV locale issues | Data → From Text/CSV; set delimiter |

## Copilot in Excel prompts

- "Create a pivot table summarizing sales by region and month"
- "Write an XLOOKUP to match student ID to grade from the roster sheet"
- "Suggest a chart type for this time-series temperature data"

## Boundaries

- Power Query / DAX / Power Pivot → advanced; mention only if user asks
- Macro/VBA → out of scope unless explicit
