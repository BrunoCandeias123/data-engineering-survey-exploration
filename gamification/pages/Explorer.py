import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random

if st.button("🎮 Back to the game"):
    st.switch_page("pages/Game.py")



# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="2026 DE Survey Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ACCENT = "#ff6b35"
ACCENT2 = "#00d4aa"
ACCENT3 = "#7c6aef"
BG_CHART = "rgba(0,0,0,0)"

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/expanded.csv")
    # Drop the unnamed index column
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Clean architecture_trend into a usable dimension
    arch_map = {
        "Centralized warehouse": "Centralized warehouse",
        "Lakehouse": "Lakehouse",
        "Data mesh / federated ownership": "Data mesh / federated",
        "Event-driven architecture": "Event-driven",
    }
    df["architecture_clean"] = df["architecture_trend"].map(arch_map).fillna("Other")

    # Clean education_topic — bucket freetext into "Other"
    main_topics = [
        "AI/LLM integration", "Data modeling",
        "Semantics / ontologies / knowledge graphs",
        "Architecture patterns", "Streaming / event-driven systems",
        "Career growth / leadership", "Reliability engineering",
    ]
    df["education_clean"] = df["education_topic"].where(
        df["education_topic"].isin(main_topics), "Other"
    )

    return df


df = load_data()
TOTAL_RESPONDENTS = df["id"].nunique()


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def count_distinct(data, group_col, sort=True, top_n=None):
    """Count distinct respondents per group."""
    result = data.groupby(group_col)["id"].nunique().reset_index()
    result.columns = [group_col, "respondents"]
    result["pct"] = (result["respondents"] / data["id"].nunique() * 100).round(1)
    if sort:
        result = result.sort_values("respondents", ascending=False)
    if top_n:
        result = result.head(top_n)
    return result


def bar_chart(data, x_col, y_col="respondents", color=ACCENT, title="",
              orientation="h", height=400, show_pct=True, text_col=None):
    """Horizontal bar chart with consistent styling."""
    if text_col is None:
        text_col = "pct" if show_pct else y_col

    if orientation == "h":
        fig = px.bar(
            data, x=y_col, y=x_col, orientation="h",
            text=data[text_col].apply(lambda v: f"{v}%" if show_pct else str(v)),
            color_discrete_sequence=[color],
        )
        fig.update_yaxes(autorange="reversed")
    else:
        fig = px.bar(
            data, x=x_col, y=y_col, orientation="v",
            text=data[text_col].apply(lambda v: f"{v}%" if show_pct else str(v)),
            color_discrete_sequence=[color],
        )

    fig.update_layout(
        title=title,
        plot_bgcolor=BG_CHART,
        paper_bgcolor=BG_CHART,
        font=dict(family="JetBrains Mono, monospace", size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        xaxis_title="",
        yaxis_title="",
        showlegend=False,
    )
    fig.update_traces(textposition="outside")
    return fig


def comparison_chart(data, group_col, compare_col, title="", height=450):
    """Grouped bar chart comparing distributions across a compare dimension."""
    ct = data.groupby([compare_col, group_col])["id"].nunique().reset_index()
    ct.columns = [compare_col, group_col, "respondents"]
    totals = data.groupby(compare_col)["id"].nunique().reset_index()
    totals.columns = [compare_col, "total"]
    ct = ct.merge(totals, on=compare_col)
    ct["pct"] = (ct["respondents"] / ct["total"] * 100).round(1)

    fig = px.bar(
        ct, x=group_col, y="pct", color=compare_col,
        barmode="group", text="pct",
        color_discrete_sequence=[ACCENT, ACCENT2, ACCENT3, "#ff4777", "#ffb800"],
    )
    fig.update_layout(
        title=title,
        plot_bgcolor=BG_CHART,
        paper_bgcolor=BG_CHART,
        font=dict(family="JetBrains Mono, monospace", size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        height=height,
        xaxis_title="",
        yaxis_title="% of cohort",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_traces(textposition="outside", texttemplate="%{text}%")
    return fig


# ============================================================
# SIDEBAR FILTERS
# ============================================================
st.sidebar.title("🔍 Filters")

# Role filter
roles = sorted(df["role_clean"].unique())
selected_roles = st.sidebar.multiselect("Role", roles, default=roles)

# Org size filter
sizes = ["< 50 employees", "50–199", "200–999", "1,000–10,000", "10,000+"]
selected_sizes = st.sidebar.multiselect("Org Size", sizes, default=sizes)

# Industry filter
industries = sorted(df["industry"].unique())
selected_industries = st.sidebar.multiselect("Industry", industries, default=industries)

# Region filter
regions = sorted(df["region"].unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

# AI usage filter
ai_freqs = ["Multiple times per day", "Daily", "Weekly", "Rarely", "Never"]
selected_ai = st.sidebar.multiselect("AI Usage Frequency", ai_freqs, default=ai_freqs)

# Management filter
mgmt = sorted(df["management_vs_non"].unique())
selected_mgmt = st.sidebar.multiselect("Management vs Non", mgmt, default=mgmt)

# Apply filters
filtered = df[
    (df["role_clean"].isin(selected_roles)) &
    (df["org_size"].isin(selected_sizes)) &
    (df["industry"].isin(selected_industries)) &
    (df["region"].isin(selected_regions)) &
    (df["ai_usage_frequency"].isin(selected_ai)) &
    (df["management_vs_non"].isin(selected_mgmt))
]

n_filtered = filtered["id"].nunique()
st.sidebar.markdown("---")


# ============================================================
# HEADER
# ============================================================
st.title("2026 State of Data Engineering")
st.caption(f"Survey Explorer · {n_filtered:,} of {TOTAL_RESPONDENTS:,} respondents · All metrics use COUNT(DISTINCT id)")

# ============================================================
# TABS
# ============================================================
tab_overview, tab_infra, tab_ai, tab_modeling, tab_challenges, tab_cohorts, tab_crosstab = st.tabs([
    "📋 Overview", "🏗️ Infrastructure", "🤖 AI Adoption",
    "📐 Modeling", "🔥 Challenges", "🧬 Cohort Analysis", "📊 Crosstab"
])

# ============================================================
# TAB: OVERVIEW
# ============================================================
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)

    daily_ai = filtered[filtered["ai_usage_frequency"].isin(["Multiple times per day", "Daily"])]["id"].nunique()
    col1.metric("Daily AI Users", f"{daily_ai/n_filtered*100:.0f}%")

    legacy = filtered[filtered["bottleneck_clean"] == "Legacy / tech debt"]["id"].nunique()
    col2.metric("#1 Bottleneck: Legacy Debt", f"{legacy/n_filtered*100:.0f}%")

    grow = filtered[filtered["team_growth_2026"] == "Grow"]["id"].nunique()
    col3.metric("Expect Team Growth", f"{grow/n_filtered*100:.0f}%")

    fires = filtered[filtered["fights_fires"] == True]["id"].nunique()
    col4.metric("Fighting Fires", f"{fires/n_filtered*100:.0f}%")

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        role_data = count_distinct(filtered, "role_clean", top_n=10)
        st.plotly_chart(bar_chart(role_data, "role_clean", title="By Role (top 10)"),
                       use_container_width=True)
    with c2:
        ind_data = count_distinct(filtered, "industry")
        st.plotly_chart(bar_chart(ind_data, "industry", color=ACCENT2, title="By Industry"),
                       use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        size_data = count_distinct(filtered, "org_size")
        # Reorder
        size_order = ["< 50 employees", "50–199", "200–999", "1,000–10,000", "10,000+"]
        size_data["org_size"] = pd.Categorical(size_data["org_size"], categories=size_order, ordered=True)
        size_data = size_data.sort_values("org_size")
        st.plotly_chart(bar_chart(size_data, "org_size", color=ACCENT3, title="By Org Size"),
                       use_container_width=True)
    with c4:
        reg_data = count_distinct(filtered, "region")
        st.plotly_chart(bar_chart(reg_data, "region", color="#ff4777", title="By Region"),
                       use_container_width=True)

# ============================================================
# TAB: INFRASTRUCTURE
# ============================================================
with tab_infra:
    c1, c2 = st.columns(2)
    with c1:
        storage_data = count_distinct(filtered, "Category")
        st.plotly_chart(bar_chart(storage_data, "Category", title="Storage Category"),
                       use_container_width=True)
    with c2:
        arch_data = count_distinct(filtered, "architecture_clean")
        st.plotly_chart(bar_chart(arch_data, "architecture_clean", color=ACCENT2,
                                  title="Architecture Trend"),
                       use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        orch_data = count_distinct(filtered, "orchestration_clean", top_n=12)
        st.plotly_chart(bar_chart(orch_data, "orchestration_clean", color=ACCENT3,
                                  title="Orchestration (top 12)", height=500),
                       use_container_width=True)
    with c4:
        growth_data = count_distinct(filtered, "team_growth_2026")
        order = ["Grow", "Stay the same", "Shrink", "Not sure"]
        growth_data["team_growth_2026"] = pd.Categorical(
            growth_data["team_growth_2026"], categories=order, ordered=True
        )
        growth_data = growth_data.sort_values("team_growth_2026")
        st.plotly_chart(bar_chart(growth_data, "team_growth_2026", color="#ffb800",
                                  title="Team Growth 2026"),
                       use_container_width=True)

# ============================================================
# TAB: AI ADOPTION
# ============================================================
with tab_ai:
    c1, c2 = st.columns(2)
    with c1:
        freq_data = count_distinct(filtered, "ai_usage_frequency")
        freq_order = ["Multiple times per day", "Daily", "Weekly", "Rarely", "Never"]
        freq_data["ai_usage_frequency"] = pd.Categorical(
            freq_data["ai_usage_frequency"], categories=freq_order, ordered=True
        )
        freq_data = freq_data.sort_values("ai_usage_frequency")
        st.plotly_chart(bar_chart(freq_data, "ai_usage_frequency", title="AI Usage Frequency"),
                       use_container_width=True)
    with c2:
        adopt_data = count_distinct(filtered, "ai_adoption")
        st.plotly_chart(bar_chart(adopt_data, "ai_adoption", color=ACCENT2,
                                  title="Organizational AI Adoption"),
                       use_container_width=True)

    st.markdown("---")
    helps_data = count_distinct(filtered, "ai_helps_with")
    st.plotly_chart(bar_chart(helps_data, "ai_helps_with", color=ACCENT3,
                              title="What AI Helps With (multi-select, exploded)"),
                   use_container_width=True)

# ============================================================
# TAB: MODELING
# ============================================================
with tab_modeling:
    c1, c2 = st.columns(2)
    with c1:
        model_data = count_distinct(filtered, "modeling_clean")
        st.plotly_chart(bar_chart(model_data, "modeling_clean", title="Modeling Approach"),
                       use_container_width=True)
    with c2:
        pain_data = count_distinct(filtered, "modeling_pain_points")
        st.plotly_chart(bar_chart(pain_data, "modeling_pain_points", color="#ff4777",
                                  title="Modeling Pain Points (multi-select, exploded)"),
                       use_container_width=True)

    st.markdown("---")
    edu_data = count_distinct(filtered, "education_clean")
    st.plotly_chart(bar_chart(edu_data, "education_clean", color=ACCENT3,
                              title="Desired Training Topics"),
                   use_container_width=True)

# ============================================================
# TAB: CHALLENGES
# ============================================================
with tab_challenges:
    c1, c2 = st.columns(2)
    with c1:
        bottle_data = count_distinct(filtered, "bottleneck_clean")
        st.plotly_chart(bar_chart(bottle_data, "bottleneck_clean", title="Biggest Bottleneck"),
                       use_container_width=True)
    with c2:
        focus_data = count_distinct(filtered, "team_focus")
        st.plotly_chart(bar_chart(focus_data, "team_focus", color=ACCENT2,
                                  title="Team Focus (multi-select, exploded)"),
                       use_container_width=True)

    st.markdown("---")
    st.subheader("Bottleneck by Role")
    st.plotly_chart(
        comparison_chart(filtered, "bottleneck_clean", "role_clean",
                        title="Bottleneck distribution by Role (top roles)"),
        use_container_width=True,
    )

# ============================================================
# TAB: COHORT ANALYSIS
# ============================================================
with tab_cohorts:
    st.subheader("Pain Point Pair Cohorts")
    st.caption("Compare respondents who have a specific pain point pair vs. those who don't.")

    # Build cohort selector from the individual pairs (not the pipe-delimited combos)
    all_pairs = [
        "Lack of ownership + Move fast pressure",
        "Hard to maintain + Move fast pressure",
        "Hard to maintain + Lack of ownership",
        "Move fast pressure + Tools inadequate",
        "Lack of ownership + Tools inadequate",
        "Hard to maintain + Tools inadequate",
    ]
    selected_pair = st.selectbox("Select a pain point pair", all_pairs)

    # Since pain_point_pair is pipe-delimited, use str.contains with regex=False
    cohort_has = filtered[filtered["pain_point_pair"].str.contains(selected_pair, na=False, regex=False)]
    cohort_not = filtered[~filtered["pain_point_pair"].str.contains(selected_pair, na=False, regex=False)]

    n_has = cohort_has["id"].nunique()
    n_not = cohort_not["id"].nunique()

    c1, c2, c3 = st.columns(3)
    c1.metric("Has Pair", f"{n_has:,}", f"{n_has/n_filtered*100:.1f}%")
    c2.metric("Doesn't Have Pair", f"{n_not:,}", f"{n_not/n_filtered*100:.1f}%")
    c3.metric("Total Filtered", f"{n_filtered:,}")

    # Compare across a chosen dimension
    compare_dim = st.selectbox("Compare across", [
        "bottleneck_clean", "team_growth_2026", "ai_adoption",
        "modeling_clean", "architecture_clean", "org_size",
        "industry", "role_clean", "region",
    ])

    # Build comparison data
    has_dist = count_distinct(cohort_has, compare_dim)
    has_dist["cohort"] = f"Has: {selected_pair}"
    not_dist = count_distinct(cohort_not, compare_dim)
    not_dist["cohort"] = f"Doesn't have pair"

    combined = pd.concat([has_dist, not_dist])

    fig = px.bar(
        combined, x=compare_dim, y="pct", color="cohort",
        barmode="group", text="pct",
        color_discrete_sequence=[ACCENT, ACCENT2],
    )
    fig.update_layout(
        title=f"{compare_dim} — Cohort Comparison",
        plot_bgcolor=BG_CHART,
        paper_bgcolor=BG_CHART,
        font=dict(family="JetBrains Mono, monospace", size=12),
        margin=dict(l=10, r=10, t=40, b=10),
        height=500,
        xaxis_title="",
        yaxis_title="% of cohort",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_traces(textposition="outside", texttemplate="%{text}%")
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TAB: CROSSTAB
# ============================================================
with tab_crosstab:
    st.subheader("Custom Crosstab")
    st.caption("Cross-tabulate any two dimensions. Values = COUNT(DISTINCT id).")

    available_dims = [
        "role_clean", "org_size", "industry", "region",
        "ai_usage_frequency", "ai_adoption", "team_focus",
        "modeling_clean", "modeling_pain_points", "ai_helps_with",
        "architecture_clean", "bottleneck_clean", "orchestration_clean",
        "team_growth_2026", "education_clean", "management_vs_non",
        "Category", "fights_fires",
    ]

    c1, c2 = st.columns(2)
    row_dim = c1.selectbox("Rows", available_dims, index=0)
    col_dim = c2.selectbox("Columns", available_dims, index=3)

    show_as = st.radio("Show as", ["Column %", "Count"], horizontal=True)

    # Build crosstab using distinct IDs
    ct = filtered.groupby([row_dim, col_dim])["id"].nunique().reset_index()
    ct.columns = [row_dim, col_dim, "count"]
    pivot = ct.pivot_table(index=row_dim, columns=col_dim, values="count", fill_value=0)

    if show_as == "Row %":
        pivot = pivot.div(pivot.sum(axis=1), axis=0).multiply(100).round(1)
    elif show_as == "Column %":
        pivot = pivot.div(pivot.sum(axis=0), axis=1).multiply(100).round(1)

    st.dataframe(pivot, use_container_width=True, height=500)

    # Heatmap
    if st.checkbox("Show heatmap", value=True):
        fig = px.imshow(
            pivot.values,
            labels=dict(x=col_dim, y=row_dim, color=show_as),
            x=list(pivot.columns),
            y=list(pivot.index),
            color_continuous_scale="Oranges",
            aspect="auto",
        )
        fig.update_layout(
            height=max(400, len(pivot) * 35),
            font=dict(family="JetBrains Mono, monospace", size=11),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(
    "Data: 2026 Practical Data Community State of Data Engineering Survey (Joe Reis) · "
    "1,101 respondents · Dec 2025 – Jan 2026 · "
    "All metrics use COUNT(DISTINCT id) on the exploded dataset."
)
