# src/plotter.py
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data

def ternary_plot(df):
    # Calculate macronutrient calories
    df = df.copy()
    df['fat_cal'] = df['total_fat'] * 9
    df['carb_cal'] = df['total_carb'] * 4
    df['prot_cal'] = df['protein'] * 4
    total = df['fat_cal'] + df['carb_cal'] + df['prot_cal']

    df['% Fat'] = df['fat_cal'] / total
    df['% Carbs'] = df['carb_cal'] / total
    df['% Protein'] = df['prot_cal'] / total

    fig = go.Figure()

    # Contour background (density of calories)
    fig.add_trace(go.Scatterternary({
        'mode': 'markers',
        'a': df['% Fat'],
        'b': df['% Carbs'],
        'c': df['% Protein'],
        'marker': {
            'size': 4,
            'opacity': 0.6,
            'color': df['calories'],
            'colorscale': 'Reds',
            'colorbar': dict(title="Calories"),
            'showscale': True,
        },
        'text': df['item'] + " (" + df['restaurant'] + ")",
        'hoverinfo': 'text+x+y+z'
    }))

    fig.update_layout(
        title="Fast Food Macronutrient Triangle<br>"
              "<sub>Color = Total Calories | Hover for item details</sub>",
        ternary=dict(
            sum=1,
            aaxis=dict(title="Fat %", min=0),
            baxis=dict(title="Carbs %", min=0),
            caxis=dict(title="Protein %", min=0),
        ),
        width=900,
        height=800,
    )
    fig.show()

def worst_items_table(df, top_n=20):
    df = df.copy()
    df['unhealthy_score'] = (
        df['calories'] * 0.4 +
        df['sodium'] * 0.0012 +
        df['sat_fat'] * 10 +
        df['sugar'] * 5 -
        df['protein'] * 2
    )
    worst = df.nlargest(top_n, 'unhealthy_score')[[
        'restaurant', 'item', 'calories', 'sodium', 'sat_fat', 'sugar', 'protein'
    ]].round(1)
    print("\nTOP 20 MOST UNHEALTHY FAST FOOD ITEMS:")
    print(worst.to_string(index=False))

def main():
    df = load_data()

    print("\nGenerating ternary plot...")
    ternary_plot(df)

    print("\nCalculating worst offenders...")
    worst_items_table(df, top_n=15)

    # Bonus: quick scatter of sodium vs calories
    fig = px.scatter(
        df, x='calories', y='sodium',
        color='restaurant', size='sugar',
        hover_data=['item'],
        title="The Sodium-Calorie Death Zone",
        labels={'calories': 'Calories', 'sodium': 'Sodium (mg)'}
    )
    fig.update_layout(height=700)
    fig.show()

if __name__ == "__main__":
    main()