# Fast Food Nutrition Dashboard

## Overview
An interactive web dashboard for analyzing and visualizing nutritional data from fast food restaurants. Built with Python, Plotly Dash, and modern Bootstrap UI components. Users can filter data, compare restaurants, explore nutrition profiles, and export visualizations as PNG images.

## Project Structure
- `app.py` - Main Dash application with all UI components and callbacks
- `data/` - Contains the fast food nutrition dataset (fastfood.csv with 515 items from 8 restaurants)
- `src/` - Source code modules
  - `services.py` - DataService singleton for data loading and caching
  - `analyzer.py` - Core analysis logic with quartic regression algorithms
  - `data_loader.py` - CSV data loading utilities (legacy)
  - `plotter.py` - Visualization utilities (legacy)
  - `graph_exports.py` - PNG export functionality module
- `main.py` - CLI script for basic data loading (legacy)

## Key Features
### Interactive Dashboard
- **Overview Tab**: Scatter plots showing calories vs nutrients, restaurant health score rankings
- **Restaurant Comparison Tab**: Radar charts comparing nutrition profiles, box plots for calorie distributions
- **Item Analysis Tab**: Top 20 items ranked by selected nutrients
- **Nutrition Explorer Tab**: Ternary diagrams for macronutrient distribution, correlation heatmaps

### Interactive Controls
- Restaurant filter dropdown (all or specific restaurant)
- Calorie range slider (0 to 2400+)
- Nutrient focus selector (protein, sodium, saturated fat, sugars, fiber)
- Reset filters button
- Export data as CSV button

### Visualization Features
- Real-time chart updates based on filter selections
- Multiple chart types: scatter, bar, radar, box, ternary, heatmap
- Color-coded by restaurant or nutrient values
- Hover tooltips with detailed item information
- PNG export functionality for all graphs

### Data Analysis
- Quartic regression scoring algorithm for restaurant health rankings
- Macronutrient distribution analysis
- Correlation analysis between nutrients
- Statistical aggregations by restaurant

## Dependencies
- Python 3.11
- dash - Web application framework
- dash-bootstrap-components - Modern UI components
- plotly - Interactive visualizations
- pandas - Data manipulation
- kaleido - PNG image export
- matplotlib - Legacy plotting support

## Running the Dashboard
The dashboard runs on port 5000 and is accessible via the web browser:
```bash
python app.py
```
Server automatically binds to 0.0.0.0:5000 for Replit compatibility.

## Recent Changes
- 2025-11-23: Complete refactor from CLI analysis tool to interactive web dashboard
  - Built full-featured Dash application with Bootstrap UI
  - Implemented 4 distinct analysis tabs with multiple visualization types
  - Added interactive filters (restaurant, calorie range, nutrient focus)
  - Integrated PNG export for all graphs using kaleido
  - Created DataService singleton with caching for performance
  - Consolidated duplicate analysis code
  - Removed legacy CLI workflow
  - Modern, responsive UI with Font Awesome icons
  - Data export to CSV functionality

## User Preferences
- Prefers modern, clean UI
- Wants interactive controls with automatic graph updates
- Needs PNG export functionality for all visualizations
- Wants comprehensive analysis with multiple formulas and metrics

## Architecture Notes
- Single-page Dash application with tab-based navigation
- DataService uses singleton pattern with LRU caching for performance
- All visualizations generated server-side with Plotly
- Callbacks handle real-time filter updates
- Bootstrap grid system for responsive layout
- Quartic regression analysis from original codebase preserved
- CSV data loaded once on startup and cached in memory
