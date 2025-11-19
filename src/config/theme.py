"""
Theme Configuration
Color schemes and styling for light and dark modes
"""

# ============================================================================
# LIGHT THEME
# ============================================================================

LIGHT_THEME = {
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
# DARK THEME
# ============================================================================

DARK_THEME = {
    'primary': '#3b82f6',
    'secondary': '#94a3b8',
    'success': '#34d399',
    'info': '#22d3ee',
    'warning': '#fbbf24',
    'danger': '#f87171',
    'background': '#0f172a',
    'card_bg': '#1e293b',
    'text': '#f1f5f9',
    'text_secondary': '#94a3b8',
    'border': '#334155',
    'shadow': 'rgba(0, 0, 0, 0.3)',
}

# ============================================================================
# CHART COLOR PALETTES
# ============================================================================

LIGHT_CHART_COLORS = [
    '#2563eb', '#10b981', '#f59e0b', '#ef4444', 
    '#06b6d4', '#8b5cf6', '#ec4899', '#f97316'
]

DARK_CHART_COLORS = [
    '#3b82f6', '#34d399', '#fbbf24', '#f87171', 
    '#22d3ee', '#a78bfa', '#f472b6', '#fb923c'
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_theme_colors(dark_mode: bool = False) -> dict:
    """Get theme colors based on mode."""
    return DARK_THEME if dark_mode else LIGHT_THEME

def get_chart_colors(dark_mode: bool = False) -> list:
    """Get chart color palette based on mode."""
    return DARK_CHART_COLORS if dark_mode else LIGHT_CHART_COLORS

def get_plot_template(dark_mode: bool = False) -> str:
    """Get plotly template based on theme."""
    return 'plotly_dark' if dark_mode else 'plotly_white'
