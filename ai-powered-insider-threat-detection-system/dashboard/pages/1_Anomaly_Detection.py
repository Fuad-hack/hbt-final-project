"""Anomaly Detection — Model comparison and detailed scoring."""
import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.data_loader import load_anomaly_scores, load_merged_features, get_enriched_scores
from components.theme import apply_theme, section_title, glow_divider, risk_badge, RISK_COLOR_MAP
from components.charts import (
    create_score_histogram, create_model_comparison_radar,
    create_model_agreement_heatmap, MODEL_COLORS
)

st.set_page_config(page_title="Anomaly Detection", page_icon="🔍", layout="wide")
apply_theme()

scores = get_enriched_scores()
features = load_merged_features()

st.markdown("# 🔍 Anomaly Detection")
st.markdown("*Compare model outputs, explore score distributions, and investigate flagged users.*")
glow_divider()

# --- Model Selector ---
col_sel, col_info = st.columns([1, 2])
with col_sel:
    model = st.selectbox("Select Model", ['isolation_forest', 'oneclass_svm', 'autoencoder'],
                         format_func=lambda x: x.replace('_', ' ').title())

with col_info:
    model_descriptions = {
        'isolation_forest': '**Isolation Forest** — Ensemble of random trees. Anomalies are isolated faster (shorter path).',
        'oneclass_svm': '**One-Class SVM** — Finds a boundary enclosing normal data. Points outside are anomalies.',
        'autoencoder': '**Autoencoder (MLP)** — Learns to reconstruct input. High reconstruction error = anomaly.',
    }
    st.info(model_descriptions[model])

# --- Ranked User Table ---
section_title("User Anomaly Rankings")
df = pd.merge(features, scores, on='user')
df['rank'] = df[model].rank(ascending=False).astype(int)
df_sorted = df.sort_values(model, ascending=False)

# Format display
display_df = df_sorted[['user', 'rank', model, 'risk_level', 'is_red_team', 'max_score']].copy()
display_df['is_red_team'] = display_df['is_red_team'].apply(lambda x: '🚩 Yes' if x == 1 else '')
display_df.columns = ['User', 'Rank', f'{model.replace("_"," ").title()} Score', 'Risk Level', 'Red Team', 'Max Score']

st.dataframe(display_df, use_container_width=True, height=450,
             column_config={
                 'Rank': st.column_config.NumberColumn(format="%d"),
                 f'{model.replace("_"," ").title()} Score': st.column_config.NumberColumn(format="%.4f"),
                 'Max Score': st.column_config.NumberColumn(format="%.4f"),
             })

st.markdown("<br>", unsafe_allow_html=True)

# --- Score Distribution + Radar ---
col_hist, col_radar = st.columns(2)

with col_hist:
    section_title("Score Distribution")
    fig = create_score_histogram(scores, model)
    st.plotly_chart(fig, use_container_width=True)

with col_radar:
    section_title("Model Comparison for Selected User")
    selected_user = st.selectbox("Select user to compare", df_sorted['user'].tolist(), key='radar_user')
    user_row = scores[scores['user'] == selected_user].iloc[0]
    user_scores = {
        'Isolation Forest': user_row['isolation_forest'],
        'One-Class SVM': user_row['oneclass_svm'],
        'Autoencoder': user_row['autoencoder'],
    }
    fig = create_model_comparison_radar(user_scores, list(user_scores.keys()))
    st.plotly_chart(fig, use_container_width=True)

glow_divider()

# --- Detection Performance ---
section_title("Detection Performance vs Ground Truth")
col_tp, col_fp = st.columns(2)

red_team_users = set(scores[scores['is_red_team'] == 1]['user'].tolist())
flagged_users = set(scores[scores['risk_level'].isin(['High', 'Critical'])]['user'].tolist())
tp = red_team_users & flagged_users
fp = flagged_users - red_team_users
fn = red_team_users - flagged_users
tn_count = len(scores) - len(tp) - len(fp) - len(fn)

with col_tp:
    st.markdown(f"""
    <div style="background: rgba(46,213,115,0.1); border: 1px solid rgba(46,213,115,0.2);
                border-radius: 12px; padding: 20px; text-align: center;">
        <div style="color: #2ed573; font-size: 2rem; font-weight: 700;">{len(tp)}</div>
        <div style="color: #888; font-size: 0.8rem; text-transform: uppercase;">True Positives</div>
        <div style="color: #636e72; font-size: 0.75rem; margin-top: 4px;">
            Red team users correctly flagged: {', '.join(tp) if tp else 'None'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_fp:
    st.markdown(f"""
    <div style="background: rgba(255,165,2,0.1); border: 1px solid rgba(255,165,2,0.2);
                border-radius: 12px; padding: 20px; text-align: center;">
        <div style="color: #ffa502; font-size: 2rem; font-weight: 700;">{len(fp)}</div>
        <div style="color: #888; font-size: 0.8rem; text-transform: uppercase;">False Positives</div>
        <div style="color: #636e72; font-size: 0.75rem; margin-top: 4px;">
            Normal users flagged high: {', '.join(fp) if fp else 'None'}
        </div>
    </div>
    """, unsafe_allow_html=True)

col_fn, col_tn = st.columns(2)
with col_fn:
    st.markdown(f"""
    <div style="background: rgba(255,71,87,0.1); border: 1px solid rgba(255,71,87,0.2);
                border-radius: 12px; padding: 20px; text-align: center;">
        <div style="color: #ff4757; font-size: 2rem; font-weight: 700;">{len(fn)}</div>
        <div style="color: #888; font-size: 0.8rem; text-transform: uppercase;">False Negatives</div>
        <div style="color: #636e72; font-size: 0.75rem; margin-top: 4px;">
            Red team users missed: {', '.join(fn) if fn else 'None'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_tn:
    st.markdown(f"""
    <div style="background: rgba(0,212,255,0.1); border: 1px solid rgba(0,212,255,0.2);
                border-radius: 12px; padding: 20px; text-align: center;">
        <div style="color: #00d4ff; font-size: 2rem; font-weight: 700;">{tn_count}</div>
        <div style="color: #888; font-size: 0.8rem; text-transform: uppercase;">True Negatives</div>
        <div style="color: #636e72; font-size: 0.75rem; margin-top: 4px;">
            Normal users correctly classified
        </div>
    </div>
    """, unsafe_allow_html=True)
