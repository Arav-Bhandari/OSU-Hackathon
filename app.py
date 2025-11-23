import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from src.services import data_service
import pandas as pd

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

server = app.server

colors = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'danger': '#D00000',
    'background': '#F8F9FA',
    'card': '#FFFFFF'
}

navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.Div([
                html.I(className="fas fa-hamburger me-2"),
                dbc.NavbarBrand("Fast Food Nutrition Dashboard", className="fs-3 fw-bold")
            ]), width="auto"),
        ], align="center", className="g-0 w-100"),
    ], fluid=True),
    color=colors['primary'],
    dark=True,
    className="mb-4"
)

stats = data_service.get_stats()
restaurant_scores = data_service.get_restaurant_scores()

stats_cards = dbc.Row([
    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4([html.I(className="fas fa-utensils me-2"), "Total Items"]),
            html.H2(f"{stats['total_items']:,}", className="text-primary")
        ])
    ], className="text-center shadow-sm"), md=3),
    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4([html.I(className="fas fa-store me-2"), "Restaurants"]),
            html.H2(f"{stats['total_restaurants']}", className="text-success")
        ])
    ], className="text-center shadow-sm"), md=3),
    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4([html.I(className="fas fa-fire me-2"), "Avg Calories"]),
            html.H2(f"{stats['avg_calories']:.0f}", className="text-warning")
        ])
    ], className="text-center shadow-sm"), md=3),
    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4([html.I(className="fas fa-drumstick-bite me-2"), "Avg Protein"]),
            html.H2(f"{stats['avg_protein']:.1f}g", className="text-info")
        ])
    ], className="text-center shadow-sm"), md=3),
], className="mb-4")

controls_panel = dbc.Card([
    dbc.CardHeader(html.H5([html.I(className="fas fa-sliders-h me-2"), "Filters & Controls"])),
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label("Select Restaurants:", className="fw-bold"),
                dcc.Dropdown(
                    id='restaurant-filter',
                    options=[{'label': 'All Restaurants', 'value': 'ALL'}] + 
                            [{'label': r, 'value': r} for r in data_service.get_restaurants()],
                    value='ALL',
                    multi=False,
                    className="mb-3"
                ),
            ], md=4),
            dbc.Col([
                html.Label("Calorie Range:", className="fw-bold"),
                dcc.RangeSlider(
                    id='calorie-slider',
                    min=0,
                    max=int(stats['max_calories']),
                    step=50,
                    value=[0, int(stats['max_calories'])],
                    marks={
                        0: '0',
                        500: '500',
                        1000: '1000',
                        1500: '1500',
                        2000: '2000+',
                    },
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], md=4),
            dbc.Col([
                html.Label("Nutrient Focus:", className="fw-bold"),
                dcc.Dropdown(
                    id='nutrient-selector',
                    options=[
                        {'label': 'Protein', 'value': 'protein'},
                        {'label': 'Sodium', 'value': 'sodium'},
                        {'label': 'Saturated Fat', 'value': 'saturated_fat'},
                        {'label': 'Sugars', 'value': 'sugars'},
                        {'label': 'Fiber', 'value': 'fiber'},
                    ],
                    value='protein',
                    className="mb-3"
                ),
            ], md=4),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(className="fas fa-sync me-2"), "Reset Filters"], 
                          id='reset-btn', color="secondary", size="sm", className="me-2"),
                dbc.Button([html.I(className="fas fa-download me-2"), "Export Data"], 
                          id='export-btn', color="primary", size="sm"),
            ], className="text-end"),
        ]),
    ])
], className="mb-4 shadow-sm")

tabs = dbc.Tabs([
    dbc.Tab(label="Overview Dashboard", tab_id="tab-overview", label_style={"cursor": "pointer"}),
    dbc.Tab(label="Restaurant Comparison", tab_id="tab-comparison", label_style={"cursor": "pointer"}),
    dbc.Tab(label="Item Analysis", tab_id="tab-items", label_style={"cursor": "pointer"}),
    dbc.Tab(label="Nutrition Explorer", tab_id="tab-explorer", label_style={"cursor": "pointer"}),
], id="tabs", active_tab="tab-overview", className="mb-3")

app.layout = dbc.Container([
    navbar,
    stats_cards,
    controls_panel,
    tabs,
    html.Div(id='tab-content'),
    dcc.Download(id="download-data"),
    dcc.Download(id="download-png"),
], fluid=True, style={'backgroundColor': colors['background'], 'minHeight': '100vh', 'paddingBottom': '2rem'})


@callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'active_tab'),
     Input('restaurant-filter', 'value'),
     Input('calorie-slider', 'value'),
     Input('nutrient-selector', 'value')]
)
def render_tab_content(active_tab, restaurant, calorie_range, nutrient):
    df = data_service.df.copy()
    
    if restaurant != 'ALL':
        df = df[df['restaurant'] == restaurant]
    
    df = df[(df['calories'] >= calorie_range[0]) & (df['calories'] <= calorie_range[1])]
    
    if active_tab == "tab-overview":
        return render_overview(df, nutrient)
    elif active_tab == "tab-comparison":
        return render_comparison(df)
    elif active_tab == "tab-items":
        return render_items(df, nutrient)
    elif active_tab == "tab-explorer":
        return render_explorer(df)
    
    return html.Div("Select a tab")


def render_overview(df, nutrient):
    fig_scatter = px.scatter(
        df, 
        x='calories', 
        y=nutrient,
        color='restaurant',
        size='protein',
        hover_data=['item'],
        title=f'Calories vs {nutrient.replace("_", " ").title()}',
        template='plotly_white',
        height=500
    )
    fig_scatter.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    rest_scores = pd.DataFrame(data_service.get_restaurant_scores())
    fig_scores = px.bar(
        rest_scores,
        x='restaurant',
        y='score',
        color='score',
        title='Restaurant Health Scores (Higher is Better)',
        template='plotly_white',
        height=400,
        color_continuous_scale='RdYlGn'
    )
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Nutrition Scatter Plot", className="fw-bold"),
                        dbc.Button([html.I(className="fas fa-download")], 
                                  id='download-scatter-btn', size="sm", 
                                  color="link", className="float-end")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='scatter-plot', figure=fig_scatter)
                    ])
                ], className="shadow-sm mb-3")
            ], md=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Restaurant Rankings", className="fw-bold"),
                        dbc.Button([html.I(className="fas fa-download")], 
                                  id='download-bar-btn', size="sm", 
                                  color="link", className="float-end")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='bar-chart', figure=fig_scores)
                    ])
                ], className="shadow-sm")
            ], md=12),
        ])
    ], fluid=True)


def render_comparison(df):
    rest_stats = df.groupby('restaurant').agg({
        'calories': 'mean',
        'sodium': 'mean',
        'saturated_fat': 'mean',
        'protein': 'mean',
        'fiber': 'mean',
        'sugars': 'mean'
    }).reset_index()
    
    fig_radar = go.Figure()
    
    for _, row in rest_stats.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[
                row['protein'] / rest_stats['protein'].max() * 100,
                row['fiber'] / rest_stats['fiber'].max() * 100,
                100 - (row['sodium'] / rest_stats['sodium'].max() * 100),
                100 - (row['saturated_fat'] / rest_stats['saturated_fat'].max() * 100),
                100 - (row['sugars'] / rest_stats['sugars'].max() * 100),
            ],
            theta=['Protein', 'Fiber', 'Low Sodium', 'Low Sat Fat', 'Low Sugar'],
            fill='toself',
            name=row['restaurant']
        ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Restaurant Nutrition Profile Comparison",
        height=600,
        template='plotly_white'
    )
    
    fig_box = px.box(
        df,
        x='restaurant',
        y='calories',
        color='restaurant',
        title='Calorie Distribution by Restaurant',
        template='plotly_white',
        height=400
    )
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Nutrition Profile Radar", className="fw-bold"),
                        dbc.Button([html.I(className="fas fa-download")], 
                                  id='download-radar-btn', size="sm", 
                                  color="link", className="float-end")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='radar-chart', figure=fig_radar)
                    ])
                ], className="shadow-sm mb-3")
            ], md=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Calorie Distribution"),
                    dbc.CardBody([
                        dcc.Graph(figure=fig_box)
                    ])
                ], className="shadow-sm")
            ], md=12),
        ])
    ], fluid=True)


def render_items(df, nutrient):
    df_sorted = df.nsmallest(20, nutrient) if nutrient in ['sodium', 'saturated_fat', 'sugars'] else df.nlargest(20, nutrient)
    
    fig_items = px.bar(
        df_sorted,
        x=nutrient,
        y='item',
        color='restaurant',
        orientation='h',
        title=f'Top 20 Items by {nutrient.replace("_", " ").title()}',
        template='plotly_white',
        height=800
    )
    fig_items.update_layout(yaxis={'categoryorder': 'total ascending'})
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Item Rankings", className="fw-bold"),
                        dbc.Button([html.I(className="fas fa-download")], 
                                  id='download-items-btn', size="sm", 
                                  color="link", className="float-end")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='items-chart', figure=fig_items)
                    ])
                ], className="shadow-sm")
            ], md=12),
        ])
    ], fluid=True)


def render_explorer(df):
    df_macro = df.copy()
    df_macro['fat_cal'] = df_macro['saturated_fat'] * 9
    df_macro['carb_cal'] = df_macro['sugars'] * 4
    df_macro['prot_cal'] = df_macro['protein'] * 4
    total = df_macro['fat_cal'] + df_macro['carb_cal'] + df_macro['prot_cal']
    total = total.replace(0, 1)
    
    df_macro['% Fat'] = df_macro['fat_cal'] / total
    df_macro['% Carbs'] = df_macro['carb_cal'] / total
    df_macro['% Protein'] = df_macro['prot_cal'] / total
    
    fig_ternary = px.scatter_ternary(
        df_macro,
        a='% Fat',
        b='% Carbs',
        c='% Protein',
        color='calories',
        size='calories',
        hover_data=['item', 'restaurant'],
        title='Macronutrient Distribution Triangle',
        color_continuous_scale='Reds',
        template='plotly_white',
        height=700
    )
    
    correlation = df[['calories', 'sodium', 'saturated_fat', 'protein', 'fiber', 'sugars']].corr()
    fig_heatmap = px.imshow(
        correlation,
        text_auto='.2f',
        aspect='auto',
        title='Nutrient Correlation Matrix',
        color_continuous_scale='RdBu_r',
        template='plotly_white',
        height=500
    )
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Span("Macronutrient Ternary Plot", className="fw-bold"),
                        dbc.Button([html.I(className="fas fa-download")], 
                                  id='download-ternary-btn', size="sm", 
                                  color="link", className="float-end")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(id='ternary-chart', figure=fig_ternary)
                    ])
                ], className="shadow-sm mb-3")
            ], md=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Correlation Heatmap"),
                    dbc.CardBody([
                        dcc.Graph(figure=fig_heatmap)
                    ])
                ], className="shadow-sm")
            ], md=12),
        ])
    ], fluid=True)


@callback(
    [Output('restaurant-filter', 'value'),
     Output('calorie-slider', 'value'),
     Output('nutrient-selector', 'value')],
    Input('reset-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    return 'ALL', [0, int(stats['max_calories'])], 'protein'


@callback(
    Output("download-data", "data"),
    Input("export-btn", "n_clicks"),
    [State('restaurant-filter', 'value'),
     State('calorie-slider', 'value')],
    prevent_initial_call=True
)
def export_data(n_clicks, restaurant, calorie_range):
    df = data_service.df.copy()
    if restaurant != 'ALL':
        df = df[df['restaurant'] == restaurant]
    df = df[(df['calories'] >= calorie_range[0]) & (df['calories'] <= calorie_range[1])]
    return dcc.send_data_frame(df.to_csv, "nutrition_data.csv", index=False)


@callback(
    Output("download-png", "data"),
    [Input('download-scatter-btn', 'n_clicks'),
     Input('download-bar-btn', 'n_clicks'),
     Input('download-radar-btn', 'n_clicks'),
     Input('download-items-btn', 'n_clicks'),
     Input('download-ternary-btn', 'n_clicks')],
    [State('scatter-plot', 'figure'),
     State('bar-chart', 'figure'),
     State('radar-chart', 'figure'),
     State('items-chart', 'figure'),
     State('ternary-chart', 'figure')],
    prevent_initial_call=True
)
def export_graph_png(scatter_clicks, bar_clicks, radar_clicks, items_clicks, ternary_clicks,
                     scatter_fig, bar_fig, radar_fig, items_fig, ternary_fig):
    if not ctx.triggered_id:
        return None
    
    figure_map = {
        'download-scatter-btn': (scatter_fig, 'nutrition_scatter.png'),
        'download-bar-btn': (bar_fig, 'restaurant_rankings.png'),
        'download-radar-btn': (radar_fig, 'nutrition_radar.png'),
        'download-items-btn': (items_fig, 'item_rankings.png'),
        'download-ternary-btn': (ternary_fig, 'macronutrient_ternary.png')
    }
    
    if ctx.triggered_id in figure_map:
        fig_data, filename = figure_map[ctx.triggered_id]
        if fig_data:
            fig = go.Figure(fig_data)
            img_bytes = pio.to_image(fig, format='png', width=1200, height=800, engine='kaleido')
            return dcc.send_bytes(img_bytes, filename)
    
    return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
