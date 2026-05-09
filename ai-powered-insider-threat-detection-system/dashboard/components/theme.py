"""SOC Dark Theme - CSS injection and styled component helpers."""
import streamlit as st

COLORS = {
    'primary': '#00d4ff',
    'danger': '#ff4757',
    'warning': '#ffa502',
    'success': '#2ed573',
    'info': '#5352ed',
    'muted': '#636e72',
    'bg': '#0a0a0f',
    'card': '#12121a',
    'border': '#1e1e2e',
    'text': '#c0c0c0',
    'text_bright': '#e0e0e0',
}

RISK_COLOR_MAP = {
    'Normal': '#2ed573',
    'Elevated': '#ffa502',
    'High': '#ff6348',
    'Critical': '#ff4757',
}


def apply_theme():
    """Inject custom CSS for the SOC dark theme."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Hide default branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {background: rgba(10,10,15,0.8); backdrop-filter: blur(10px);}

        .stApp {font-family: 'Inter', sans-serif;}

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d0d15 0%, #10101c 100%);
            border-right: 1px solid rgba(0, 212, 255, 0.08);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdown"] p {color: #a0a0b0;}

        /* Metric cards */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(18,18,26,0.9), rgba(26,26,46,0.6));
            border: 1px solid rgba(0,212,255,0.12);
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        }
        [data-testid="stMetricValue"] {font-size: 1.8rem; font-weight: 700;}
        [data-testid="stMetricLabel"] {color: #888 !important; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {gap: 4px; background: #0d0d15; border-radius: 12px; padding: 4px;}
        .stTabs [data-baseweb="tab"] {border-radius: 8px; color: #888; padding: 8px 20px;}
        .stTabs [aria-selected="true"] {background: rgba(0,212,255,0.12) !important; color: #00d4ff !important;}

        /* DataFrames */
        [data-testid="stDataFrame"] {border: 1px solid #1e1e2e; border-radius: 10px; overflow: hidden;}

        /* Headings */
        h1 {color: #e8e8e8 !important; font-weight: 700 !important; letter-spacing: -0.5px;}
        h2 {color: #d0d0d0 !important; font-weight: 600 !important;}
        h3 {color: #b0b0b0 !important; font-weight: 600 !important;}

        /* Selectbox */
        [data-testid="stSelectbox"] label {color: #a0a0b0 !important; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.5px;}

        /* Dividers */
        hr {border-color: #1e1e2e !important; margin: 1.5rem 0 !important;}

        /* Plotly charts dark background fix */
        .js-plotly-plot .plotly .modebar {background: transparent !important;}

        /* Custom card class */
        .soc-card {
            background: linear-gradient(135deg, rgba(18,18,26,0.95), rgba(26,26,46,0.7));
            border: 1px solid rgba(0,212,255,0.1);
            border-radius: 16px;
            padding: 24px;
            margin: 8px 0;
            box-shadow: 0 4px 24px rgba(0,0,0,0.25);
        }

        /* Badge styles */
        .risk-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .risk-critical {background: rgba(255,71,87,0.2); color: #ff4757; border: 1px solid rgba(255,71,87,0.3);}
        .risk-high {background: rgba(255,99,72,0.2); color: #ff6348; border: 1px solid rgba(255,99,72,0.3);}
        .risk-elevated {background: rgba(255,165,2,0.2); color: #ffa502; border: 1px solid rgba(255,165,2,0.3);}
        .risk-normal {background: rgba(46,213,115,0.2); color: #2ed573; border: 1px solid rgba(46,213,115,0.3);}

        /* Section title */
        .section-title {
            color: #00d4ff;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(0,212,255,0.15);
        }

        /* Glow accent line */
        .glow-line {
            height: 2px;
            background: linear-gradient(90deg, transparent, #00d4ff, transparent);
            margin: 20px 0;
            border: none;
        }
    </style>
    """, unsafe_allow_html=True)


def risk_badge(level):
    """Return HTML for a styled risk badge."""
    css_class = f"risk-{level.lower()}"
    return f'<span class="risk-badge {css_class}">{level}</span>'


def section_title(text):
    """Render a styled section title."""
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def glow_divider():
    """Render a glowing accent line divider."""
    st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)


def soc_card(content_html):
    """Wrap HTML content in a styled SOC card."""
    st.markdown(f'<div class="soc-card">{content_html}</div>', unsafe_allow_html=True)
