# 🎯 UAE Donations Analytics Dashboard

A comprehensive Business Intelligence (BI) dashboard for analyzing donation trends and patterns in the UAE. This interactive dashboard provides deep insights into donation data with advanced filtering, drill-down capabilities, and statistical analysis.

## 📊 Features

### Interactive Visualizations
- **📈 Trend Analysis**: Daily donation trends with 7-day moving averages
- **🥧 Donation Type Distribution**: Top 10 donation types by amount
- **📊 Comparative Analysis**: Distribution of donations by type
- **🔥 Heat Maps**: Time-based patterns (hour vs. weekday)
- **📅 Seasonality Analysis**: Monthly patterns across years
- **💰 Amount Distribution**: Histogram and box plots for donation amounts
- **📆 Monthly Comparisons**: Year-over-year monthly performance
- **🎯 Cumulative Growth**: Track total growth over time
- **🔍 Top Performers**: Identify highest-performing donation categories

### Key Performance Indicators (KPIs)
- Total number of donations
- Total amount donated (AED)
- Average donation amount
- Number of unique donation types
- Percentage comparisons against overall data

### Advanced Filtering & Slicers
- **Donation Type Filter**: Select one or multiple donation types
- **Year Filter**: Filter by specific years
- **Quarter Filter**: Analyze quarterly data (Q1-Q4)
- **Month Filter**: Focus on specific months
- **Amount Range Slider**: Filter donations by amount range

### Statistical Analysis
- Comprehensive statistical summary table
- Mean, median, standard deviation
- Quartile analysis (Q1, Q3)
- Skewness and kurtosis metrics
- Min/max values

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd d:\git\IACAD
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Dashboard

1. **Start the dashboard application**
   ```bash
   python dashboard_app.py
   ```

2. **Access the dashboard**
   - Open your web browser
   - Navigate to: `http://localhost:8050`
   - The dashboard will load automatically

3. **Stop the dashboard**
   - Press `Ctrl+C` in the terminal

## 📁 Project Structure

```
IACAD/
│
├── data/
│   └── General_Donation.csv          # Donation dataset
│
├── dashboard_app.py                  # Main dashboard application
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## 🎨 Dashboard Usage Guide

### 1. Filters & Slicers
Located at the top of the dashboard, use these to drill down into your data:
- **Multi-select dropdowns**: Hold Ctrl/Cmd to select multiple options
- **Range slider**: Drag handles to adjust amount range
- **Reset filters**: Select "All" options to view complete data

### 2. KPI Cards
Four cards display key metrics that update based on your filters:
- **Total Donations**: Count of filtered donations with percentage of total
- **Total Amount**: Sum of donation amounts with percentage of total
- **Average Donation**: Mean donation amount with comparison to overall average
- **Unique Types**: Number of unique donation categories in filtered data

### 3. Interactive Charts
All charts are interactive:
- **Hover**: View detailed tooltips with exact values
- **Zoom**: Click and drag to zoom into specific areas
- **Pan**: Shift + drag to pan across the chart
- **Reset**: Double-click to reset zoom
- **Download**: Use the camera icon to save chart images

### 4. Drill-Down Capabilities
- Filter by donation type to see specific category trends
- Select year → quarter → month for temporal drill-down
- Adjust amount range to focus on specific donation sizes
- Combine multiple filters for granular analysis

## 📈 Analytics Capabilities

### Trend Analysis
- Identify growth patterns over time
- Spot seasonal variations
- Detect anomalies and outliers
- Compare different time periods

### Performance Metrics
- Top-performing donation categories
- Time-of-day and day-of-week patterns
- Monthly and quarterly comparisons
- Year-over-year growth analysis

### Statistical Insights
- Distribution analysis (normal, skewed)
- Variability measurements
- Quartile and percentile analysis
- Correlation between time and donation patterns

## 🛠️ Customization

### Modifying the Dashboard

**Add new visualizations**: Edit `dashboard_app.py` and add new chart components

**Change colors**: Modify the `colors` dictionary in the code

**Adjust filters**: Add or remove filter components in the layout section

**Update data source**: Change the CSV file path in the `load_data()` function

### Performance Optimization

For large datasets (>100K records):
- Consider aggregating data before visualization
- Implement data caching with `@cache` decorator
- Use server-side filtering for very large datasets

## 📊 Data Format

The dashboard expects a CSV file with the following columns:
- `amount`: Numeric donation amount
- `donationdate`: Date and time of donation (YYYY-MM-DD HH:MM:SS.mmm)
- `donationtype`: Category/type of donation (in Arabic or English)
- `id`: Unique identifier for each donation

## 🔧 Troubleshooting

### Dashboard won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8050 is available
- Verify Python version: `python --version`

### Charts not displaying
- Clear browser cache
- Check browser console for errors (F12)
- Ensure data file path is correct

### Slow performance
- Reduce the amount range filter
- Select specific donation types instead of "All"
- Limit date range using year/month filters

## 📝 Technical Details

### Technology Stack
- **Backend**: Python 3.12+
- **Web Framework**: Dash (Flask-based)
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly
- **UI Components**: Dash Bootstrap Components
- **Statistics**: SciPy

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge

## 📄 License

This project is created for internal analytics purposes.

## 🤝 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the code comments in `dashboard_app.py`
3. Ensure your data format matches the expected structure

## 🎉 Features Highlights

✅ **10+ Interactive Visualizations**  
✅ **Real-time Filtering & Updates**  
✅ **Comprehensive Statistical Analysis**  
✅ **Mobile-Responsive Design**  
✅ **Export Charts as Images**  
✅ **Multi-dimensional Drill-Down**  
✅ **Time-Series Analysis**  
✅ **Heatmap Visualizations**  
✅ **KPI Tracking**  
✅ **Professional UI/UX**

---

**Developed with ❤️ for UAE Donations Analytics**
