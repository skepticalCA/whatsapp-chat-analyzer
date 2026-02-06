"""
Font setup module for dashboard generators.
Registers Noto Emoji font with matplotlib for proper emoji rendering in PNGs.
"""

import os
import matplotlib
import matplotlib.font_manager as fm

_font_added = False
_emoji_font_available = False


def setup_fonts():
    """
    Register NotoEmoji-Regular.ttf with matplotlib and configure the
    sans-serif font fallback chain so that emoji glyphs render correctly.

    The font file is registered once, but rcParams are reapplied every call
    because plt.style.use() resets them between dashboard generators.
    """
    global _font_added, _emoji_font_available

    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    emoji_font_path = os.path.join(font_dir, 'NotoEmoji-Regular.ttf')

    # Register font file only once
    if not _font_added and os.path.exists(emoji_font_path):
        fm.fontManager.addfont(emoji_font_path)
        _emoji_font_available = True
        _font_added = True
    elif not _font_added:
        import warnings
        warnings.warn(
            f"NotoEmoji-Regular.ttf not found at {emoji_font_path}. "
            "Emoji characters may not render correctly in dashboards."
        )
        _font_added = True

    # Always reapply rcParams (plt.style.use() resets them)
    if _emoji_font_available:
        matplotlib.rcParams['font.family'] = ['sans-serif', 'Noto Emoji']
        matplotlib.rcParams['font.sans-serif'] = [
            'Arial', 'Helvetica', 'DejaVu Sans'
        ]
