"""How It Works — System documentation and AI explainability."""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.theme import apply_theme, section_title, glow_divider

st.set_page_config(page_title="How It Works", page_icon="🧠", layout="wide")
apply_theme()

st.markdown("# 🧠 How It Works")
st.markdown("*System architecture, AI algorithms, and feature engineering explained.*")
glow_divider()

# --- Pipeline Overview ---
section_title("Data Pipeline Architecture")
st.markdown("""
```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  Data Simulation │────▶│  Red Team Inject  │────▶│  Feature Engineering │
│  • Logins        │     │  • After-hours    │     │  • Behavioral        │
│  • File Access   │     │  • Mass downloads │     │  • NLP (Email)       │
│  • USB Usage     │     │  • Suspicious USB │     │  • Graph Centrality  │
│  • Emails        │     │                   │     │                      │
└──────────────────┘     └──────────────────┘     └──────────┬───────────┘
                                                              │
                                                              ▼
                          ┌──────────────────┐     ┌──────────────────────┐
                          │    Dashboard      │◀────│   Model Training     │
                          │  • Streamlit      │     │  • Isolation Forest  │
                          │  • Plotly         │     │  • One-Class SVM     │
                          │  • PyVis Graph    │     │  • Autoencoder (MLP) │
                          └──────────────────┘     └──────────────────────┘
```
""")

glow_divider()

# --- Algorithms ---
section_title("Anomaly Detection Algorithms")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(0,212,255,0.02));
                border: 1px solid rgba(0,212,255,0.15); border-radius: 16px; padding: 24px; height: 100%;">
        <div style="color: #00d4ff; font-size: 1.2rem; font-weight: 700; margin-bottom: 12px;">
            🌲 Isolation Forest
        </div>
        <div style="color: #a0a0b0; font-size: 0.85rem; line-height: 1.6;">
            <b style="color:#c0c0c0;">Principle:</b> Anomalies are few and different — they can be isolated
            with fewer random partitions than normal points.<br><br>
            <b style="color:#c0c0c0;">Math:</b> Anomaly score = 2<sup>−E(h(x))/c(n)</sup> where h(x) is the
            path length to isolate point x, and c(n) is the average path length in a BST.<br><br>
            <b style="color:#c0c0c0;">Strengths:</b> Fast, scales well, no density estimation needed.
            Works with high-dimensional data.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(83,82,237,0.08), rgba(83,82,237,0.02));
                border: 1px solid rgba(83,82,237,0.15); border-radius: 16px; padding: 24px; height: 100%;">
        <div style="color: #5352ed; font-size: 1.2rem; font-weight: 700; margin-bottom: 12px;">
            🎯 One-Class SVM
        </div>
        <div style="color: #a0a0b0; font-size: 0.85rem; line-height: 1.6;">
            <b style="color:#c0c0c0;">Principle:</b> Learn a decision boundary that encloses normal data in
            a high-dimensional kernel space.<br><br>
            <b style="color:#c0c0c0;">Math:</b> Maximize the margin from the origin in feature space φ(x).
            Uses RBF kernel: K(x,y) = exp(−γ‖x−y‖²).<br><br>
            <b style="color:#c0c0c0;">Strengths:</b> Robust boundary estimation, works well when normal data
            is compact. Controls outlier fraction via ν parameter.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255,165,2,0.08), rgba(255,165,2,0.02));
                border: 1px solid rgba(255,165,2,0.15); border-radius: 16px; padding: 24px; height: 100%;">
        <div style="color: #ffa502; font-size: 1.2rem; font-weight: 700; margin-bottom: 12px;">
            🔄 Autoencoder (MLP)
        </div>
        <div style="color: #a0a0b0; font-size: 0.85rem; line-height: 1.6;">
            <b style="color:#c0c0c0;">Principle:</b> Train a neural network to compress and reconstruct input.
            Anomalies have high reconstruction error.<br><br>
            <b style="color:#c0c0c0;">Math:</b> Minimize MSE = (1/n)Σ‖x − f(g(x))‖² where g is encoder
            and f is decoder. Architecture: 12→8→4→8→12.<br><br>
            <b style="color:#c0c0c0;">Strengths:</b> Captures non-linear patterns. Learns a compressed
            representation of normal behavior.
        </div>
    </div>
    """, unsafe_allow_html=True)

glow_divider()

# --- Features ---
section_title("Feature Engineering — 12 Dimensions")

st.markdown("""
| Category | Feature | Source | Description |
|----------|---------|--------|-------------|
| 🕐 **Temporal** | `mean_login_hour` | Logins | Average hour of day for login |
| 🕐 **Temporal** | `mean_logout_hour` | Logins | Average hour of day for logout |
| 📁 **Activity** | `files_per_day` | File Access | Mean daily file access count |
| 🔌 **Activity** | `usb_per_day` | USB Usage | Mean daily USB device usage |
| ✉️ **Activity** | `emails_per_day` | Emails | Mean daily emails sent |
| ⚠️ **Behavioral** | `out_of_session_access` | Logins + Files | Files accessed outside login sessions |
| 🕸️ **Graph** | `degree_centrality` | NetworkX | How many entities a user connects to |
| 🕸️ **Graph** | `betweenness_centrality` | NetworkX | How often user bridges entity paths |
| 🔍 **NLP** | `keyword_flag` | Emails | Frequency of suspicious keywords in subjects |
| 🔍 **NLP** | `subject_len` | Emails | Average email subject length |
| 🔍 **NLP** | `sentiment` | Emails | Sentiment score (placeholder) |
| 🚩 **Label** | `is_red_team` | Red Team | Ground truth malicious user flag |
""")

glow_divider()

# --- Red Team Simulation ---
section_title("Red Team Simulation")

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(255,71,87,0.08), rgba(255,71,87,0.02));
            border: 1px solid rgba(255,71,87,0.15); border-radius: 16px; padding: 24px;">
    <div style="color: #ff4757; font-size: 1.1rem; font-weight: 700; margin-bottom: 12px;">
        🚩 Adversary Simulation
    </div>
    <div style="color: #a0a0b0; font-size: 0.9rem; line-height: 1.8;">
        3 randomly selected users are designated as malicious insiders. The system injects:<br><br>
        <b style="color:#ff6348;">1. After-Hours File Access:</b> 5 file accesses between 12am–4am per red team user<br>
        <b style="color:#ff6348;">2. Mass File Downloads:</b> 20 rapid file accesses within a single hour<br>
        <b style="color:#ff6348;">3. Suspicious USB Usage:</b> USB device plugged in at 2am (highly unusual)<br><br>
        These behaviors create detectable anomalies that the AI models should flag.
        The <b style="color:#e0e0e0;">Detection Performance</b> panel on the Anomaly Detection page shows how
        well each model identifies these injected threats.
    </div>
</div>
""", unsafe_allow_html=True)

glow_divider()

# --- Explainability ---
section_title("Explainability (SHAP & LIME)")

col_shap, col_lime = st.columns(2)

with col_shap:
    st.markdown("""
    <div style="background: rgba(18,18,26,0.9); border: 1px solid #1e1e2e;
                border-radius: 16px; padding: 24px;">
        <div style="color: #2ed573; font-size: 1.1rem; font-weight: 700; margin-bottom: 12px;">
            📊 SHAP (SHapley Additive exPlanations)
        </div>
        <div style="color: #a0a0b0; font-size: 0.85rem; line-height: 1.6;">
            Based on cooperative game theory. Computes each feature's contribution
            to the prediction by averaging over all possible feature orderings.<br><br>
            <b style="color:#c0c0c0;">Formula:</b> φᵢ = Σ |S|!(n-|S|-1)!/n! × [f(S∪{i}) - f(S)]<br><br>
            Provides global and local feature importance for each user's anomaly score.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_lime:
    st.markdown("""
    <div style="background: rgba(18,18,26,0.9); border: 1px solid #1e1e2e;
                border-radius: 16px; padding: 24px;">
        <div style="color: #00d4ff; font-size: 1.1rem; font-weight: 700; margin-bottom: 12px;">
            🔬 LIME (Local Interpretable Model-agnostic Explanations)
        </div>
        <div style="color: #a0a0b0; font-size: 0.85rem; line-height: 1.6;">
            Fits a simple, interpretable model locally around each prediction to approximate
            the complex model's behavior.<br><br>
            <b style="color:#c0c0c0;">Method:</b> Perturbs input features, observes output changes,
            and fits a weighted linear model to estimate feature influence.<br><br>
            Provides per-prediction explanations that are human-readable.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div style="text-align: center; color: #3a3a4a; font-size: 0.75rem; margin-top: 40px; padding: 20px 0;">
    AI-Powered Insider Threat Detection System • Built with Streamlit, Plotly, NetworkX, scikit-learn
</div>
""", unsafe_allow_html=True)
