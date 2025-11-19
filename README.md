# UAE Donations Analytics Dashboard

A comprehensive Streamlit application for analyzing donation data with interactive visualizations, Ramadan analysis, temporal patterns, and donor insights.

## 🌟 Features

- **📊 Overview Dashboard**: Key metrics, trends, and category analysis
- **🌙 Ramadan Analysis**: Special focus on Ramadan donation patterns and Islamic calendar events
- **⏰ Temporal Analysis**: Hourly, daily, weekly, and monthly donation patterns
- **👥 Donor Analysis**: Donor segmentation, behavior analysis, and retention metrics
- **🔄 Comparison Tool**: Compare donations between different time periods

## 📁 Project Structure

```
IACAD/
├── app.py                          # Main Streamlit application
├── preprocess_data.py              # Data preprocessing script
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── data/
│   ├── General_Donation.csv        # Raw data
│   └── General_Donation_Processed.csv  # Processed data
└── src/
    ├── config/                     # Configuration files
    │   ├── settings.py             # App settings
    │   └── theme.py                # Theme configuration
    ├── services/                   # Business logic
    │   ├── data_service.py         # Data loading and processing
    │   └── metrics_service.py      # KPI calculations
    ├── components/                 # Reusable UI components
    │   ├── kpi_cards.py            # KPI display components
    │   ├── time_series_charts.py   # Time series visualizations
    │   ├── ramadan_charts.py       # Ramadan analysis charts
    │   ├── category_charts.py      # Category visualizations
    │   ├── temporal_charts.py      # Temporal pattern charts
    │   └── donor_charts.py         # Donor analysis charts
    └── pages/                      # Page modules
        ├── overview.py             # Overview page
        ├── ramadan.py              # Ramadan analysis page
        ├── temporal.py             # Temporal analysis page
        ├── donors.py               # Donor analysis page
        └── comparison.py           # Comparison tool page
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository** (or navigate to the project directory)
   ```bash
   cd IACAD
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Data Preparation

Before running the app, preprocess your data to add Hijri calendar information and translations:

```bash
python preprocess_data.py
```

This will create `data/General_Donation_Processed.csv` with:
- Hijri calendar dates
- Ramadan detection
- Islamic event identification
- English translations of donation types

### Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## 📊 Usage

### Navigation

Use the sidebar to navigate between different sections:

1. **Overview**: Get a comprehensive view of all donations
2. **Ramadan Analysis**: Explore Ramadan-specific patterns
3. **Temporal Analysis**: Analyze patterns over time
4. **Donor Analysis**: Understand donor behavior
5. **Comparison Tool**: Compare different time periods

### Features

- **Dark Mode**: Toggle between light and dark themes
- **Interactive Charts**: Hover, zoom, and pan on all visualizations
- **Data Export**: Download filtered data as CSV
- **Responsive Design**: Works on desktop and mobile devices

## 🌐 Deployment

### Deploy to Streamlit Community Cloud (Free)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Streamlit app ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository, branch, and `app.py`
   - Click "Deploy"

Your app will be live in ~2 minutes! 🎉

### Other Deployment Options

#### Render

1. Create a `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Deploy via Render dashboard connecting to your GitHub repo

#### Hugging Face Spaces

1. Create a new Space on huggingface.co
2. Upload your code
3. The app will auto-deploy

#### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t donations-dashboard .
docker run -p 8501:8501 donations-dashboard
```

## 🔧 Configuration

### Settings

Edit `src/config/settings.py` to customize:
- Data paths
- Chart heights
- Cache TTL
- Feature flags

### Theme

Edit `src/config/theme.py` to customize:
- Color schemes
- Chart colors
- Light/dark themes

### Streamlit Config

Edit `.streamlit/config.toml` to configure:
- Server settings
- Theme colors
- Upload limits

## 📦 Adding New Features

The modular architecture makes it easy to extend:

### Add a New Page

1. Create a new file in `src/pages/`, e.g., `src/pages/my_page.py`:
   ```python
   import streamlit as st
   
   def render_my_page(df, dark_mode=False):
       st.title("My New Page")
       # Your page code here
   ```

2. Import in `src/pages/__init__.py`:
   ```python
   from .my_page import render_my_page
   ```

3. Add to navigation in `app.py`:
   ```python
   elif page == "My Page":
       render_my_page(df, dark_mode)
   ```

### Add a New Chart

1. Create the chart function in the appropriate component file or create a new one
2. Import and use in your page module

### Add New Metrics

Add calculation functions to `src/services/metrics_service.py`

## 🐛 Troubleshooting

**Data not loading?**
- Ensure `data/General_Donation_Processed.csv` exists
- Run `python preprocess_data.py` to generate it
- Check file paths in `src/config/settings.py`

**Charts not displaying?**
- Clear Streamlit cache: Click "Clear cache" in the hamburger menu
- Or delete `.streamlit/cache/` folder

**Import errors?**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

## 📝 License

This project is for internal use by IACAD.

## 👥 Support

For questions or issues, please contact the development team.

---

**Built with ❤️ using Streamlit**
