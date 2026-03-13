import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dataset Profiler",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;700&display=swap');

/* Background & base */
.stApp { background: #0a0a0f; color: #e8e8f0; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Hide default Streamlit decorations */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Hero */
.hero { padding: 3rem 0 2rem 0; border-bottom: 1px solid #1e1e2e; margin-bottom: 2rem; }
.hero h1 { font-family: 'Space Mono', monospace; font-size: 2.8rem; font-weight: 700; color: #fff; margin: 0; }
.hero p  { color: #6b6b8a; font-size: 1.05rem; margin-top: 0.5rem; }

/* Metric cards */
.metric-card {
    background: #12121a;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.2rem 1.6rem;
    text-align: center;
}
.metric-card .label {
    font-size: 0.72rem;
    color: #6b6b8a;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: 'Space Mono', monospace;
    margin-bottom: 0.4rem;
}
.metric-card .value {
    font-size: 1.8rem;
    font-weight: 700;
    font-family: 'Space Mono', monospace;
    line-height: 1.1;
}

/* Section title */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #7c6af7;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 1rem;
    margin-top: 1.5rem;
}

/* Column cards */
.col-card {
    background: #12121a;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}
.col-card:hover { border-color: #7c6af7; }
.col-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
}
.col-name {
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 0.95rem;
    color: #e8e8f0;
}
.col-summary {
    font-size: 0.82rem;
    color: #6b6b8a;
    margin-top: 0.3rem;
}
.null-pct { font-size: 0.82rem; font-family: 'Space Mono', monospace; }

/* Type badges */
.type-num  { background: #1a1a3a; color: #7c6af7; padding: 2px 8px; border-radius: 20px; font-family: 'Space Mono', monospace; font-size: 0.72rem; }
.type-cat  { background: #1a2a1a; color: #6af7a7; padding: 2px 8px; border-radius: 20px; font-family: 'Space Mono', monospace; font-size: 0.72rem; }
.type-dat  { background: #2a1a1a; color: #f7a76a; padding: 2px 8px; border-radius: 20px; font-family: 'Space Mono', monospace; font-size: 0.72rem; }
.type-bool { background: #2a2a1a; color: #f7f76a; padding: 2px 8px; border-radius: 20px; font-family: 'Space Mono', monospace; font-size: 0.72rem; }

/* Suggestion / warn boxes */
.suggestion {
    background: #0f1a2a;
    border-left: 3px solid #7c6af7;
    padding: 0.8rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    color: #c0c0d8;
}
.warn-box {
    background: #1a150a;
    border-left: 3px solid #f7a76a;
    padding: 0.8rem 1rem;
    border-radius: 0 8px 8px 0;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    color: #c0b090;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #6b6b8a;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-state p { font-size: 1rem; margin: 0.2rem 0; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; border-bottom: 1px solid #1e1e2e; }
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border: none;
    color: #6b6b8a;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    padding: 0.6rem 1rem;
    border-radius: 8px 8px 0 0;
}
.stTabs [aria-selected="true"] { background: #1e1e2e; color: #7c6af7; }

/* Dataframe dark */
.stDataFrame { background: #12121a; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: #12121a;
    border: 2px dashed #1e1e2e;
    border-radius: 12px;
    padding: 1rem;
}
[data-testid="stFileUploader"]:hover { border-color: #7c6af7; }

/* Plotly chart containers */
[data-testid="stPlotlyChart"] { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY THEME DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#9090b0",
    colorway=["#7c6af7", "#6af7a7", "#f7a76a", "#f76a6a", "#6ad4f7"],
    margin=dict(l=10, r=10, t=30, b=10),
)

def apply_theme(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_xaxes(gridcolor="#1e1e2e", zeroline=False)
    fig.update_yaxes(gridcolor="#1e1e2e", zeroline=False)
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def classify_column(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "bool"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    return "categorical"


def detect_outliers_iqr(series: pd.Series) -> tuple:
    clean = series.dropna()
    if len(clean) == 0:
        return 0, 0
    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    n_outliers = int(((clean < lower) | (clean > upper)).sum())
    return n_outliers, len(clean)


def suggest_features(col_name: str, series: pd.Series, col_type: str) -> list:
    suggestions = []

    if col_type == "numeric":
        clean = series.dropna()
        if len(clean) < 2:
            return suggestions
        skew = float(clean.skew())
        nuniq = int(clean.nunique())
        n_out, n_tot = detect_outliers_iqr(series)
        nulls = int(series.isna().sum())

        if abs(skew) > 1:
            suggestions.append(f"💡 Skewness={skew:.2f} → try log1p or Box-Cox transform")
        if n_tot > 0 and n_out / n_tot > 0.05:
            pct = n_out / n_tot * 100
            suggestions.append(f"⚠️ {n_out} outliers ({pct:.1f}%) → consider capping/winsorizing")
        if len(clean) > 0 and nuniq / len(series) < 0.05:
            suggestions.append("💡 Low cardinality → consider treating as categorical")
        if nulls > 0:
            suggestions.append(f"🔧 {nulls} nulls → impute with median (skewed) or mean (normal)")

    elif col_type == "categorical":
        nuniq = int(series.nunique())
        freq = series.value_counts(normalize=True)
        nulls = int(series.isna().sum())

        if nuniq == 2:
            suggestions.append("💡 Binary column → Label Encoding (0/1) is sufficient")
        elif nuniq <= 10:
            suggestions.append(f"💡 {nuniq} categories → One-Hot Encoding recommended")
        elif nuniq <= 50:
            suggestions.append(f"💡 {nuniq} categories → try Target Encoding or Frequency Encoding")
        else:
            suggestions.append(f"⚠️ {nuniq} unique values → high cardinality, consider hashing or embedding")

        if len(freq) > 0 and freq.iloc[0] > 0.9:
            suggestions.append(f"⚠️ '{freq.index[0]}' = {freq.iloc[0]*100:.0f}% → imbalanced, may not be informative")
        if nulls > 0:
            suggestions.append(f"🔧 {nulls} nulls → impute with mode or add 'Unknown' category")

    elif col_type == "datetime":
        nulls = int(series.isna().sum())
        suggestions.append("💡 Extract year, month, day, weekday, hour as features")
        suggestions.append("💡 Compute time since reference (days elapsed)")
        if nulls > 0:
            suggestions.append(f"🔧 {nulls} nulls in datetime → check data pipeline")

    elif col_type == "bool":
        nulls = int(series.isna().sum())
        suggestions.append("💡 Boolean column → already binary, no encoding needed")
        if nulls > 0:
            suggestions.append(f"🔧 {nulls} nulls → impute with mode (True/False)")

    return suggestions


def memory_usage(df: pd.DataFrame) -> str:
    total = df.memory_usage(deep=True).sum()
    if total >= 1_048_576:
        return f"{total / 1_048_576:.1f} MB"
    elif total >= 1024:
        return f"{total / 1024:.1f} KB"
    else:
        return f"{total} B"


def format_number(n) -> str:
    if isinstance(n, float):
        if abs(n) < 0.01 and n != 0:
            return f"{n:.5f}"
        return f"{n:,.2f}"
    return f"{int(n):,}"


@st.cache_data
def load_data(file):
    return pd.read_csv(file)


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>Dataset <span style="color:#7c6af7">Profiler</span></h1>
  <p>Upload a CSV — get a complete analysis report in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FILE UPLOADER
# ─────────────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("", type=["csv"], label_visibility="collapsed")

if uploaded is None:
    st.markdown("""
    <div class="empty-state">
      <div class="icon">📂</div>
      <p style="font-size:1.1rem; color:#e8e8f0; margin-bottom:0.5rem;">Drop a CSV file above to start profiling</p>
      <p>Supports any structured CSV · Nothing leaves your browser</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("Loading..."):
    df = load_data(uploaded)

# Pre-compute column types
col_types = {col: classify_column(df[col]) for col in df.columns}
numeric_cols  = [c for c, t in col_types.items() if t == "numeric"]
cat_cols      = [c for c, t in col_types.items() if t == "categorical"]
datetime_cols = [c for c, t in col_types.items() if t == "datetime"]
bool_cols     = [c for c, t in col_types.items() if t == "bool"]

total_cells   = df.size
missing_total = int(df.isna().sum().sum())
missing_pct   = (missing_total / total_cells * 100) if total_cells > 0 else 0
n_dupes       = int(df.duplicated().sum())
dupe_pct      = (n_dupes / len(df) * 100) if len(df) > 0 else 0

# ─────────────────────────────────────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────────────────────────────────────
def _color_missing(pct):
    if pct < 5:   return "#6af7a7"
    if pct < 20:  return "#f7a76a"
    return "#f76a6a"

def _color_dupes(n, pct):
    if n == 0:    return "#6af7a7"
    if pct < 5:   return "#f7a76a"
    return "#f76a6a"

metrics = [
    ("Rows",       format_number(len(df)),          "#7c6af7"),
    ("Columns",    str(len(df.columns)),             "#e8e8f0"),
    ("Numeric",    str(len(numeric_cols)),           "#e8e8f0"),
    ("Categorical",str(len(cat_cols)),               "#e8e8f0"),
    ("Missing %",  f"{missing_pct:.1f}%",           _color_missing(missing_pct)),
    ("Duplicates", format_number(n_dupes),           _color_dupes(n_dupes, dupe_pct)),
    ("Memory",     memory_usage(df),                 "#e8e8f0"),
]

cols = st.columns(len(metrics))
for col, (label, value, color) in zip(cols, metrics):
    col.markdown(f"""
    <div class="metric-card">
      <div class="label">{label}</div>
      <div class="value" style="color:{color}">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Overview",
    "📊 Distributions",
    "🔗 Correlations",
    "⚠️ Quality",
    "💡 Suggestions",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Column Summary</div>', unsafe_allow_html=True)

    TYPE_BADGE = {
        "numeric":     '<span class="type-num">NUM</span>',
        "categorical": '<span class="type-cat">CAT</span>',
        "datetime":    '<span class="type-dat">DATE</span>',
        "bool":        '<span class="type-bool">BOOL</span>',
    }

    for col in df.columns:
        ct     = col_types[col]
        series = df[col]
        n_null = int(series.isna().sum())
        null_p = n_null / len(df) * 100 if len(df) > 0 else 0
        null_color = "#6af7a7" if null_p == 0 else ("#f7a76a" if null_p < 20 else "#f76a6a")

        # One-line summary
        if ct == "numeric":
            clean = series.dropna()
            if len(clean) > 0:
                summary = (f"mean={clean.mean():.3g} · std={clean.std():.3g} · "
                           f"min={clean.min():.3g} · max={clean.max():.3g}")
            else:
                summary = "all values missing"
        elif ct == "categorical":
            nuniq = int(series.nunique())
            top   = series.value_counts().index[0] if series.nunique() > 0 else "—"
            summary = f"{nuniq} unique · top='{top}'"
        elif ct == "datetime":
            clean = series.dropna()
            if len(clean) > 0:
                summary = f"range: {clean.min()} → {clean.max()}"
            else:
                summary = "all values missing"
        else:  # bool
            vals = series.dropna().unique().tolist()
            summary = f"values: {vals}"

        badge = TYPE_BADGE.get(ct, "")
        st.markdown(f"""
        <div class="col-card">
          <div class="col-card-header">
            <span>
              <span class="col-name">{col}</span>&nbsp;&nbsp;{badge}
            </span>
            <span class="null-pct" style="color:{null_color}">
              {null_p:.1f}% null
            </span>
          </div>
          <div class="col-summary">{summary}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Sample Data (first 10 rows)</div>', unsafe_allow_html=True)
    st.dataframe(df.head(10), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DISTRIBUTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    # ── Numeric ──────────────────────────────────────────────────────────────
    if numeric_cols:
        st.markdown('<div class="section-title">Numeric Columns</div>', unsafe_allow_html=True)
        sel_num = st.selectbox("Select numeric column", numeric_cols, key="sel_num")
        series  = df[sel_num].dropna()

        c_left, c_right = st.columns(2)

        with c_left:
            fig_hist = px.histogram(series, nbins=40, title=f"Histogram — {sel_num}")
            fig_hist.update_traces(marker_color="#7c6af7", marker_line_width=0)
            apply_theme(fig_hist)
            st.plotly_chart(fig_hist, use_container_width=True)

        with c_right:
            fig_box = go.Figure()
            fig_box.add_trace(go.Box(
                y=series,
                name=sel_num,
                boxmean="sd",
                marker_color="#7c6af7",
                line_color="#7c6af7",
            ))
            fig_box.update_layout(title=f"Box Plot — {sel_num}", showlegend=False)
            apply_theme(fig_box)
            st.plotly_chart(fig_box, use_container_width=True)

        # Stats row
        skew_val = float(series.skew()) if len(series) >= 3 else 0.0
        kurt_val = float(series.kurtosis()) if len(series) >= 4 else 0.0
        skew_color = "#f7a76a" if abs(skew_val) > 1 else "#6af7a7"

        if len(series) >= 8:
            _, p_norm = stats.normaltest(series)
            normal_label = "✓ Normal" if p_norm > 0.05 else "✗ Not Normal"
            normal_color = "#6af7a7" if p_norm > 0.05 else "#f7a76a"
        else:
            normal_label = "N/A"
            normal_color = "#6b6b8a"

        stat_cols = st.columns(6)
        stat_data = [
            ("Mean",      f"{series.mean():.4g}",    "#e8e8f0"),
            ("Median",    f"{series.median():.4g}",  "#e8e8f0"),
            ("Std Dev",   f"{series.std():.4g}",     "#e8e8f0"),
            ("Skewness",  f"{skew_val:.3f}",         skew_color),
            ("Kurtosis",  f"{kurt_val:.3f}",         "#e8e8f0"),
            ("Normal?",   normal_label,              normal_color),
        ]
        for sc, (lbl, val, clr) in zip(stat_cols, stat_data):
            sc.markdown(f"""
            <div class="metric-card">
              <div class="label">{lbl}</div>
              <div class="value" style="color:{clr}; font-size:1.1rem">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("No numeric columns found in this dataset.")

    st.markdown("---")

    # ── Categorical ───────────────────────────────────────────────────────────
    if cat_cols:
        st.markdown('<div class="section-title">Categorical Columns</div>', unsafe_allow_html=True)
        sel_cat = st.selectbox("Select categorical column", cat_cols, key="sel_cat")
        series  = df[sel_cat].dropna()
        vc      = series.value_counts().head(20)

        cc_left, cc_right = st.columns(2)

        with cc_left:
            fig_bar = px.bar(
                x=vc.values,
                y=vc.index.astype(str),
                orientation="h",
                title=f"Top Values — {sel_cat}",
                labels={"x": "Count", "y": sel_cat},
            )
            fig_bar.update_traces(marker_color="#6af7a7")
            apply_theme(fig_bar)
            fig_bar.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True)

        with cc_right:
            fig_pie = px.pie(
                values=vc.values,
                names=vc.index.astype(str),
                title=f"Distribution — {sel_cat}",
                hole=0.4,
            )
            apply_theme(fig_pie)
            fig_pie.update_traces(textfont_color="#e8e8f0")
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No categorical columns found in this dataset.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CORRELATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if len(numeric_cols) < 2:
        st.info("Need at least 2 numeric columns to compute correlations.")
    else:
        corr = df[numeric_cols].corr()

        st.markdown('<div class="section-title">Correlation Heatmap</div>', unsafe_allow_html=True)
        fig_hm = px.imshow(
            corr,
            text_auto=".2f",
            zmin=-1, zmax=1,
            color_continuous_scale=[
                [0,   "#f76a6a"],
                [0.5, "#12121a"],
                [1,   "#7c6af7"],
            ],
            aspect="auto",
            title="Pearson Correlation Matrix",
        )
        apply_theme(fig_hm)
        fig_hm.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_hm, use_container_width=True)

        # Top correlations table + scatter side by side
        st.markdown('<div class="section-title">Top Correlations</div>', unsafe_allow_html=True)
        t_left, t_right = st.columns([1, 1])

        with t_left:
            pairs = []
            cols_list = list(corr.columns)
            for i in range(len(cols_list)):
                for j in range(i + 1, len(cols_list)):
                    pairs.append({
                        "Column A": cols_list[i],
                        "Column B": cols_list[j],
                        "Correlation": round(corr.iloc[i, j], 4),
                    })
            pairs_df = (
                pd.DataFrame(pairs)
                .assign(abs_corr=lambda d: d["Correlation"].abs())
                .sort_values("abs_corr", ascending=False)
                .drop(columns="abs_corr")
                .reset_index(drop=True)
            )
            st.dataframe(pairs_df.head(15), use_container_width=True)

        with t_right:
            st.markdown('<div class="section-title">Scatter Explorer</div>', unsafe_allow_html=True)
            x_col = st.selectbox("X axis", numeric_cols, key="scatter_x")
            y_col = st.selectbox("Y axis", numeric_cols,
                                 index=min(1, len(numeric_cols) - 1),
                                 key="scatter_y")
            if x_col != y_col:
                fig_sc = px.scatter(
                    df, x=x_col, y=y_col,
                    trendline="ols",
                    opacity=0.6,
                    title=f"{x_col} vs {y_col}",
                    color_discrete_sequence=["#7c6af7"],
                )
                apply_theme(fig_sc)
                st.plotly_chart(fig_sc, use_container_width=True)
            else:
                st.info("Select two different columns.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — QUALITY
# ══════════════════════════════════════════════════════════════════════════════
with tab4:

    # ── Missing Values ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Missing Values</div>', unsafe_allow_html=True)
    null_df = pd.DataFrame({
        "Column":        df.columns,
        "Missing Count": df.isna().sum().values,
        "Missing %":     (df.isna().sum().values / len(df) * 100).round(2),
    })

    if null_df["Missing Count"].sum() == 0:
        st.success("✅ No missing values — your dataset is complete!")
    else:
        null_nonzero = null_df[null_df["Missing Count"] > 0].sort_values("Missing %", ascending=False)
        fig_null = px.bar(
            null_nonzero, x="Column", y="Missing %",
            color="Missing %",
            color_continuous_scale=["#6af7a7", "#f7a76a", "#f76a6a"],
            title="Missing Values by Column",
        )
        apply_theme(fig_null)
        st.plotly_chart(fig_null, use_container_width=True)
        st.dataframe(null_nonzero.reset_index(drop=True), use_container_width=True)

    # ── Duplicates ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Duplicate Rows</div>', unsafe_allow_html=True)
    if n_dupes == 0:
        st.success("✅ No duplicate rows found.")
    else:
        st.markdown(f"""
        <div class="warn-box">
          ⚠️ Found <strong>{format_number(n_dupes)}</strong> duplicate rows
          ({dupe_pct:.1f}% of dataset)
        </div>
        """, unsafe_allow_html=True)
        if st.checkbox("Show duplicate rows"):
            st.dataframe(df[df.duplicated(keep=False)].head(50), use_container_width=True)

    # ── Outliers ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Outliers (IQR Method)</div>', unsafe_allow_html=True)
    if not numeric_cols:
        st.info("No numeric columns to check for outliers.")
    else:
        outlier_rows = []
        for c in numeric_cols:
            n_out, n_tot = detect_outliers_iqr(df[c])
            if n_tot > 0:
                outlier_rows.append({
                    "Column":     c,
                    "Outliers":   n_out,
                    "Outlier %":  round(n_out / n_tot * 100, 2),
                })
        outlier_df = pd.DataFrame(outlier_rows)
        outlier_nonzero = outlier_df[outlier_df["Outliers"] > 0].sort_values("Outlier %", ascending=False)

        if outlier_nonzero.empty:
            st.success("✅ No significant outliers detected.")
        else:
            fig_out = px.bar(
                outlier_nonzero, x="Column", y="Outlier %",
                color="Outlier %",
                color_continuous_scale=["#f7f76a", "#f7a76a", "#f76a6a"],
                title="Outlier Rate by Column",
            )
            apply_theme(fig_out)
            st.plotly_chart(fig_out, use_container_width=True)
            st.dataframe(outlier_nonzero.reset_index(drop=True), use_container_width=True)

    # ── Constant / Near-Constant ─────────────────────────────────────────────
    st.markdown('<div class="section-title">Constant & Near-Constant Columns</div>', unsafe_allow_html=True)
    issues = []
    for col in df.columns:
        series  = df[col]
        ct      = col_types[col]
        nuniq   = series.nunique()
        if nuniq == 1:
            issues.append(f"🔴 **{col}** — constant column (1 unique value) → drop it")
        elif nuniq / max(len(df), 1) < 0.01 and ct == "numeric":
            issues.append(f"🟡 **{col}** — near-constant ({nuniq} unique values) → consider dropping")

    if not issues:
        st.success("✅ No constant or near-constant columns detected.")
    else:
        for msg in issues:
            st.markdown(f'<div class="warn-box">{msg}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SUGGESTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:

    TYPE_BADGE = {
        "numeric":     '<span class="type-num">NUM</span>',
        "categorical": '<span class="type-cat">CAT</span>',
        "datetime":    '<span class="type-dat">DATE</span>',
        "bool":        '<span class="type-bool">BOOL</span>',
    }

    st.markdown('<div class="section-title">Feature Engineering Suggestions</div>', unsafe_allow_html=True)

    any_suggestions = False
    for col in df.columns:
        ct          = col_types[col]
        suggestions = suggest_features(col, df[col], ct)
        if not suggestions:
            continue
        any_suggestions = True
        badge = TYPE_BADGE.get(ct, "")
        st.markdown(f"""
        <div style="margin-bottom:0.4rem; margin-top:1.2rem;">
          <span class="col-name">{col}</span>&nbsp;&nbsp;{badge}
        </div>
        """, unsafe_allow_html=True)
        for s in suggestions:
            box_class = "warn-box" if s.startswith("⚠️") else "suggestion"
            st.markdown(f'<div class="{box_class}">{s}</div>', unsafe_allow_html=True)

    if not any_suggestions:
        st.success("✅ No specific suggestions — your dataset looks clean!")

    # ── Global Recommendations ────────────────────────────────────────────────
    st.markdown('<div class="section-title">Global Recommendations</div>', unsafe_allow_html=True)

    if missing_pct > 20:
        st.markdown(
            '<div class="warn-box">⚠️ High overall missing rate → '
            'consider multiple imputation (IterativeImputer)</div>',
            unsafe_allow_html=True,
        )

    if n_dupes > 0:
        st.markdown(
            '<div class="warn-box">⚠️ Duplicate rows → '
            'run <code>df.drop_duplicates(inplace=True)</code> before training</div>',
            unsafe_allow_html=True,
        )

    if len(numeric_cols) >= 2:
        corr_m = df[numeric_cols].corr().abs()
        high_pairs = []
        nc = list(corr_m.columns)
        for i in range(len(nc)):
            for j in range(i + 1, len(nc)):
                if corr_m.iloc[i, j] > 0.95:
                    high_pairs.append(f"{nc[i]} & {nc[j]}")
        if high_pairs:
            pairs_str = ", ".join(high_pairs[:5])
            st.markdown(
                f'<div class="warn-box">⚠️ Highly correlated pairs: {pairs_str} → '
                'risk of multicollinearity</div>',
                unsafe_allow_html=True,
            )

    universal = [
        "💡 Always scale numeric features (StandardScaler or MinMaxScaler) for KNN, SVM, neural nets",
        "💡 Use train_test_split with stratify=y if your target is imbalanced",
        "💡 Run SHAP after training to validate feature importances",
    ]
    for u in universal:
        st.markdown(f'<div class="suggestion">{u}</div>', unsafe_allow_html=True)
