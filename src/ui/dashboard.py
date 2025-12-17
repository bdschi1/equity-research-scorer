import streamlit as st
import json
import os
import pandas as pd

# --- CONFIG ---
st.set_page_config(page_title="AI Research Analyst", page_icon="📈", layout="wide")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "data/processed/scores.json")

# --- LOAD DATA ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

data = load_data()

# --- SIDEBAR ---
st.sidebar.title("📚 Research History")
if not data:
    st.sidebar.info("No analysis found. Run 'python main.py' first.")
    st.stop()

# Create a clear label for the sidebar dropdown
options = [f"{d.get('ticker', 'MACRO')} | {os.path.basename(d['file'])[:25]}..." for d in data]
selected_idx = st.sidebar.selectbox("Select Report", range(len(data)), format_func=lambda x: options[x])
report = data[selected_idx]

# --- MAIN HEADER ---
st.title("🤖 AI Investment Committee")
st.markdown("---")

# ====================================================
# MODE A: SINGLE STOCK PITCH
# ====================================================
if report.get('type') == 'single_stock':
    
    # 1. HEADER & VERDICT
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.metric("Overall Score", f"{report.get('overall_score', 0)}/5.0")
    with col2:
        st.subheader(f"Ticker: {report.get('ticker')}")
        verdict = report.get('verdict', 'NEUTRAL')
        color = "green" if verdict == "STRONG" else "red" if verdict == "WEAK" else "orange"
        st.markdown(f"### Verdict: :{color}[{verdict}]")
    with col3:
        st.metric("Boilerplate Removed", report.get('boilerplate_removed', '0%'))

    # 2. THE VARIANT VIEW (New Feature)
    pm = report.get('pm_perspective', {})
    with st.expander("👁️ The Variant View (Second-Level Analysis)", expanded=True):
        st.markdown(f"**The Non-Obvious Insight:**")
        st.info(pm.get('variant_view', 'No variant view identified.'))

    # 3. THE ALPHA TEST (PM Perspective)
    st.markdown("### 🦁 The Alpha Test")
    
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🐻 Bear Case (Counter-Thesis)**")
            st.warning(pm.get('bear_case', 'No bear case identified.'))
            
            st.markdown("**💀 Pre-Mortem (The Kill Shot)**")
            st.error(pm.get('pre_mortem', 'N/A'))
            
        with c2:
            st.markdown("**🔭 Mosaic & Alt-Data Strategy**")
            for point in pm.get('mosaic_data_points', []):
                st.markdown(f"- 🛰️ {point}")
            
            st.markdown("**⚖️ Asymmetry & Timing**")
            st.caption(f"Timing: {pm.get('catalyst_timing', 'N/A')}")
            st.caption(f"Skew: {pm.get('asymmetry_check', 'N/A')}")

    # 4. FINANCIAL FACT CHECK
    st.markdown("### 🔍 Financial Fact Check")
    checks = report.get('fact_checks', [])
    if checks:
        df = pd.DataFrame(checks)
        st.dataframe(
            df[['metric', 'claimed', 'actual', 'status', 'diff_pct']],
            column_config={
                "status": st.column_config.TextColumn("Status", help="MATCH if < 5% diff"),
                "diff_pct": st.column_config.NumberColumn("Diff %", format="%.1f%%"),
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No financial claims verified.")

    # 5. EVIDENCE-BASED TABS
    tab1, tab2, tab3 = st.tabs(["Logic & Thesis", "Catalysts", "Risks"])
    
    with tab1:
        score = report.get('thesis_logic', {})
        st.markdown(f"**Score: {score.get('score')}/5**")
        st.write(score.get('reasoning'))
        if score.get('quote_verbatim'):
            st.caption(f"📝 Evidence: \"{score.get('quote_verbatim')}\"")
        for flag in score.get('red_flags', []):
            st.warning(f"🚩 {flag}")

    with tab2:
        score = report.get('catalyst_quality', {})
        st.markdown(f"**Score: {score.get('score')}/5**")
        st.write(score.get('reasoning'))
        if score.get('quote_verbatim'):
            st.caption(f"📝 Evidence: \"{score.get('quote_verbatim')}\"")

    with tab3:
        score = report.get('risk_analysis', {})
        st.markdown(f"**Score: {score.get('score')}/5**")
        st.write(score.get('reasoning'))
        if score.get('quote_verbatim'):
            st.caption(f"📝 Evidence: \"{score.get('quote_verbatim')}\"")

# ====================================================
# MODE B: MACRO / SECTOR DEEP DIVE
# ====================================================
elif report.get('type') == 'macro_deep_dive':
    
    st.subheader(f"🌍 Sector Deep Dive: {report.get('topic')}")
    st.caption(f"Source: {os.path.basename(report['file'])}")
    
    # 1. THE VARIANT VIEW (New Feature)
    with st.expander("👁️ The Variant View (Second-Level Analysis)", expanded=True):
        st.markdown(f"**The Non-Obvious Insight:**")
        st.info(report.get('variant_view', 'No variant view identified.'))

    # 2. SUMMARY & BEAR CASE
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**Thesis:** {report.get('summary')}")
    with c2:
        st.warning(f"**🐻 Bear Case:** {report.get('bear_case', 'N/A')}")

    # 3. TOP 5 INVESTABLE IDEAS BASKET
    st.markdown("### 🏆 Top 5 Investable Ideas")
    
    ideas = report.get('top_ideas', [])
    cols = st.columns(len(ideas)) if ideas else [st.empty()]
    
    for idx, idea in enumerate(ideas):
        with cols[idx % len(cols)]: # Wrap if many
            with st.container(border=True):
                icon = "🏢" if idea['type'] == 'Ticker' else "🌊"
                st.markdown(f"### {icon}")
                st.markdown(f"**{idea['name']}**")
                st.caption(idea['rationale'])

    # 4. KEY STATS TABLE
    st.markdown("### 📉 Key Sector Data")
    stats = report.get('key_stats', [])
    if stats:
        st.dataframe(pd.DataFrame(stats), use_container_width=True, hide_index=True)

    # 5. IMPLICATION
    st.markdown("### 💡 Investment Implication")
    st.write(report.get('investment_implication'))

else:
    st.error("Unknown report type.")