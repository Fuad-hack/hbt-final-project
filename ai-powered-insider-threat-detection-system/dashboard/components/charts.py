"""Reusable Plotly chart factories for the SOC dashboard."""
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#c0c0c0', family='Inter, sans-serif', size=12),
    margin=dict(l=40, r=40, t=50, b=40),
)

RISK_COLORS = {
    'Normal': '#2ed573',
    'Elevated': '#ffa502',
    'High': '#ff6348',
    'Critical': '#ff4757',
}

MODEL_COLORS = {
    'isolation_forest': '#00d4ff',
    'oneclass_svm': '#5352ed',
    'autoencoder': '#ffa502',
}


def create_risk_donut(risk_counts):
    """Create a donut chart showing risk level distribution."""
    labels = list(risk_counts.keys())
    values = list(risk_counts.values())
    colors = [RISK_COLORS.get(l, '#636e72') for l in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        hole=0.7,
        marker=dict(colors=colors, line=dict(color='#0a0a0f', width=2)),
        textinfo='label+value',
        textfont=dict(size=13, color='#c0c0c0'),
        hovertemplate='%{label}: %{value} users<extra></extra>',
    )])
    total = sum(values)
    fig.update_layout(
        **PLOTLY_LAYOUT,
        showlegend=False,
        title=dict(text='Risk Distribution', font=dict(size=16, color='#e0e0e0')),
        annotations=[dict(text=f'<b>{total}</b><br>Users', x=0.5, y=0.5,
                         font=dict(size=18, color='#e0e0e0'), showarrow=False)],
        height=350,
    )
    return fig


def create_top_threats_bar(users, scores, is_red_team):
    """Create a horizontal bar chart of top anomalous users."""
    colors = ['#ff4757' if rt else '#00d4ff' for rt in is_red_team]

    fig = go.Figure(data=[go.Bar(
        x=scores, y=users,
        orientation='h',
        marker=dict(color=colors, line=dict(color='rgba(0,0,0,0)', width=0),
                     opacity=0.85),
        hovertemplate='%{y}: %{x:.3f}<extra></extra>',
    )])
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text='Top Anomalous Users', font=dict(size=16, color='#e0e0e0')),
        xaxis=dict(title='Max Anomaly Score', gridcolor='rgba(255,255,255,0.05)',
                   zeroline=False),
        yaxis=dict(autorange='reversed'),
        height=350,
    )
    return fig


def create_model_comparison_radar(user_scores, feature_names=None):
    """Create a radar chart comparing a user's scores across all 3 models."""
    if feature_names is None:
        feature_names = ['Isolation Forest', 'One-Class SVM', 'Autoencoder']

    values = list(user_scores.values())
    values.append(values[0])  # close the polygon
    cats = feature_names + [feature_names[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=cats,
        fill='toself',
        fillcolor='rgba(0,212,255,0.15)',
        line=dict(color='#00d4ff', width=2),
        marker=dict(size=8, color='#00d4ff'),
        hovertemplate='%{theta}: %{r:.3f}<extra></extra>',
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, gridcolor='rgba(255,255,255,0.08)',
                           linecolor='rgba(255,255,255,0.05)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.08)',
                            linecolor='rgba(255,255,255,0.05)'),
        ),
        showlegend=False,
        height=350,
    )
    return fig


def create_feature_radar(feature_dict, title='User Feature Profile'):
    """Create a radar chart for a user's normalized feature values."""
    cats = list(feature_dict.keys())
    vals = list(feature_dict.values())
    vals.append(vals[0])
    cats_closed = cats + [cats[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=cats_closed,
        fill='toself',
        fillcolor='rgba(83,82,237,0.15)',
        line=dict(color='#5352ed', width=2),
        marker=dict(size=6, color='#5352ed'),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, 1], gridcolor='rgba(255,255,255,0.08)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        ),
        title=dict(text=title, font=dict(size=16, color='#e0e0e0')),
        showlegend=False,
        height=400,
    )
    return fig


def create_score_histogram(scores_df, model_name):
    """Create a histogram of anomaly scores for a specific model."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=scores_df[model_name],
        nbinsx=15,
        marker=dict(color=MODEL_COLORS.get(model_name, '#00d4ff'), opacity=0.7,
                     line=dict(color='rgba(255,255,255,0.1)', width=1)),
        hovertemplate='Score: %{x:.3f}<br>Count: %{y}<extra></extra>',
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=f'{model_name.replace("_", " ").title()} Score Distribution',
                   font=dict(size=16, color='#e0e0e0')),
        xaxis=dict(title='Anomaly Score', gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        yaxis=dict(title='Count', gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        height=320,
    )
    return fig


def create_heatmap(z_data, x_labels, y_labels, title='Heatmap'):
    """Create a styled heatmap."""
    fig = go.Figure(data=go.Heatmap(
        z=z_data, x=x_labels, y=y_labels,
        colorscale=[[0, '#0a0a0f'], [0.5, '#5352ed'], [1, '#ff4757']],
        hovertemplate='%{x} - %{y}: %{z}<extra></extra>',
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font=dict(size=16, color='#e0e0e0')),
        height=400,
    )
    return fig


def create_activity_timeline(df, date_col, title='Activity Over Time'):
    """Create a daily event count line chart."""
    daily = df.groupby(df[date_col].dt.date).size().reset_index(name='count')
    daily.columns = ['date', 'count']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily['date'], y=daily['count'],
        mode='lines+markers',
        line=dict(color='#00d4ff', width=2),
        marker=dict(size=5, color='#00d4ff'),
        fill='tonexty',
        fillcolor='rgba(0,212,255,0.08)',
        hovertemplate='%{x}: %{y} events<extra></extra>',
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font=dict(size=16, color='#e0e0e0')),
        xaxis=dict(title='Date', gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(title='Events', gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        height=320,
    )
    return fig


def create_hour_heatmap(df, time_col, title='Activity by Day & Hour'):
    """Create a day-of-week × hour-of-day heatmap."""
    df = df.copy()
    df['hour'] = df[time_col].dt.hour
    df['dow'] = df[time_col].dt.day_name()
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = df.groupby(['dow', 'hour']).size().reset_index(name='count')
    pivot_table = pivot.pivot(index='dow', columns='hour', values='count').reindex(days_order).fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=[f'{h}:00' for h in pivot_table.columns],
        y=pivot_table.index,
        colorscale=[[0, '#0a0a0f'], [0.3, '#12121a'], [0.6, '#5352ed'], [1, '#ff4757']],
        hovertemplate='%{y} %{x}: %{z} events<extra></extra>',
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font=dict(size=16, color='#e0e0e0')),
        height=350,
    )
    return fig


def create_model_agreement_heatmap(scores_df):
    """Create a heatmap showing model agreement on user risk."""
    models = ['isolation_forest', 'oneclass_svm', 'autoencoder']
    users = scores_df['user'].tolist()

    # Normalize each model's scores to 0-1 for comparison
    z = []
    for m in models:
        vals = scores_df[m].values
        mn, mx = vals.min(), vals.max()
        if mx > mn:
            normed = (vals - mn) / (mx - mn)
        else:
            normed = np.zeros_like(vals)
        z.append(normed)

    fig = go.Figure(data=go.Heatmap(
        z=z, x=users,
        y=['Isolation Forest', 'One-Class SVM', 'Autoencoder'],
        colorscale=[[0, '#12121a'], [0.4, '#ffa502'], [0.7, '#ff6348'], [1, '#ff4757']],
        hovertemplate='%{y} → %{x}: %{z:.2f}<extra></extra>',
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text='Model Agreement Heatmap (Normalized)', font=dict(size=16, color='#e0e0e0')),
        height=280,
    )
    return fig
