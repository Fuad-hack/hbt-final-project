"""Activity Timeline — Raw event exploration and temporal analysis."""
import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.data_loader import (
    load_logins, load_file_access, load_usb_usage, load_emails, load_nlp_features
)
from components.theme import apply_theme, section_title, glow_divider
from components.charts import create_activity_timeline, create_hour_heatmap, PLOTLY_LAYOUT

st.set_page_config(page_title="Activity Timeline", page_icon="📊", layout="wide")
apply_theme()

logins = load_logins()
file_access = load_file_access()
usb_usage = load_usb_usage()
emails = load_emails()
nlp_features = load_nlp_features()

st.markdown("# 📊 Activity Timeline")
st.markdown("*Explore raw events, temporal patterns, and suspicious activity across all data sources.*")
glow_divider()

# --- Event Summary KPIs ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Login Sessions", f"{len(logins):,}")
with col2:
    st.metric("File Access Events", f"{len(file_access):,}")
with col3:
    st.metric("USB Events", f"{len(usb_usage):,}")
with col4:
    st.metric("Emails", f"{len(emails):,}")

st.markdown("<br>", unsafe_allow_html=True)

# --- Tabs for event types ---
tab_logins, tab_files, tab_usb, tab_emails, tab_patterns = st.tabs([
    "🔐 Logins", "📁 File Access", "🔌 USB Activity", "✉️ Emails", "🔥 Patterns"
])

with tab_logins:
    section_title("Login Sessions")
    col_filter, col_chart = st.columns([1, 2])
    with col_filter:
        login_users = ['All'] + sorted(logins['user'].unique().tolist())
        sel_login_user = st.selectbox("Filter by user", login_users, key='login_user')

    filtered_logins = logins if sel_login_user == 'All' else logins[logins['user'] == sel_login_user]

    st.dataframe(
        filtered_logins.sort_values('login', ascending=False).rename(
            columns={'user': 'User', 'login': 'Login Time', 'logout': 'Logout Time'}),
        use_container_width=True, height=400
    )
    fig = create_activity_timeline(filtered_logins, 'login', 'Login Events per Day')
    st.plotly_chart(fig, use_container_width=True)

with tab_files:
    section_title("File Access Events")
    col_filter2, col_chart2 = st.columns([1, 2])
    with col_filter2:
        file_users = ['All'] + sorted(file_access['user'].unique().tolist())
        sel_file_user = st.selectbox("Filter by user", file_users, key='file_user')

    filtered_files = file_access if sel_file_user == 'All' else file_access[file_access['user'] == sel_file_user]

    st.dataframe(
        filtered_files.sort_values('access_time', ascending=False).head(500).rename(
            columns={'user': 'User', 'file': 'File', 'access_time': 'Access Time'}),
        use_container_width=True, height=400
    )
    fig = create_activity_timeline(filtered_files, 'access_time', 'File Access Events per Day')
    st.plotly_chart(fig, use_container_width=True)

with tab_usb:
    section_title("USB Device Activity")
    col_filter3, _ = st.columns([1, 2])
    with col_filter3:
        usb_users = ['All'] + sorted(usb_usage['user'].unique().tolist())
        sel_usb_user = st.selectbox("Filter by user", usb_users, key='usb_user')

    filtered_usb = usb_usage if sel_usb_user == 'All' else usb_usage[usb_usage['user'] == sel_usb_user]
    display_usb = filtered_usb.copy()
    display_usb['duration_min'] = (
        (display_usb['unplug_time'] - display_usb['plug_time']).dt.total_seconds() / 60
    ).round(1)

    st.dataframe(
        display_usb.sort_values('plug_time', ascending=False).rename(
            columns={'user': 'User', 'device': 'Device', 'plug_time': 'Plug Time',
                     'unplug_time': 'Unplug Time', 'duration_min': 'Duration (min)'}),
        use_container_width=True, height=400
    )
    fig = create_activity_timeline(filtered_usb, 'plug_time', 'USB Events per Day')
    st.plotly_chart(fig, use_container_width=True)

with tab_emails:
    section_title("Email Communication")
    col_filter4, col_filter5 = st.columns([1, 1])
    with col_filter4:
        email_senders = ['All'] + sorted(emails['sender'].unique().tolist())
        sel_sender = st.selectbox("Filter by sender", email_senders, key='email_sender')
    with col_filter5:
        show_suspicious = st.checkbox("Show only suspicious emails (keyword flagged)", key='suspicious_only')

    filtered_emails = emails.copy()
    if sel_sender != 'All':
        filtered_emails = filtered_emails[filtered_emails['sender'] == sel_sender]

    # Merge with NLP features for keyword flags
    merged_emails = filtered_emails.merge(
        nlp_features[['sender', 'time', 'keyword_flag', 'subject_len']],
        on=['sender', 'time'], how='left'
    )
    merged_emails['flag'] = merged_emails['keyword_flag'].apply(lambda x: '⚠️' if x == 1 else '')

    if show_suspicious:
        merged_emails = merged_emails[merged_emails['keyword_flag'] == 1]

    st.dataframe(
        merged_emails.sort_values('time', ascending=False).head(500)[
            ['sender', 'recipient', 'subject', 'time', 'flag']
        ].rename(columns={'sender': 'From', 'recipient': 'To', 'subject': 'Subject',
                          'time': 'Sent At', 'flag': 'Suspicious'}),
        use_container_width=True, height=400
    )
    fig = create_activity_timeline(filtered_emails, 'time', 'Emails per Day')
    st.plotly_chart(fig, use_container_width=True)

with tab_patterns:
    section_title("Temporal Patterns & Anomalies")

    st.markdown("### After-Hours File Access Heatmap")
    st.markdown("*Red-hot zones indicate file access outside normal business hours (potential insider threat indicator).*")
    fig = create_hour_heatmap(file_access, 'access_time', 'File Access by Day of Week & Hour')
    st.plotly_chart(fig, use_container_width=True)

    glow_divider()

    st.markdown("### USB Activity Heatmap")
    fig = create_hour_heatmap(usb_usage, 'plug_time', 'USB Plug-in by Day of Week & Hour')
    st.plotly_chart(fig, use_container_width=True)

    glow_divider()

    st.markdown("### Email Activity Heatmap")
    fig = create_hour_heatmap(emails, 'time', 'Emails by Day of Week & Hour')
    st.plotly_chart(fig, use_container_width=True)
