import plotly.graph_objects as go
from dash import Output, Input, callback, State
import plotly.io as pio

def register_export_callbacks():
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
    def export_graph_as_png(scatter_clicks, bar_clicks, radar_clicks, items_clicks, 
                           ternary_clicks, scatter_fig, bar_fig, radar_fig, items_fig, ternary_fig):
        from dash import ctx
        
        if not ctx.triggered_id:
            return None
        
        button_id = ctx.triggered_id
        figure_map = {
            'download-scatter-btn': (scatter_fig, 'nutrition_scatter.png'),
            'download-bar-btn': (bar_fig, 'restaurant_rankings.png'),
            'download-radar-btn': (radar_fig, 'nutrition_radar.png'),
            'download-items-btn': (items_fig, 'item_rankings.png'),
            'download-ternary-btn': (ternary_fig, 'macronutrient_ternary.png')
        }
        
        if button_id in figure_map:
            fig_data, filename = figure_map[button_id]
            if fig_data:
                fig = go.Figure(fig_data)
                img_bytes = pio.to_image(fig, format='png', width=1200, height=800, engine='kaleido')
                return dict(content=img_bytes, filename=filename, type='image/png', base64=True)
        
        return None
