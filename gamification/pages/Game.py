import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Data Engineering: The Game",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ORANGE = "#ff6b35"
GREEN = "#00d4aa"
PURPLE = "#7c6aef"
PINK = "#ff4777"
YELLOW = "#ffb800"
BLUE = "#4a9eff"
DIM = "#7a7a94"
BG = "rgba(0,0,0,0)"

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&display=swap');

h1, h2, h3 { font-family: 'JetBrains Mono', monospace !important; }

.score-box {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.score-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.2rem;
    font-weight: 800;
    color: #ff6b35;
    line-height: 1;
}
.score-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #7a7a94;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}
.stat-reveal {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    padding: 16px;
}
.stat-correct { color: #00d4aa; }
.stat-wrong { color: #ff4777; }

.category-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #7a7a94;
    letter-spacing: 1px;
    text-transform: uppercase;
    background: #1a1a2e;
    padding: 4px 10px;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 8px;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/expanded.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df


@st.cache_data
def get_base():
    return load_data().drop_duplicates("id")


df = load_data()
base = get_base()
TOTAL = base["id"].nunique()


# ============================================================
# CHART BUILDER
# ============================================================
def reveal_bar_chart(labels, values, highlight_label=None, highlight_label_2=None, title="", suffix="%"):
    """Bar chart that highlights specific bars for the reveal."""
    colors = []
    for label in labels:
        if label == highlight_label:
            colors.append(ORANGE)
        elif label == highlight_label_2:
            colors.append(GREEN)
        else:
            colors.append("#2a2a4a")

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v}{suffix}" for v in values],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=12),
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(family="JetBrains Mono", size=13)),
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(family="JetBrains Mono", size=11, color="#e8e6e3"),
        margin=dict(l=10, r=60, t=35, b=10),
        height=max(220, len(labels) * 38),
        xaxis=dict(visible=False),
        yaxis=dict(autorange="reversed", categoryorder="total ascending"),
        showlegend=False,
    )
    return fig


# ============================================================
# QUESTION BANK
# ============================================================
@st.cache_data
def build_hl_questions():
    """Build all Higher/Lower questions with chart data embedded."""
    questions = []

    def add_comparison(stats_dict, context, category, chart_title):
        """From a dict of {label: pct}, generate question pairs."""
        items = list(stats_dict.items())
        pairs = [(a, b) for a, b in [(items[i], items[j])
                  for i in range(len(items)) for j in range(len(items)) if i != j]]
        for (anchor_label, anchor_val), (compare_label, compare_val) in pairs:
            questions.append({
                "anchor_label": anchor_label,
                "anchor_value": anchor_val,
                "compare_label": compare_label,
                "compare_value": compare_val,
                "context": context,
                "category": category,
                "chart_labels": list(stats_dict.keys()),
                "chart_values": list(stats_dict.values()),
                "chart_title": chart_title,
            })

    # 1. Bottleneck by role

    # 2. Fire-fighting by industry
    stats = {}
    for ind in sorted(base["industry"].unique()):
        r = base[base["industry"] == ind]
        stats[ind] = round(r["fights_fires"].mean() * 100, 1)
    add_comparison(stats, "teams report **fighting fires**", "Fires × Industry",
                  "Fire-fighting rate by Industry")

    # 3. Ad-hoc modeling by industry
    stats = {}
    for ind in sorted(base["industry"].unique()):
        r = base[base["industry"] == ind]
        stats[ind] = round((r["modeling_clean"] == "Ad-hoc").mean() * 100, 1)
    add_comparison(stats, "use **ad-hoc modeling**", "Modeling × Industry",
                  "Ad-hoc modeling by Industry")

    # 4. Growth by bottleneck
    stats = {}
    for bn in ["Legacy / tech debt", "Lack of leadership", "Talent / hiring", "Data quality", "Poor requirements"]:
        r = base[base["bottleneck_clean"] == bn]
        stats[bn] = round((r["team_growth_2026"] == "Grow").mean() * 100, 1)
    add_comparison(stats, "expect their team to **grow** in 2026", "Growth × Bottleneck",
                  "% expecting growth, by bottleneck")

    # 5. No orchestration by org size
    stats = {}
    for size in ["< 50 employees", "50–199", "200–999", "1,000–10,000", "10,000+"]:
        r = base[base["org_size"] == size]
        stats[size] = round((r["orchestration_clean"] == "No orchestration / ad-hoc").mean() * 100, 1)
    add_comparison(stats, "have **no orchestration**", "Orchestration × Org Size",
                  "No orchestration rate by Org Size")

    # 6. Management self-awareness
    stats = {}
    for m in ["Management", "Non-Management"]:
        r = base[base["management_vs_non"] == m]
        stats[m] = round((r["bottleneck_clean"] == "Lack of leadership").mean() * 100, 1)
    add_comparison(stats, 'cite **"Lack of leadership"** as bottleneck',
                  "Self-awareness", "Leadership bottleneck: Mgmt vs IC")

    # 8. AI daily usage by industry
    stats = {}
    for ind in sorted(base["industry"].unique()):
        r = base[base["industry"] == ind]
        stats[ind] = round(r["ai_usage_frequency"].isin(["Multiple times per day", "Daily"]).mean() * 100, 1)
    add_comparison(stats, "use AI tools **daily or more**", "AI Usage × Industry",
                  "Daily+ AI usage by Industry")


    # 10. Fire-fighting by org size
    stats = {}
    for size in ["< 50 employees", "50–199", "200–999", "1,000–10,000", "10,000+"]:
        r = base[base["org_size"] == size]
        stats[size] = round(r["fights_fires"].mean() * 100, 1)
    add_comparison(stats, "teams report **fighting fires**", "Fires × Org Size",
                  "Fire-fighting rate by Org Size")

    return questions


@st.cache_data
def build_guess_questions():
    """Build Guess the Number questions with chart data."""
    questions = []

    # Helper to build a distribution dict
    def dist(col, val, group_col):
        stats = {}
        for g in sorted(base[group_col].unique()):
            r = base[base[group_col] == g]
            stats[g] = round((r[col] == val).mean() * 100, 1)
        return stats

    questions.append({
        "question": "What % of data professionals use AI tools **daily or more**?",
        "answer": round(base["ai_usage_frequency"].isin(["Multiple times per day", "Daily"]).mean() * 100, 1),
        "hint": "Think about ChatGPT, Copilot, Claude adoption...",
        "reveal": "AI is table stakes. Only 1% never use AI tools at all.",
        "category": "AI Adoption",
        "chart_labels": ["Multiple times/day", "Daily", "Weekly", "Rarely", "Never"],
        "chart_values": [
            round((base["ai_usage_frequency"] == f).mean() * 100, 1)
            for f in ["Multiple times per day", "Daily", "Weekly", "Rarely", "Never"]
        ],
        "chart_title": "AI Usage Frequency (all respondents)",
        "highlight": None,
    })

    questions.append({
        "question": "What % of respondents report **fighting fires** as a primary focus for the team?",
        "answer": round(base["fights_fires"].mean() * 100, 1),
        "hint": "More than 1 in 5, but less than 1 in 2...",
        "reveal": "Over a quarter of data teams spend significant time firefighting.",
        "category": "Team Focus",
        "chart_labels": list(dist("fights_fires", True, "industry").keys()),
        "chart_values": list(dist("fights_fires", True, "industry").values()),
        "chart_title": "Fire-fighting rate by Industry",
        "highlight": None,
    })

    questions.append({
        "question": "What % cite **legacy / tech debt** as their #1 bottleneck?",
        "answer": round((base["bottleneck_clean"] == "Legacy / tech debt").mean() * 100, 1),
        "hint": "It's the single biggest bottleneck in the survey.",
        "reveal": "The #1 bottleneck, beating leadership and requirements.",
        "category": "Challenges",
        "chart_labels": list(base["bottleneck_clean"].value_counts().head(7).index),
        "chart_values": [round(v / TOTAL * 100, 1) for v in base["bottleneck_clean"].value_counts().head(7).values],
        "chart_title": "Top bottlenecks (all respondents)",
        "highlight": "Legacy / tech debt",
    })

    questions.append({
        "question": "What % of **10,000+ employee** orgs have **no orchestration**?",
        "answer": round((base[base["org_size"] == "10,000+"]["orchestration_clean"] == "No orchestration / ad-hoc").mean() * 100, 1),
        "hint": "Surprisingly close to startup rates...",
        "reveal": "Enterprise ≠ mature infrastructure. Nearly identical to startups.",
        "category": "Infrastructure",
        "chart_labels": ["< 50 emp", "50–199", "200–999", "1K–10K", "10,000+"],
        "chart_values": [
            round((base[base["org_size"] == s]["orchestration_clean"] == "No orchestration / ad-hoc").mean() * 100, 1)
            for s in ["< 50 employees", "50–199", "200–999", "1,000–10,000", "10,000+"]
        ],
        "chart_title": "No orchestration rate by Org Size",
        "highlight": "10,000+",
    })

    questions.append({
        "question": "What % of **Healthcare** orgs use **ad-hoc modeling**?",
        "answer": round((base[base["industry"] == "Healthcare"]["modeling_clean"] == "Ad-hoc").mean() * 100, 1),
        "hint": "The most regulated industries aren't always the most disciplined...",
        "reveal": "The most regulated industry has the messiest modeling.",
        "category": "Modeling",
        "chart_labels": list(dist("modeling_clean", "Ad-hoc", "industry").keys()),
        "chart_values": list(dist("modeling_clean", "Ad-hoc", "industry").values()),
        "chart_title": "Ad-hoc modeling rate by Industry",
        "highlight": "Healthcare",
    })

    questions.append({
        "question": "What % say **modeling is going well** (no pain points)?",
        "answer": 11.3,
        "hint": "Joe Reis called modeling 'in crisis'...",
        "reveal": "Nearly 90% report at least one modeling pain point.",
        "category": "Modeling",
        "chart_labels": list(df.groupby("modeling_pain_points")["id"].nunique().sort_values(ascending=False).index),
        "chart_values": [round(v / TOTAL * 100, 1) for v in df.groupby("modeling_pain_points")["id"].nunique().sort_values(ascending=False).values],
        "chart_title": "Modeling pain points (multi-select)",
        "highlight": "None / modeling is going well",
    })

    questions.append({
        "question": "What % of **Manufacturing** teams report **fighting fires**?",
        "answer": round(base[base["industry"] == "Manufacturing / Industrial"]["fights_fires"].mean() * 100, 1),
        "hint": "Think factories, supply chains, legacy SCADA systems...",
        "reveal": "Manufacturing and Finance lead in firefighting, far above Tech.",
        "category": "Industry",
        "chart_labels": list(dist("fights_fires", True, "industry").keys()),
        "chart_values": list(dist("fights_fires", True, "industry").values()),
        "chart_title": "Fire-fighting rate by Industry",
        "highlight": "Manufacturing / Industrial",
    })

    questions.append({
        "question": "What % of teams with **Talent / hiring** as bottleneck expect to **grow**?",
        "answer": round((base[base["bottleneck_clean"] == "Talent / hiring"]["team_growth_2026"] == "Grow").mean() * 100, 1),
        "hint": "If your only problem is hiring, things might be going well...",
        "reveal": "The most bullish group. If talent is your only problem, the future is bright.",
        "category": "Growth",
        "chart_labels": list(dist("team_growth_2026", "Grow", "bottleneck_clean").keys()),
        "chart_values": list(dist("team_growth_2026", "Grow", "bottleneck_clean").values()),
        "chart_title": "% expecting growth, by bottleneck",
        "highlight": "Talent / hiring",
    })

    questions.append({
        "question": "What % of **Managers/VPs** cite **lack of leadership** as the bottleneck?",
        "answer": round((base[base["management_vs_non"] == "Management"]["bottleneck_clean"] == "Lack of leadership").mean() * 100, 1),
        "hint": "Do managers admit they're the problem?",
        "reveal": "The self-awareness gap is only ~3pp. Managers largely agree.",
        "category": "Self-awareness",
        "chart_labels": ["Management", "Non-Management"],
        "chart_values": [
            round((base[base["management_vs_non"] == m]["bottleneck_clean"] == "Lack of leadership").mean() * 100, 1)
            for m in ["Management", "Non-Management"]
        ],
        "chart_title": '"Lack of leadership" by Mgmt vs IC',
        "highlight": "Management",
    })

    questions.append({
        "question": "What % of teams building **AI platforms** expect to **shrink**?",
        "answer": round((base[base["ai_adoption"] == "Building internal AI platforms"]["team_growth_2026"] == "Shrink").mean() * 100, 1),
        "hint": "AI platforms might be replacing headcount...",
        "reveal": "Building AI platforms correlates with shrinkage, not growth. The transition costs headcount.",
        "category": "AI Paradox",
        "chart_labels": list(base["ai_adoption"].unique()),
        "chart_values": [
            round((base[base["ai_adoption"] == ai]["team_growth_2026"] == "Shrink").mean() * 100, 1)
            for ai in base["ai_adoption"].unique()
        ],
        "chart_title": "% expecting shrinkage by AI adoption",
        "highlight": "Building internal AI platforms",
    })

    return questions


# ============================================================
# SCORING
# ============================================================
def streak_emoji(s):
    if s >= 10: return "🔥🔥🔥"
    if s >= 7: return "🔥🔥"
    if s >= 5: return "🔥"
    if s >= 3: return "⚡"
    return ""


def points_for_guess(guess, actual):
    diff = abs(guess - actual)
    if diff <= 2: return 100
    if diff <= 5: return 75
    if diff <= 10: return 50
    if diff <= 20: return 25
    if diff <= 25: return 10
    return 0


# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "game_mode": None, "score": 0, "streak": 0, "best_streak": 0,
    "questions_answered": 0, "q_index": 0, "answered": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_game():
    for k, v in defaults.items():
        if k != "game_mode":
            st.session_state[k] = v
    st.session_state.best_streak = 0


# ============================================================
# MAIN MENU
# ============================================================
if st.session_state.game_mode is None:
    st.markdown("<h1 style='text-align:center; font-size: 2.5rem;'>🎮 Data Engineering:<br>The Game</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color: #7a7a94; font-style: italic; margin-bottom: 40px;'>"
        "How well do you know the 2026 data engineering landscape?<br>"
        "1,101 professionals answered. Can you predict what they said?</p>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### ⬆️⬇️ Higher or Lower")
        st.markdown("See a real stat. Guess if the next group is higher or lower. Build your streak.")
        if st.button("Play Higher/Lower", use_container_width=True, type="primary"):
            st.session_state.game_mode = "higher_lower"
            reset_game()
            st.rerun()

    with c2:
        st.markdown("### 🎯 Guess the Number")
        st.markdown("Use the slider to guess percentages. Precision = points. See the full picture on reveal.")
        if st.button("Play Guess the Number", use_container_width=True, type="primary"):
            st.session_state.game_mode = "guess"
            reset_game()
            st.rerun()

    st.markdown("---")
    st.caption("Data: 2026 Practical Data Community State of Data Engineering Survey by Joe Reis · 1,101 respondents")


# ============================================================
# HIGHER / LOWER
# ============================================================
elif st.session_state.game_mode == "higher_lower":
    all_qs = build_hl_questions()

    # Header
    c_back, c_title, c_score = st.columns([1, 3, 1])
    with c_back:
        if st.button("← Menu"):
            st.session_state.game_mode = None
            st.rerun()
    with c_title:
        st.markdown("## ⬆️⬇️ Higher or Lower")
    with c_score:
        se = streak_emoji(st.session_state.streak)
        st.markdown(
            f'<div class="score-box"><div class="score-number">{st.session_state.streak}</div>'
            f'<div class="score-label">streak {se}</div></div>',
            unsafe_allow_html=True,
        )

    # Pick question deterministically from index (with shuffle seed)
    if "hl_order" not in st.session_state:
        order = list(range(len(all_qs)))
        random.seed(42)
        random.shuffle(order)
        st.session_state.hl_order = order

    idx = st.session_state.hl_order[st.session_state.q_index % len(all_qs)]
    q = all_qs[idx]

    st.markdown(f'<span class="category-tag">{q["category"]}</span>', unsafe_allow_html=True)
    st.markdown(f"**{q['anchor_value']}%** of **{q['anchor_label']}** {q['context']}")
    st.markdown("---")
    st.markdown(f"### Is **{q['compare_label']}** higher or lower?")

    if not st.session_state.answered:
        c1, c2 = st.columns(2)
        with c1:
            higher = st.button("⬆️ HIGHER", use_container_width=True, type="primary")
        with c2:
            lower = st.button("⬇️ LOWER", use_container_width=True)

        if higher or lower:
            st.session_state.answered = True
            st.session_state.questions_answered += 1
            user_said_higher = higher

            actual_higher = q["compare_value"] >= q["anchor_value"]
            is_correct = user_said_higher == actual_higher

            st.session_state.last_correct = is_correct
            if is_correct:
                st.session_state.streak += 1
                st.session_state.score += 10 * min(st.session_state.streak, 5)
                st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
            else:
                st.session_state.streak = 0
            st.rerun()
    else:
        # --- REVEAL ---
        if st.session_state.last_correct:
            st.markdown(f'<div class="stat-reveal stat-correct">✅ {q["compare_value"]}%</div>', unsafe_allow_html=True)
            st.success(f"**{q['compare_label']}** = **{q['compare_value']}%** vs {q['anchor_label']} = {q['anchor_value']}%")
        else:
            st.markdown(f'<div class="stat-reveal stat-wrong">❌ {q["compare_value"]}%</div>', unsafe_allow_html=True)
            st.error(f"**{q['compare_label']}** = **{q['compare_value']}%** vs {q['anchor_label']} = {q['anchor_value']}%")

        # --- REVEAL CHART ---
        fig = reveal_bar_chart(
            q["chart_labels"], q["chart_values"],
            highlight_label=q["compare_label"],
            highlight_label_2=q["anchor_label"],
            title=q["chart_title"],
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"🟠 {q['compare_label']}  ·  🟢 {q['anchor_label']}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Score", st.session_state.score)
        c2.metric("Streak", f"{st.session_state.streak} {streak_emoji(st.session_state.streak)}")
        c3.metric("Best Streak", st.session_state.best_streak)

        if st.button("Next →", use_container_width=True, type="primary"):
            st.session_state.q_index += 1
            st.session_state.answered = False
            if "hl_order" in st.session_state and st.session_state.q_index >= len(st.session_state.hl_order):
                random.shuffle(st.session_state.hl_order)
                st.session_state.q_index = 0
            st.rerun()


# ============================================================
# GUESS THE NUMBER
# ============================================================
elif st.session_state.game_mode == "guess":
    all_qs = build_guess_questions()

    c_back, c_title, c_score = st.columns([1, 3, 1])
    with c_back:
        if st.button("← Menu"):
            st.session_state.game_mode = None
            st.rerun()
    with c_title:
        st.markdown("## 🎯 Guess the Number")
    with c_score:
        st.markdown(
            f'<div class="score-box"><div class="score-number">{st.session_state.score}</div>'
            f'<div class="score-label">points</div></div>',
            unsafe_allow_html=True,
        )

    idx = st.session_state.q_index % len(all_qs)
    q = all_qs[idx]

    st.markdown(f'<span class="category-tag">{q["category"]} · Question {st.session_state.questions_answered + 1} of {len(all_qs)}</span>', unsafe_allow_html=True)
    st.markdown(f"### {q['question']}")
    st.caption(f"💡 {q['hint']}")

    if not st.session_state.answered:
        guess = st.slider("Your guess (%)", 0, 100, 50, key=f"guess_{idx}")

        if st.button("🔒 Lock in answer", use_container_width=True, type="primary"):
            st.session_state.answered = True
            st.session_state.user_guess = guess
            st.session_state.questions_answered += 1
            pts = points_for_guess(guess, q["answer"])
            st.session_state.score += pts
            st.session_state.last_points = pts
            if pts >= 50:
                st.session_state.streak += 1
                st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
            else:
                st.session_state.streak = 0
            st.rerun()
    else:
        # --- REVEAL ---
        diff = abs(st.session_state.user_guess - q["answer"])
        pts = st.session_state.last_points

        if pts == 100: reaction, css = "🎯 BULLSEYE!", "stat-correct"
        elif pts >= 50: reaction, css = "👏 Nice!", "stat-correct"
        elif pts >= 10: reaction, css = "🤔 Close-ish...", "stat-wrong"
        else: reaction, css = "😅 Way off!", "stat-wrong"

        st.markdown(f'<div class="stat-reveal {css}">{q["answer"]}%</div>', unsafe_allow_html=True)
        st.markdown(
            f"<p style='text-align:center; font-size: 1.2rem;'>{reaction} "
            f"You guessed **{st.session_state.user_guess}%** (off by {diff:.1f}pp) → **+{pts} points**</p>",
            unsafe_allow_html=True,
        )
        st.info(f"📊 {q['reveal']}")

        # --- REVEAL CHART ---
        fig = reveal_bar_chart(
            q["chart_labels"], q["chart_values"],
            highlight_label=q.get("highlight"),
            title=q["chart_title"],
        )
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Score", st.session_state.score)
        c2.metric("This Round", f"+{pts}")
        c3.metric("Answered", f"{st.session_state.questions_answered}/{len(all_qs)}")

        if st.session_state.questions_answered >= len(all_qs):
            st.markdown("---")
            st.markdown(f"### 🏆 All questions answered! Final score: **{st.session_state.score}** / {len(all_qs) * 100}")
            avg = st.session_state.score / st.session_state.questions_answered
            if avg >= 75: grade = "🥇 Expert — you know this industry cold."
            elif avg >= 50: grade = "🥈 Solid — good industry intuition."
            elif avg >= 25: grade = "🥉 Decent — some blind spots to work on."
            else: grade = "📚 Time to read the survey report!"
            st.markdown(f"**{grade}**")

            if st.button("Play Again", use_container_width=True, type="primary"):
                reset_game()
                st.rerun()
        else:
            if st.button("Next →", use_container_width=True, type="primary"):
                st.session_state.q_index += 1
                st.session_state.answered = False
                st.rerun()


st.markdown("---")
if st.button("📊 Explore the data yourself", use_container_width=True):
    st.switch_page("pages/Explorer.py")