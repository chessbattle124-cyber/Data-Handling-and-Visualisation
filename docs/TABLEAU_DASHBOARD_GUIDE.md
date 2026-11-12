# Tableau dashboard guide

The packaged workbook contains the main Tableau dashboard and the chatbot extension worksheet.

## Dashboard contents
1. **Average Score by Year** — line chart using Year and AVG(Score).
2. **Institution Score Comparison** — institution-level score comparison.
3. **Top 100 by State** — state aggregation filtered to numeric rank ≤ 100.
4. **Category Coverage** — distinct institution counts by category.
5. **NIRF AI Chatbot** — embedded Tableau extension panel.

## Filters to add / verify in Tableau Desktop
For each worksheet, place these dimensions on Filters:
- Year (2017–2025)
- Category
- State
- Institution
- Rank_Band

For a dashboard-wide filter, use the filter card menu → **Apply to Worksheets → All Using This Data Source**. The packaged workbook's CSV is under `Data/nirf_tableau.csv`.

## Suggested additional worksheets for full Annexure A coverage
- Rank history by institution (Year vs Rank_numeric; reverse the rank axis).
- Rank gain/loss table between selected start and end years.
- Score histogram and quartile percentage chart.
- Score standard deviation by year and category.
- State top-100 trend over time.
- Rank-band transition matrix.
- Rank volatility by institution.
- Top-10 vs remaining score comparison.

## Correct interpretation
- Rank 1 is best; lower rank numbers are better. Reverse the rank axis for trend charts.
- Rank comparisons must be category-specific.
- Use distinct Institution_ID counts rather than counting raw rows when reporting institution totals.
- Missing scores stay null; do not replace them with 0.
- Exclude `is_withdrawn = True` and non-numeric rank records from rank-movement calculations.
