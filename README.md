# 🎮 2026 Data Engineering Survey — Gamified Explorer

An interactive Streamlit app that turns the [2026 Practical Data Community State of Data Engineering Survey](https://joereis.github.io/practical_data_data_eng_survey/) into a game. Test your intuition about the data engineering landscape, then explore the raw data yourself.

Built for the 2026 State of Data Engineering Survey Hackathon.

## What is this?

1,101 data professionals answered questions about their tools, pain points, team dynamics, and AI adoption. Instead of reading static charts, this app lets you **play with the data** — guess industry statistics, discover surprising patterns, and then dive into self-serve analytics.

## App Structure

### 🎮 Game (landing page)

Two game modes that test how well you know the industry:

**⬆️⬇️ Higher or Lower** — See a real stat (e.g., "22.1% of Data Engineers cite lack of leadership as their bottleneck"). Guess whether the next group is higher or lower. Build streaks for bonus multipliers. After each answer, a bar chart reveals the full distribution with both groups highlighted.

Question categories include:
- Bottleneck × Role
- Fire-fighting × Industry
- Ad-hoc modeling × Industry
- Growth expectations × Bottleneck
- No orchestration × Org Size
- Kimball adoption × Architecture
- AI Usage × Industry
- Shrinkage × AI Adoption
- Management self-awareness

**🎯 Guess the Number** — Use a slider to guess exact percentages. Scored on precision: within 1pp = 100 points (Bullseye), within 3pp = 75, within 5pp = 50. Each reveal includes context and a chart showing where the answer sits relative to the full distribution. 11 curated questions covering AI adoption, firefighting rates, modeling pain, orchestration gaps, and more.

### 📊 Explorer (self-serve analytics)

A full interactive dashboard with 6 sidebar filters and 7 analysis tabs:

**Filters:** Role, Org Size, Industry, Region, AI Usage Frequency, Management vs Non-Management

**Tabs:**
- **Overview** — KPI cards (daily AI usage, #1 bottleneck, growth expectations, fire-fighting rate) + distributions by role, industry, org size, and region
- **Infrastructure** — Storage category, architecture trend, orchestration tools (top 12), team growth outlook
- **AI Adoption** — Usage frequency, organizational adoption level, what AI helps with
- **Modeling** — Modeling approach, pain points, desired training topics
- **Challenges** — Bottleneck distribution + bottleneck-by-role comparison chart
- **Cohort Analysis** — Select a pain point pair (e.g., "Lack of ownership + Move fast pressure") and compare that cohort vs. the rest across any dimension
- **Crosstab** — Cross-tabulate any two dimensions with row %, column %, or raw count view + heatmap

## Data Pipeline

```
survey_2026_data_engineering.csv          Raw survey (1,101 rows × 18 columns)
        │
        ├── Role normalization            82 freetext variants → 15 categories
        ├── Bottleneck normalization       63 freetext variants → 10 categories
        ├── Orchestration normalization    211 freetext variants → 26 categories
        ├── Modeling normalization         31 variants → 10 categories
        ├── Management vs Non flag         Derived from role_clean
        ├── Fights fires flag              Derived from team_focus
        ├── Pain point pairs               Combinatorial pairs from modeling_pain_points
        ├── Team focus pairs               Combinatorial pairs from team_focus
        ├── Num focuses / num pains        Counts per respondent
        │
        ├── Storage mapping merge          survey_platform_mapping.csv → 5 categories
        │
        └── Multi-select explosion         team_focus × modeling_pain_points × ai_helps_with
                │
                └── expanded.xlsx          Exploded dataset (11,385 rows × 32 columns)
```

### Multi-select handling

Three survey fields allow multiple selections: `team_focus`, `modeling_pain_points`, and `ai_helps_with`. These are exploded into individual rows, creating a cartesian product (~11K rows from 1,101 respondents). Every metric uses `COUNT(DISTINCT id)` to avoid double-counting.

### Cleaned dimensions

| Column | Source | Categories |
|--------|--------|-----------|
| `role_clean` | `role` (freetext) | 15 (Data Engineer, Analytics Engineer, Manager/Director/VP, ...) |
| `bottleneck_clean` | `biggest_bottleneck` (freetext) | 10 (Legacy/tech debt, Lack of leadership, Poor requirements, ...) |
| `orchestration_clean` | `orchestration` (freetext) | 26 (Airflow, Dagster, Databricks Workflows, ...) |
| `modeling_clean` | `modeling_approach` (freetext) | 10 (Kimball, Ad-hoc, Medallion, Data Vault, ...) |
| `Category` | `storage_environment` via mapping | 5 (Cloud Data Warehouse, Lake/Lakehouse, ...) |
| `management_vs_non` | Derived from `role_clean` | 2 (Management, Non-Management) |
| `fights_fires` | Derived from `team_focus` | Boolean |
| `pain_point_pair` | Combinations of `modeling_pain_points` | Pipe-delimited pairs |
| `team_focus_pair` | Combinations of `team_focus` | Pipe-delimited pairs |

## Project Structure

```
data-engineering-survey-exploration/
├── data/
│   ├── survey_2026_data_engineering.csv   # Raw survey responses (1,101 × 18)
│   ├── survey_platform_mapping.csv        # Storage environment → 5 categories
│   └── expanded.xlsx                      # Cleaned + exploded dataset (11,385 × 32)
├── gamification/
│   ├── Home.py                            # Entry point — redirects to Game
│   └── pages/
│       ├── Game.py                        # 🎮 Higher/Lower + Guess the Number
│       └── Explorer.py                    # 📊 Self-serve analytics dashboard
└── README.md
```

## Run online:
https://gamification-data-engineering-survey-exploration.streamlit.app/


## Run Locally

```bash
cd gamification
pip install streamlit pandas plotly openpyxl
streamlit run Home.py
```

The app opens at `http://localhost:8501`. Game is the landing page; click "📊 Explore the data yourself" at the bottom to switch to the Explorer.

## Key Findings Embedded in the Game

Some of the surprising patterns the game surfaces:

- **Manufacturing and Finance** lead in fire-fighting (33-34%) — far above Tech (22%)
- **10,000+ employee orgs** have 21.8% no-orchestration rate — nearly identical to startups
- **Healthcare** has 25.2% ad-hoc modeling — the most regulated industry, among the messiest modeling
- **Managers admit they're the problem** — 18.4% cite lack of leadership vs 22.3% of ICs (only ~3pp gap)
- **Teams building AI platforms** have the highest shrinkage expectation (11.3%) — the automation paradox
- **"Talent/hiring" bottleneck teams** are the most bullish on growth (57.7%) — if that's your only problem, things are going well

## Credits

- **Data:** [2026 Practical Data Community Survey](https://joereis.github.io/practical_data_data_eng_survey/) by Joe Reis
- **Inspiration:** [Joe Reis's interactive explorer](https://joereis.github.io/practical_data_data_eng_survey/) (DuckDB-WASM) and [AnttiRask's Shiny dashboard](https://github.com/AnttiRask/state-of-data-engineering-survey-explorer-but-boring) (R/Shiny on Cloud Run)
