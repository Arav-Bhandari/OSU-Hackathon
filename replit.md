# Fast Food Nutrition Analysis

## Overview
This is a Python data analysis project that analyzes nutritional data from various fast food restaurants. It performs quartic regression analysis to score restaurants based on their nutritional profiles.

## Project Structure
- `data/` - Contains the fast food nutrition dataset (fastfood.csv)
- `src/` - Source code modules
  - `data_loader.py` - Loads and parses the CSV data using pandas
  - `analyzer.py.py` - Core analysis logic with quartic fitting algorithms
  - `plotter.py` - Visualization functions using plotly and matplotlib
  - `reporter.py` - Reporting utilities (currently empty)
- `utils/` - Utility functions
- `main.py` - Main entry point that loads data
- `lovable.py` - Contains the analysis algorithms and data structures

## Key Features
- Loads fast food nutritional data from CSV
- Performs quartic regression analysis on nutrient ratios
- Scores restaurants based on good vs bad nutrients
- Supports visualization with plotly (ternary plots, scatter plots)

## Dependencies
- Python 3.11
- pandas - Data manipulation
- plotly - Interactive visualizations
- matplotlib - Static plotting

## Recent Changes
- 2025-11-23: Imported from GitHub and configured for Replit environment
  - Installed Python 3.11
  - Added Python dependencies (pandas, plotly, matplotlib)
  - Updated .gitignore for Python
  - Verified data loading functionality

## User Preferences
None specified yet.

## Architecture Notes
- The project has duplicate analysis code in both `lovable.py` and `src/analyzer.py.py` (identical content)
- Data loader uses pandas with custom regex parsing for handling quoted CSV fields
- Analysis uses quartic polynomial fitting for nutrient scoring
