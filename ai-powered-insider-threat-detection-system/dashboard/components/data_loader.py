"""Centralized data loading with Streamlit caching."""
import streamlit as st
import pandas as pd
import os

DATA_DIR = 'data'
MODEL_DIR = 'models'


@st.cache_data
def load_logins():
    return pd.read_csv(os.path.join(DATA_DIR, 'logins.csv'), parse_dates=['login', 'logout'])


@st.cache_data
def load_file_access():
    return pd.read_csv(os.path.join(DATA_DIR, 'file_access.csv'), parse_dates=['access_time'])


@st.cache_data
def load_usb_usage():
    return pd.read_csv(os.path.join(DATA_DIR, 'usb_usage.csv'), parse_dates=['plug_time', 'unplug_time'])


@st.cache_data
def load_emails():
    return pd.read_csv(os.path.join(DATA_DIR, 'emails.csv'), parse_dates=['time'])


@st.cache_data
def load_features():
    return pd.read_csv(os.path.join(DATA_DIR, 'features.csv'))


@st.cache_data
def load_merged_features():
    return pd.read_csv(os.path.join(DATA_DIR, 'merged_features.csv'))


@st.cache_data
def load_anomaly_scores():
    return pd.read_csv(os.path.join(DATA_DIR, 'anomaly_scores.csv'))


@st.cache_data
def load_graph_features():
    return pd.read_csv(os.path.join(DATA_DIR, 'graph_features.csv'))


@st.cache_data
def load_nlp_features():
    return pd.read_csv(os.path.join(DATA_DIR, 'nlp_email_features.csv'))


@st.cache_data
def load_red_team():
    return pd.read_csv(os.path.join(DATA_DIR, 'red_team_users.csv'))


def get_risk_level(score):
    """Classify a user's max anomaly score into a risk level."""
    if score > 1.5:
        return 'Critical'
    elif score > 1.0:
        return 'High'
    elif score > 0.5:
        return 'Elevated'
    else:
        return 'Normal'


def get_enriched_scores():
    """Load anomaly scores enriched with risk levels and max score."""
    scores = load_anomaly_scores()
    scores['max_score'] = scores[['isolation_forest', 'oneclass_svm', 'autoencoder']].max(axis=1)
    scores['risk_level'] = scores['max_score'].apply(get_risk_level)
    return scores
