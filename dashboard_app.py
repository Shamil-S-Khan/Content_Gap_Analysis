"""
Interactive Visual Dashboard for Content Gap Analysis
Provides real-time visualizations of analysis results using Plotly Dash
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
from pathlib import Path
import pandas as pd
import requests

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

app.title = "Content Gap Analysis Dashboard"
server = app.server  # For deployment

# Get API URL from environment or use default
API_URL = os.getenv('API_URL', 'http://localhost:8000')

# Color scheme
COLORS = {
    'primary': '#2196F3',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'danger': '#F44336',
    'info': '#00BCD4',
    'dark': '#212121',
    'light': '#F5F5F5'
}


def load_latest_results():
    """Load the latest analysis results from API or file"""
    # Try API first
    try:
        response = requests.get(f"{API_URL}/package", timeout=10)
        if response.status_code == 200:
            print(f"✅ Loaded data from API: {API_URL}")
            return response.json()
    except Exception as e:
        print(f"⚠️ Could not fetch from API ({API_URL}): {e}")
    
    # Fallback to local file
    package_path = 'content_gap_analysis_package.json'
    
    if not os.path.exists(package_path):
        print(f"❌ No local data file found: {package_path}")
        return None
    
    try:
        with open(package_path, 'r', encoding='utf-8') as f:
            print(f"✅ Loaded data from local file: {package_path}")
            return json.load(f)
    except Exception as e:
        print(f"Error loading results: {e}")
        return None


def create_header():
    """Create dashboard header"""
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.I(className="fas fa-chart-line me-2"),
                    dbc.NavbarBrand("Content Gap Analysis Dashboard", className="ms-2")
                ], width="auto"),
            ], align="center", className="g-0"),
            dbc.Row([
                dbc.Col([
                    html.Button(
                        [html.I(className="fas fa-sync-alt me-2"), "Refresh Data"],
                        id="refresh-button",
                        className="btn btn-light btn-sm"
                    )
                ], width="auto")
            ], align="center")
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    )


def create_summary_cards(data):
    """Create summary metric cards"""
    if not data:
        return html.Div("No data available. Run analysis first.", className="alert alert-warning")
    
    metadata = data.get('metadata', {})
    gaps = data.get('gaps', [])
    recommendations = data.get('recommendations', [])
    model_metrics = data.get('model_metrics', {})
    
    cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-exclamation-triangle fa-2x mb-2", style={'color': COLORS['warning']}),
                    html.H3(str(len(gaps)), className="mb-0"),
                    html.P("Content Gaps", className="text-muted mb-0")
                ])
            ], className="text-center shadow-sm")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-lightbulb fa-2x mb-2", style={'color': COLORS['success']}),
                    html.H3(str(len(recommendations)), className="mb-0"),
                    html.P("Recommendations", className="text-muted mb-0")
                ])
            ], className="text-center shadow-sm")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-bullseye fa-2x mb-2", style={'color': COLORS['info']}),
                    html.H3(f"{model_metrics.get('accuracy', 0)*100:.1f}%", className="mb-0"),
                    html.P("Model Accuracy", className="text-muted mb-0")
                ])
            ], className="text-center shadow-sm")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-calendar-alt fa-2x mb-2", style={'color': COLORS['primary']}),
                    html.H3("90", className="mb-0"),
                    html.P("Days Roadmap", className="text-muted mb-0")
                ])
            ], className="text-center shadow-sm")
        ], md=3)
    ], className="mb-4")
    
    return cards


def create_gap_distribution_chart(gaps):
    """Create gap type distribution pie chart"""
    if not gaps:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    gap_types = {}
    for gap in gaps:
        gap_type = gap.get('gap_type', 'unknown')
        gap_types[gap_type] = gap_types.get(gap_type, 0) + 1
    
    fig = go.Figure(data=[go.Pie(
        labels=[gt.replace('-', ' ').title() for gt in gap_types.keys()],
        values=list(gap_types.values()),
        hole=0.4,
        marker=dict(colors=[COLORS['primary'], COLORS['success'], COLORS['warning'], COLORS['danger']])
    )])
    
    fig.update_layout(
        title="Gap Distribution by Type",
        height=400,
        showlegend=True
    )
    
    return fig


def create_impact_score_chart(gaps):
    """Create impact score distribution histogram"""
    if not gaps:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    impact_scores = [g.get('impact_score', 0) for g in gaps]
    
    fig = go.Figure(data=[go.Histogram(
        x=impact_scores,
        nbinsx=20,
        marker=dict(color=COLORS['primary']),
        name="Impact Score"
    )])
    
    fig.update_layout(
        title="Impact Score Distribution",
        xaxis_title="Impact Score (0-100)",
        yaxis_title="Number of Gaps",
        height=400,
        bargap=0.1
    )
    
    return fig


def create_recommendations_timeline(recommendations):
    """Create recommendations timeline chart"""
    if not recommendations:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    # Convert to DataFrame
    df = pd.DataFrame(recommendations)
    
    # Group by publish priority (date)
    df['publish_date'] = pd.to_datetime(df['publish_priority'])
    df['month'] = df['publish_date'].dt.to_period('M').astype(str)
    
    monthly_counts = df.groupby('month').size().reset_index(name='count')
    
    fig = go.Figure(data=[go.Bar(
        x=monthly_counts['month'],
        y=monthly_counts['count'],
        marker=dict(color=COLORS['success']),
        text=monthly_counts['count'],
        textposition='auto'
    )])
    
    fig.update_layout(
        title="Content Publication Timeline",
        xaxis_title="Month",
        yaxis_title="Number of Recommendations",
        height=400
    )
    
    return fig


def create_difficulty_breakdown(recommendations):
    """Create difficulty vs impact scatter plot"""
    if not recommendations:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    df = pd.DataFrame(recommendations)
    
    # Map difficulty to numeric
    difficulty_map = {'low': 1, 'medium': 2, 'high': 3}
    df['difficulty_num'] = df['difficulty'].map(difficulty_map)
    
    fig = px.scatter(
        df,
        x='difficulty_num',
        y='impact_score',
        size='impact_score',
        color='difficulty',
        hover_data=['title', 'difficulty', 'impact_score'],
        color_discrete_map={'low': COLORS['success'], 'medium': COLORS['warning'], 'high': COLORS['danger']},
        title="Recommendations: Difficulty vs Impact"
    )
    
    fig.update_xaxes(
        tickvals=[1, 2, 3],
        ticktext=['Low', 'Medium', 'High'],
        title="Difficulty Level"
    )
    
    fig.update_yaxes(title="Impact Score")
    fig.update_layout(height=400)
    
    return fig


def create_model_metrics_card(model_metrics):
    """Create model performance metrics card"""
    if not model_metrics:
        return html.Div("No metrics available", className="alert alert-info")
    
    accuracy = model_metrics.get('accuracy', 0) * 100
    precision = model_metrics.get('precision', 0) * 100
    recall = model_metrics.get('recall', 0) * 100
    f1_macro = model_metrics.get('f1_macro', 0) * 100
    
    status = "success" if accuracy >= 80 else "warning"
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-robot me-2"),
            "ML Model Performance"
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4(f"{accuracy:.1f}%", className=f"text-{status}"),
                        html.P("Accuracy", className="text-muted mb-0")
                    ], className="text-center mb-3")
                ], md=3),
                dbc.Col([
                    html.Div([
                        html.H4(f"{precision:.1f}%"),
                        html.P("Precision", className="text-muted mb-0")
                    ], className="text-center mb-3")
                ], md=3),
                dbc.Col([
                    html.Div([
                        html.H4(f"{recall:.1f}%"),
                        html.P("Recall", className="text-muted mb-0")
                    ], className="text-center mb-3")
                ], md=3),
                dbc.Col([
                    html.Div([
                        html.H4(f"{f1_macro:.1f}%"),
                        html.P("F1 Score", className="text-muted mb-0")
                    ], className="text-center mb-3")
                ], md=3)
            ]),
            html.Hr(),
            dbc.Alert(
                [
                    html.I(className="fas fa-check-circle me-2"),
                    f"Model meets {model_metrics.get('samples_evaluated', 0)} sample validation threshold with {accuracy:.1f}% accuracy."
                ],
                color=status,
                className="mb-0"
            )
        ])
    ], className="shadow-sm mb-4")


def create_top_recommendations_table(recommendations):
    """Create top recommendations table"""
    if not recommendations:
        return html.Div("No recommendations available", className="alert alert-info")
    
    # Get top 10
    top_recs = sorted(recommendations, key=lambda x: x.get('impact_score', 0), reverse=True)[:10]
    
    rows = []
    for i, rec in enumerate(top_recs, 1):
        difficulty_color = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger'
        }.get(rec.get('difficulty', 'medium'), 'secondary')
        
        rows.append(html.Tr([
            html.Td(str(i)),
            html.Td(rec.get('title', 'N/A')),
            html.Td([
                dbc.Badge(str(rec.get('impact_score', 0)), color="primary", className="me-1"),
                html.Small(f"/100", className="text-muted")
            ]),
            html.Td(dbc.Badge(rec.get('difficulty', 'N/A').title(), color=difficulty_color)),
            html.Td(rec.get('publish_priority', 'N/A')),
            html.Td(rec.get('intent', 'N/A').title())
        ]))
    
    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("#"),
            html.Th("Title"),
            html.Th("Impact"),
            html.Th("Difficulty"),
            html.Th("Target Date"),
            html.Th("Intent")
        ])),
        html.Tbody(rows)
    ], bordered=True, hover=True, responsive=True, striped=True)
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-star me-2"),
            "Top 10 Priority Recommendations"
        ]),
        dbc.CardBody(table, className="p-0")
    ], className="shadow-sm mb-4")


# Main layout
app.layout = html.Div([
    create_header(),
    
    dbc.Container([
        # Hidden div for storing data
        html.Div(id='data-store', style={'display': 'none'}),
        
        # Last updated timestamp
        html.Div(id='last-updated', className="text-muted mb-3"),
        
        # Summary cards
        html.Div(id='summary-cards'),
        
        # Model metrics
        html.Div(id='model-metrics'),
        
        # Charts row 1
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(dcc.Graph(id='gap-distribution-chart'))
                ], className="shadow-sm")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(dcc.Graph(id='impact-score-chart'))
                ], className="shadow-sm")
            ], md=6)
        ], className="mb-4"),
        
        # Charts row 2
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(dcc.Graph(id='timeline-chart'))
                ], className="shadow-sm")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(dcc.Graph(id='difficulty-chart'))
                ], className="shadow-sm")
            ], md=6)
        ], className="mb-4"),
        
        # Top recommendations table
        html.Div(id='top-recommendations-table'),
        
        # Footer
        html.Footer([
            html.Hr(),
            html.P([
                "Content Gap Analysis Dashboard • ",
                html.Small(f"Generated with AI-powered analysis", className="text-muted")
            ], className="text-center text-muted")
        ], className="mt-5 mb-3")
    ], fluid=True),
    
    # Auto-refresh interval (30 seconds)
    dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0)
])


@app.callback(
    [
        Output('data-store', 'children'),
        Output('last-updated', 'children')
    ],
    [
        Input('refresh-button', 'n_clicks'),
        Input('interval-component', 'n_intervals')
    ]
)
def update_data(n_clicks, n_intervals):
    """Load and update data"""
    data = load_latest_results()
    
    if data:
        metadata = data.get('metadata', {})
        last_updated = html.Div([
            html.I(className="fas fa-clock me-2"),
            f"Last Updated: {metadata.get('report_generated', 'N/A')} • ",
            html.I(className="fas fa-sync-alt me-2 ms-3"),
            f"Auto-refresh every 30s"
        ])
    else:
        last_updated = html.Div([
            html.I(className="fas fa-info-circle me-2"),
            "No analysis data available. Run the analysis pipeline first."
        ], className="alert alert-info")
    
    return json.dumps(data) if data else None, last_updated


@app.callback(
    Output('summary-cards', 'children'),
    Input('data-store', 'children')
)
def update_summary_cards(data_json):
    """Update summary cards"""
    if not data_json:
        return html.Div("Loading...", className="alert alert-info")
    
    data = json.loads(data_json)
    return create_summary_cards(data)


@app.callback(
    Output('model-metrics', 'children'),
    Input('data-store', 'children')
)
def update_model_metrics(data_json):
    """Update model metrics card"""
    if not data_json:
        return None
    
    data = json.loads(data_json)
    return create_model_metrics_card(data.get('model_metrics'))


@app.callback(
    Output('gap-distribution-chart', 'figure'),
    Input('data-store', 'children')
)
def update_gap_chart(data_json):
    """Update gap distribution chart"""
    if not data_json:
        return go.Figure().add_annotation(text="Loading...", showarrow=False)
    
    data = json.loads(data_json)
    return create_gap_distribution_chart(data.get('gaps', []))


@app.callback(
    Output('impact-score-chart', 'figure'),
    Input('data-store', 'children')
)
def update_impact_chart(data_json):
    """Update impact score chart"""
    if not data_json:
        return go.Figure().add_annotation(text="Loading...", showarrow=False)
    
    data = json.loads(data_json)
    return create_impact_score_chart(data.get('gaps', []))


@app.callback(
    Output('timeline-chart', 'figure'),
    Input('data-store', 'children')
)
def update_timeline_chart(data_json):
    """Update timeline chart"""
    if not data_json:
        return go.Figure().add_annotation(text="Loading...", showarrow=False)
    
    data = json.loads(data_json)
    return create_recommendations_timeline(data.get('recommendations', []))


@app.callback(
    Output('difficulty-chart', 'figure'),
    Input('data-store', 'children')
)
def update_difficulty_chart(data_json):
    """Update difficulty chart"""
    if not data_json:
        return go.Figure().add_annotation(text="Loading...", showarrow=False)
    
    data = json.loads(data_json)
    return create_difficulty_breakdown(data.get('recommendations', []))


@app.callback(
    Output('top-recommendations-table', 'children'),
    Input('data-store', 'children')
)
def update_recommendations_table(data_json):
    """Update recommendations table"""
    if not data_json:
        return None
    
    data = json.loads(data_json)
    return create_top_recommendations_table(data.get('recommendations', []))


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
