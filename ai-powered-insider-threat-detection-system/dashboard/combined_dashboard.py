"""
AI-Powered Insider Threat Detection — Executive Overview (Home Page)
"""
import streamlit as st
import sys, os

# Allow importing components from the dashboard package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from components.data_loader import (
    load_anomaly_scores, load_merged_features, load_file_access,
    load_usb_usage, load_logins, load_emails, get_enriched_scores
)
from components.theme import apply_theme, section_title, glow_divider, risk_badge, RISK_COLOR_MAP
from components.charts import (
    create_risk_donut, create_top_threats_bar, create_model_agreement_heatmap
)

st.set_page_config(
    page_title="Insider Threat Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_theme()

# --- Sidebar ---
st.sidebar.markdown("""
<div style="text-align:center; padding: 20px 0 10px 0;">
    <div style="font-size: 2.5rem;">🛡️</div>
    <div style="font-size: 1.1rem; font-weight: 700; color: #00d4ff; letter-spacing: 1px; margin-top: 4px;">
        THREAT DETECTION
    </div>
    <div style="font-size: 0.7rem; color: #636e72; text-transform: uppercase; letter-spacing: 2px; margin-top: 2px;">
        Security Operations Center
    </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="color: #636e72; font-size: 0.75rem; padding: 10px;">
    <b style="color:#a0a0b0;">System Status:</b> 🟢 Online<br>
    <b style="color:#a0a0b0;">Models:</b> 3 Active<br>
    <b style="color:#a0a0b0;">Pipeline:</b> Complete
</div>
""", unsafe_allow_html=True)

# --- Load Data ---
scores = get_enriched_scores()
features = load_merged_features()
file_access = load_file_access()
usb_usage = load_usb_usage()
logins = load_logins()
emails = load_emails()

# --- Header ---
st.markdown("""
<div style="text-align: center; padding: 10px 0 5px 0;">
    <h1 style="margin: 0; font-size: 2rem;">
        🛡️ Insider Threat Detection Center
    </h1>
    <p style="color: #636e72; font-size: 0.9rem; margin-top: 4px;">
        AI-Powered Security Operations Dashboard — Real-time Threat Posture
    </p>
</div>
""", unsafe_allow_html=True)

glow_divider()

# --- KPI Cards ---
total_users = len(scores)
high_risk = len(scores[scores['risk_level'].isin(['High', 'Critical'])])
red_detected = int(scores['is_red_team'].sum())
total_events = len(file_access) + len(usb_usage) + len(logins) + len(emails)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Users Monitored", total_users, help="Users analyzed by AI models")
with col2:
    st.metric("High-Risk Users", high_risk, delta=f"{high_risk} flagged", delta_color="inverse",
              help="Users with High or Critical risk level")
with col3:
    st.metric("Red Team Detected", f"{red_detected}/3",
              help="Known malicious users correctly identified")
with col4:
    st.metric("Total Events Analyzed", f"{total_events:,}",
              help="Logins + File Access + USB + Emails")

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts Row ---
col_left, col_right = st.columns(2)

with col_left:
    section_title("Threat Level Distribution")
    risk_counts = scores['risk_level'].value_counts().to_dict()
    # Ensure all levels present
    for level in ['Normal', 'Elevated', 'High', 'Critical']:
        risk_counts.setdefault(level, 0)
    fig = create_risk_donut(risk_counts)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    section_title("Top 5 Anomalous Users")
    top5 = scores.nlargest(5, 'max_score')
    fig = create_top_threats_bar(
        top5['user'].tolist(),
        top5['max_score'].tolist(),
        top5['is_red_team'].tolist()
    )
    st.plotly_chart(fig, use_container_width=True)

glow_divider()

# --- Model Agreement Heatmap ---
section_title("Model Agreement — Cross-Model Risk Assessment")
fig = create_model_agreement_heatmap(scores)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Recent Suspicious Activity ---
section_title("Recent Suspicious Activity from High-Risk Users")
high_risk_users = scores[scores['risk_level'].isin(['High', 'Critical'])]['user'].tolist()

if high_risk_users:
    suspicious_files = file_access[file_access['user'].isin(high_risk_users)].copy()
    suspicious_files = suspicious_files.sort_values('access_time', ascending=False).head(15)
    suspicious_files['risk'] = suspicious_files['user'].apply(
        lambda u: scores[scores['user'] == u]['risk_level'].iloc[0]
    )
    suspicious_files['red_team'] = suspicious_files['user'].apply(
        lambda u: '🚩' if int(scores[scores['user'] == u]['is_red_team'].iloc[0]) == 1 else ''
    )
    display_cols = ['user', 'red_team', 'risk', 'file', 'access_time']
    st.dataframe(
        suspicious_files[display_cols].rename(columns={
            'user': 'User', 'red_team': 'Red Team', 'risk': 'Risk Level',
            'file': 'File Accessed', 'access_time': 'Access Time'
        }),
        use_container_width=True,
        height=400
    )
else:
    st.info("No high-risk users detected. System is nominal. ✅")

# --- Footer ---
st.markdown("""
<div style="text-align: center; color: #3a3a4a; font-size: 0.75rem; margin-top: 40px; padding: 20px 0;">
    AI-Powered Insider Threat Detection System • 3 Anomaly Detection Models • Graph Neural Analysis
</div>
""", unsafe_allow_html=True)