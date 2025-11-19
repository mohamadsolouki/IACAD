"""
Application Settings and Configuration
Central configuration file for all app-wide settings
"""

from pathlib import Path

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

APP_TITLE = "UAE Donations Analytics Dashboard"
APP_ICON = "📊"
PAGE_TITLE = "UAE Donations Analytics"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# ============================================================================
# DATA SETTINGS
# ============================================================================

DATA_DIR = Path('data')
DATA_PATH = DATA_DIR / 'General_Donation_Processed.csv'
RAW_DATA_PATH = DATA_DIR / 'General_Donation.csv'

# ============================================================================
# CHART SETTINGS
# ============================================================================

DEFAULT_CHART_HEIGHT = 450
HEATMAP_HEIGHT = 500
COMPARISON_CHART_HEIGHT = 500
TOP_N_CATEGORIES = 10
TOP_N_DONORS = 10

# ============================================================================
# CACHING SETTINGS
# ============================================================================

CACHE_TTL = 3600  # 1 hour in seconds
DATA_CACHE_TTL = 1800  # 30 minutes in seconds

# ============================================================================
# DATE FORMATS
# ============================================================================

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATE_FORMAT = "%B %d, %Y"

# ============================================================================
# FEATURE FLAGS
# ============================================================================

ENABLE_RAMADAN_ANALYSIS = True
ENABLE_HIJRI_CALENDAR = True
ENABLE_DONOR_ANALYSIS = True
ENABLE_COMPARISON_TOOL = True
ENABLE_DATA_EXPORT = True
