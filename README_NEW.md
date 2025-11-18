# 🎯 UAE Donations Analytics Dashboard

A comprehensive Business Intelligence (BI) dashboard for analyzing donation trends and patterns in the UAE with **Hijri calendar integration**, **Islamic events tracking**, and **dark mode support**.

## ✨ Key Features

### 🌓 Modern UI/UX
- **Dark Mode Support** - Toggle between light and dark themes
- **Responsive Design** - Works on desktop and mobile
- **Interactive Charts** - 9+ dynamic visualizations
- **Real-time Filtering** - Advanced filter controls

### 🌙 Islamic Calendar Integration
- **Ramadan Analysis** - Automatic detection and analysis of Ramadan periods
- **Hijri Calendar** - All dates mapped to Islamic calendar
- **Islamic Events** - Detects Eid al-Fitr, Eid al-Adha, Hajj, Ashura, and more
- **Period Breakdown** - Ramadan divided into First/Middle/Last 10 days

### 🌍 Multilingual Support
- **English Translations** - Arabic donation types automatically translated
- **Bilingual Data** - Both Arabic and English labels available

### 📊 Comprehensive Analytics
- Time series with Ramadan highlighting
- Ramadan vs Non-Ramadan comparison
- Donations by Islamic events
- Hijri month analysis
- Category distribution (English)
- Amount distribution
- Quarterly trends
- Day/Month heatmaps
- Hourly patterns

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Preprocess the Data

**⚠️ IMPORTANT:** Before running the dashboard, preprocess the data first:

```bash
python preprocess_data.py
```

This script will:
- ✅ Convert all Gregorian dates to Hijri calendar
- ✅ Identify Ramadan periods (First/Middle/Last 10 days)
- ✅ Detect Islamic events (Eid, Hajj, Ashura, Mawlid)
- ✅ Translate donation types from Arabic to English
- ✅ Create processed dataset: `data/General_Donation_Processed.csv`

**⏱️ Processing Time:** 5-15 minutes (depends on data size and internet speed)

### 3. Run the Dashboard

```bash
python dashboard_app.py
```

🌐 Dashboard available at: **http://localhost:8050**

## 📁 Project Structure

```
IACAD/
├── data/
│   ├── General_Donation.csv              # Raw donation data
│   └── General_Donation_Processed.csv    # Preprocessed data (auto-generated)
├── dashboard_app.py                       # Main dashboard application
├── preprocess_data.py                     # Data preprocessing script
├── requirements.txt                       # Python dependencies
└── README.md                              # Documentation
```

## 📊 Dashboard Components

### KPI Cards (5 Cards)
1. **Total Donations** - Count of all donations
2. **Total Amount** - Sum with month-over-month growth
3. **Average Donation** - Mean donation amount
4. **Ramadan Donations** - Count and percentage
5. **Ramadan Amount** - Total during Ramadan

### Visualizations (9 Charts)

#### 1. Time Series Chart
- Daily donation trends
- **Ramadan periods highlighted in gold**
- Regular days in blue
- Interactive hover details

#### 2. Ramadan Impact Analysis
- Side-by-side comparison
- Total Amount | Average Donation | Count
- Ramadan vs Non-Ramadan metrics

#### 3. Islamic Events Chart
- Horizontal bar chart
- Donations during specific events
- Eid al-Fitr, Eid al-Adha, Hajj, etc.

#### 4. Hijri Months Chart
- Donations by Islamic calendar month
- **Ramadan highlighted**
- All 12 Hijri months

#### 5. Top Donation Categories
- Top 10 categories by amount
- **English translations**
- Horizontal bars with amounts

#### 6. Distribution Histogram
- Donation amount distribution
- Frequency analysis
- Statistical insights

#### 7. Quarterly Comparison
- Year + Quarter breakdown
- Trend analysis
- Growth indicators

#### 8. Day/Month Heatmap
- Weekday vs Month patterns
- Color-coded intensity
- Pattern identification

#### 9. Hourly Patterns
- Amount by hour (top)
- Count by hour (bottom)
- Peak time identification

### Filters & Controls

#### Date Range Filter
- Start and end date pickers
- Narrow down time periods

#### Donation Type Filter
- Multi-select dropdown
- **English category names**
- Filter by specific types

#### Amount Range Slider
- Min/Max amount filter
- Dynamic range adjustment

#### Ramadan Filter
- Checkbox to show only Ramadan donations
- Quick analysis tool

#### Action Buttons
- **Apply Filters** - Execute filter changes
- **Reset Filters** - Clear all filters

#### Theme Toggle
- 🌙 Moon icon - Switch to dark mode
- ☀️ Sun icon - Switch to light mode

## 🔧 Technical Stack

### Backend
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computations
- **SciPy** - Statistical functions

### Frontend
- **Dash** - Web framework
- **Plotly** - Interactive charts
- **Dash Bootstrap Components** - UI components
- **Font Awesome** - Icons

### Data Processing
- **Hijri Converter** - Gregorian ↔ Hijri conversion
- **Deep Translator** - Arabic → English translation
- **Google Translator API** - Translation service

## 📝 Data Processing Details

### Preprocessing Script Output

The `preprocess_data.py` script adds these columns:

#### Gregorian Calendar
- `year`, `month`, `quarter`, `day`, `weekday`, `week`, `hour`, `date`
- `month_name` - Full month name (e.g., "January")

#### Hijri Calendar
- `hijri_year` - Islamic year
- `hijri_month` - Month number (1-12)
- `hijri_day` - Day of month
- `hijri_month_name` - Month name (e.g., "Ramadan")

#### Islamic Events
- `is_ramadan` - Boolean flag
- `ramadan_period` - First/Middle/Last 10 days
- `islamic_event` - Event name or None

#### Translations
- `donationtype_en` - English translation of donation type

### Sample Processing Output

```
==================================================
UAE DONATIONS DATA PREPROCESSING
==================================================

[1/5] Loading raw data...
   ✓ Loaded 92,629 records

[2/5] Processing dates and amounts...
   ✓ Removed 0 invalid records
   ✓ 92,629 valid records remaining

[3/5] Extracting time dimensions...
   ✓ Extracted Gregorian calendar dimensions

[4/5] Adding Hijri calendar information...
   ✓ Processed Hijri dates for all 92,629 records
   ✓ Identified 8,547 Ramadan donations (9.2%)

[5/5] Translating donation types to English...
   ✓ Completed translation of 47 unique types

[6/6] Saving processed data...
   ✓ Saved 92,629 processed records

==================================================
PROCESSING SUMMARY
==================================================

Total Records:           92,629
Date Range:              2025-01-01 to 2025-11-18
Total Amount:            AED 4,523,156.00
Average Donation:        AED 48.82

Ramadan Donations:       8,547 (9.2%)
Ramadan Amount:          AED 512,345.00
Non-Ramadan Amount:      AED 4,010,811.00

Unique Donation Types:   47
Unique Donors:           15,234

Islamic Events Identified:
  - Ramadan (Last 10 Days): 3,245 donations
  - Ramadan (First 10 Days): 2,891 donations
  - Ramadan (Middle 10 Days): 2,411 donations
  - Eid al-Fitr: 567 donations
  - Hajj & Eid al-Adha: 234 donations

✓ Processing completed successfully!
```

## 🎨 Theme Support

### Light Theme
- Modern blue and green color palette
- White backgrounds
- High contrast for readability
- Professional appearance

### Dark Theme
- Deep slate background
- Neon accent colors
- Reduced eye strain
- Modern aesthetic

## 🔍 Usage Tips

1. **First Time Setup**
   - Always run `preprocess_data.py` before `dashboard_app.py`
   - Preprocessing is a one-time operation (or when data updates)

2. **Filtering**
   - Apply multiple filters together for detailed analysis
   - Use Ramadan filter for quick Islamic calendar insights
   - Reset filters to return to full dataset

3. **Theme Switching**
   - Click moon/sun icon in navbar
   - All charts update automatically
   - Preference not saved (resets on refresh)

4. **Chart Interactions**
   - Hover over charts for detailed tooltips
   - Click legend items to show/hide data
   - Zoom and pan on time series charts

## 📦 Dependencies

```
pandas>=2.0.0
plotly>=5.14.0
dash>=2.14.0
dash-bootstrap-components>=1.5.0
numpy>=1.24.0
scipy>=1.11.0
hijri-converter>=2.3.0
deep-translator>=1.11.0
```

## ⚠️ Important Notes

1. **Preprocessing Required**
   - Dashboard requires preprocessed data to function fully
   - Will fall back to raw data with limited features
   - Always preprocess for best experience

2. **Internet Connection**
   - Required during preprocessing for translations
   - Dashboard itself works offline after preprocessing

3. **Translation Caching**
   - Common donation types are pre-cached
   - Unique types are translated via Google API
   - Cache stored in memory during preprocessing

4. **Data Privacy**
   - All processing happens locally
   - Only translation API calls go online
   - No donation data is sent externally

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'hijri_converter'"
```bash
pip install hijri-converter deep-translator
```

### "Processed data file not found"
```bash
python preprocess_data.py
```

### "Translation failed"
- Check internet connection
- Script will retry automatically
- Falls back to original text if needed

### Dashboard loads but no Ramadan data
- Ensure preprocessing completed successfully
- Check console for error messages
- Verify processed CSV file exists

## 📄 License

This project is for educational and analytical purposes.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional Islamic calendar features
- More visualization types
- Export functionality
- Advanced statistical analysis

---

**Made with ❤️ for UAE Donation Analytics**
