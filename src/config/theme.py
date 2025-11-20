"""
Theme Configuration
Color schemes and styling
"""

# ============================================================================
# THEME
# ============================================================================

THEME = {
    'primary': '#2563eb',
    'secondary': '#64748b',
    'success': '#10b981',
    'info': '#06b6d4',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'background': '#f8fafc',
    'card_bg': '#ffffff',
    'text': '#0f172a',
    'text_secondary': '#64748b',
    'border': '#e2e8f0',
    'shadow': 'rgba(0, 0, 0, 0.1)',
}

# ============================================================================
# CHART COLOR PALETTE
# ============================================================================

CHART_COLORS = [
    '#2563eb', '#10b981', '#f59e0b', '#ef4444', 
    '#06b6d4', '#8b5cf6', '#ec4899', '#f97316'
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_theme_colors() -> dict:
    """Get theme colors."""
    return THEME

def get_chart_colors() -> list:
    """Get chart color palette."""
    return CHART_COLORS

def get_plot_template() -> str:
    """Get plotly template."""
    return 'plotly_white'
