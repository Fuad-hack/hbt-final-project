"""User Investigation — Deep profile for investigating a specific user."""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.data_loader import (
    get_enriched_scores, load_merged_features, load_logins,
    load_file_access, load_usb_usage, load_emails, load_nlp_features
)
from components.theme import apply_theme, section_title, glow_divider, risk_badge, RISK_COLOR_MAP
from components.charts import create_feature_radar, create_model_comparison_radar, PLOTLY_LAYOUT

st.set_page_config(page_title="User Investigation", page_icon="👤", layout="wide")
apply_theme()

scores = get_enriched_scores()
features = load_merged_features()
logins = load_logins()
file_access = load_file_access()
usb_usage = load_usb_usage()
emails = load_emails()
nlp_features = load_nlp_features()

st.markdown("# 👤 User Investigation")
st.markdown("*Deep-dive into individual user behavior, features, and anomaly scores.*")
glow_divider()

# --- User Selector ---
sorted_users = scores.sort_values('max_score', ascending=False)['user'].tolist()
selected_user = st.selectbox("Select User to Investigate", sorted_users,
                              help="Users sorted by risk (highest first)")

user_score_row = scores[scores['user'] == selected_user].iloc[0]
user_feat_row = features[features['user'] == selected_user].iloc[0]
risk_level = user_score_row['risk_level']
is_red = int(user_score_row['is_red_team']) == 1

# --- User Profile Card ---
risk_color = RISK_COLOR_MAP.get(risk_level, '#636e72')
red_flag_html = '<span style="font-size:1.5rem; margin-left:10px;">🚩 RED TEAM</span>' if is_red else ''

st.markdown(f"""
<div style="background: linear-gradient(135deg, rgba(18,18,26,0.95), rgba(26,26,46,0.7));
            border: 1px solid {risk_color}33; border-radius: 16px; padding: 24px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.3); margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 16px;">
        <div style="background: {risk_color}22; border: 2px solid {risk_color}; border-radius: 50%;
                    width: 60px; height: 60px; display: flex; align-items: center; justify-content: center;
                    font-size: 1.5rem; font-weight: 700; color: {risk_color};">
            {selected_user[4:]}
        </div>
        <div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #e0e0e0;">
                {selected_user}{red_flag_html}
            </div>
            <div style="margin-top: 4px;">
                <span style="background: {risk_color}22; color: {risk_color}; border: 1px solid {risk_color}44;
                             padding: 3px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;
                             text-transform: uppercase; letter-spacing: 0.5px;">
                    {risk_level} Risk
                </span>
                <span style="color: #636e72; margin-left: 12px; font-size: 0.85rem;">
                    Max Score: {user_score_row['max_score']:.4f}
                </span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Scores + Feature Radar ---
col_scores, col_radar = st.columns(2)

with col_scores:
    section_title("Anomaly Scores by Model")
    for model_name, color in [('isolation_forest', '#00d4ff'), ('oneclass_svm', '#5352ed'), ('autoencoder', '#ffa502')]:
        val = user_score_row[model_name]
        st.markdown(f"""
        <div style="background: rgba(18,18,26,0.8); border: 1px solid #1e1e2e; border-radius: 10px;
                    padding: 12px 16px; margin: 6px 0; display: flex; justify-content: space-between; align-items: center;">
            <span style="color: {color}; font-weight: 600;">{model_name.replace('_',' ').title()}</span>
            <span style="color: #e0e0e0; font-size: 1.1rem; font-weight: 700;">{val:.4f}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    fig = create_model_comparison_radar(
        {'Isolation Forest': user_score_row['isolation_forest'],
         'One-Class SVM': user_score_row['oneclass_svm'],
         'Autoencoder': user_score_row['autoencoder']},
    )
    st.plotly_chart(fig, use_container_width=True)

with col_radar:
    section_title("Behavioral Feature Profile")
    feature_cols = ['mean_login_hour', 'mean_logout_hour', 'files_per_day', 'usb_per_day',
                    'emails_per_day', 'out_of_session_access', 'degree_centrality',
                    'betweenness_centrality', 'keyword_flag', 'subject_len']
    # Normalize features to 0-1 for radar
    feat_vals = {}
    for col in feature_cols:
        if col in features.columns:
            mn = features[col].min()
            mx = features[col].max()
            if mx > mn:
                feat_vals[col.replace('_', ' ').title()] = (user_feat_row[col] - mn) / (mx - mn)
            else:
                feat_vals[col.replace('_', ' ').title()] = 0.5
    fig = create_feature_radar(feat_vals, title=f'{selected_user} Feature Profile')
    st.plotly_chart(fig, use_container_width=True)

glow_divider()

# --- Behavioral Details ---
col_login, col_files = st.columns(2)

with col_login:
    section_title("Login Sessions")
    user_logins = logins[logins['user'] == selected_user].sort_values('login', ascending=False)
    if not user_logins.empty:
        st.dataframe(
            user_logins[['login', 'logout']].rename(columns={'login': 'Login Time', 'logout': 'Logout Time'}),
            use_container_width=True, height=300
        )
        # Login hour distribution
        hours = user_logins['login'].dt.hour
        fig = go.Figure(data=[go.Histogram(
            x=hours, nbinsx=24,
            marker=dict(color='#00d4ff', opacity=0.7, line=dict(color='rgba(255,255,255,0.1)', width=1)),
        )])
        fig.update_layout(**PLOTLY_LAYOUT, title=dict(text='Login Hour Distribution', font=dict(size=14, color='#e0e0e0')),
                         xaxis=dict(title='Hour of Day', dtick=2, gridcolor='rgba(255,255,255,0.05)'),
                         yaxis=dict(title='Count', gridcolor='rgba(255,255,255,0.05)'), height=250)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No login records found for this user.")

with col_files:
    section_title("File Access Activity")
    user_files = file_access[file_access['user'] == selected_user].sort_values('access_time', ascending=False)
    if not user_files.empty:
        st.dataframe(
            user_files[['file', 'access_time']].head(20).rename(
                columns={'file': 'File', 'access_time': 'Access Time'}),
            use_container_width=True, height=300
        )
        # File access timeline scatter
        fig = go.Figure(data=[go.Scatter(
            x=user_files['access_time'], y=user_files['file'],
            mode='markers',
            marker=dict(size=6, color='#2ed573', opacity=0.7),
            hovertemplate='%{x}<br>%{y}<extra></extra>',
        )])
        fig.update_layout(**PLOTLY_LAYOUT, title=dict(text='File Access Timeline', font=dict(size=14, color='#e0e0e0')),
                         height=250, xaxis=dict(gridcolor='rgba(255,255,255,0.05)'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No file access records found for this user.")

st.markdown("<br>", unsafe_allow_html=True)

# --- USB + Emails ---
col_usb, col_email = st.columns(2)

with col_usb:
    section_title("USB Device Activity")
    user_usb = usb_usage[usb_usage['user'] == selected_user].sort_values('plug_time', ascending=False)
    if not user_usb.empty:
        display_usb = user_usb[['device', 'plug_time', 'unplug_time']].copy()
        display_usb['duration_min'] = (
            (display_usb['unplug_time'] - display_usb['plug_time']).dt.total_seconds() / 60
        ).round(1)
        st.dataframe(
            display_usb.rename(columns={'device': 'Device', 'plug_time': 'Plug Time',
                                        'unplug_time': 'Unplug Time', 'duration_min': 'Duration (min)'}),
            use_container_width=True, height=300
        )
    else:
        st.info("No USB activity for this user.")

with col_email:
    section_title("Email Activity")
    user_emails = emails[emails['sender'] == f'{selected_user}@company.com'].sort_values('time', ascending=False)
    if not user_emails.empty:
        # Merge with NLP features
        user_nlp = nlp_features[nlp_features['sender'] == f'{selected_user}@company.com']
        if not user_nlp.empty:
            display_email = user_emails.merge(
                user_nlp[['sender', 'time', 'keyword_flag']],
                on=['sender', 'time'], how='left'
            )
            display_email['suspicious'] = display_email['keyword_flag'].apply(
                lambda x: '⚠️' if x == 1 else ''
            )
            st.dataframe(
                display_email[['recipient', 'subject', 'time', 'suspicious']].head(20).rename(
                    columns={'recipient': 'To', 'subject': 'Subject', 'time': 'Sent At',
                             'suspicious': 'Flag'}),
                use_container_width=True, height=300
            )
        else:
            st.dataframe(
                user_emails[['recipient', 'subject', 'time']].head(20).rename(
                    columns={'recipient': 'To', 'subject': 'Subject', 'time': 'Sent At'}),
                use_container_width=True, height=300
            )
    else:
        st.info("No emails found from this user.")
