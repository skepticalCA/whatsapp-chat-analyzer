"""
Font setup module for dashboard generators.
Registers Noto Emoji font with matplotlib for proper emoji rendering in PNGs.
"""

import os
import matplotlib
import matplotlib.font_manager as fm

_font_registered = False


def setup_fonts():
    """
    Register NotoEmoji-Regular.ttf with matplotlib and configure the
    sans-serif font fallback chain so that emoji glyphs render correctly.

    Safe to call multiple times; the font is only registered once.
    """
    global _font_registered
    if _font_registered:
        return

    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    emoji_font_path = os.path.join(font_dir, 'NotoEmoji-Regular.ttf')

    if os.path.exists(emoji_font_path):
        fm.fontManager.addfont(emoji_font_path)
        # Use multiple font families so matplotlib resolves both a Latin font
        # AND the emoji font, enabling per-character fallback.
        matplotlib.rcParams['font.family'] = ['sans-serif', 'Noto Emoji']
        matplotlib.rcParams['font.sans-serif'] = [
            'Arial', 'Helvetica', 'DejaVu Sans'
        ]
    else:
        import warnings
        warnings.warn(
            f"NotoEmoji-Regular.ttf not found at {emoji_font_path}. "
            "Emoji characters may not render correctly in dashboards."
        )

    _font_registered = True
