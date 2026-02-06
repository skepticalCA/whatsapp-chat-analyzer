#!/usr/bin/env python3
"""
Traits Dashboard Generator
Creates a visual dashboard showing good and bad traits for both partners.
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_parser import parse_whatsapp_chat
from metrics_calculator import MetricsCalculator
from traits_analyzer import TraitsAnalyzer
from font_setup import setup_fonts


# Romantic Love Theme Color Palette - Soft & Dreamy
COLORS = {
    'background': '#fef7f9',       # Softer blush background
    'card_bg': '#ffffff',          # White cards
    'card_border': '#ffc0cb',      # Soft pink border
    'card_shadow': '#ffe4ec',      # Pink shadow effect
    'text_primary': '#5c4a52',     # Warm dark text
    'text_secondary': '#8b7580',   # Muted rose text
    'text_muted': '#c4b0b8',       # Light muted text
    'good_green': '#4ade80',       # Soft mint green
    'good_light': '#86efac',       # Light mint
    'bad_red': '#fda4af',          # Soft coral (not harsh red)
    'bad_light': '#fecdd3',        # Light coral
    'person1': '#818cf8',          # Soft indigo
    'person2': '#f472b6',          # Rose pink
    'gold': '#fbbf24',             # Warm gold
    'purple': '#c084fc',           # Soft lavender
    'cyan': '#22d3ee',             # Soft cyan
    'love_pink': '#ff85a2',        # Romantic pink
    'love_light': '#ffb3c6',       # Light romantic pink
    'love_dark': '#db2777',        # Deep magenta
    'gradient_start': '#fce7f3',   # Gradient start
    'gradient_end': '#ddd6fe',     # Gradient end
}


class TraitsDashboardGenerator:
    """Generate visual dashboard for traits analysis."""

    def __init__(self, traits_analyzer: TraitsAnalyzer, participant_mapping: Dict[str, str]):
        self.analyzer = traits_analyzer
        self.participant_mapping = participant_mapping
        self.participants = list(participant_mapping.keys())

        plt.style.use('seaborn-v0_8-whitegrid')
        setup_fonts()
        plt.rcParams['axes.facecolor'] = COLORS['card_bg']
        plt.rcParams['figure.facecolor'] = COLORS['background']
        plt.rcParams['text.color'] = COLORS['text_primary']

    def get_display_name(self, raw_name: str) -> str:
        return self.participant_mapping.get(raw_name, raw_name)

    def create_dashboard(self, output_path: str, figsize=(22, 30)):
        """Generate the complete traits dashboard."""
        fig = plt.figure(figsize=figsize, facecolor=COLORS['background'])

        # Create grid layout
        gs = GridSpec(6, 2, figure=fig, hspace=0.25, wspace=0.15,
                      left=0.05, right=0.95, top=0.95, bottom=0.03)

        # Row 0: Header
        ax_header = fig.add_subplot(gs[0, :])
        self._render_header(ax_header)

        # Row 1: Good traits - Person 1 | Good traits - Person 2
        ax_good1 = fig.add_subplot(gs[1, 0])
        ax_good2 = fig.add_subplot(gs[1, 1])

        # Row 2: Bad traits - Person 1 | Bad traits - Person 2
        ax_bad1 = fig.add_subplot(gs[2, 0])
        ax_bad2 = fig.add_subplot(gs[2, 1])

        # Row 3: Detailed metrics comparison
        ax_metrics = fig.add_subplot(gs[3, :])

        # Row 4: Communication style comparison
        ax_style = fig.add_subplot(gs[4, :])

        # Row 5: Improvement suggestions
        ax_suggestions = fig.add_subplot(gs[5, :])

        # Get data
        good_traits = self.analyzer.get_good_traits()
        bad_traits = self.analyzer.get_bad_traits()

        # Render sections
        if len(self.participants) >= 2:
            p1, p2 = self.participants[0], self.participants[1]
            self._render_good_traits(ax_good1, p1, good_traits.get(p1, []))
            self._render_good_traits(ax_good2, p2, good_traits.get(p2, []))
            self._render_bad_traits(ax_bad1, p1, bad_traits.get(p1, []))
            self._render_bad_traits(ax_bad2, p2, bad_traits.get(p2, []))

        self._render_detailed_metrics(ax_metrics)
        self._render_communication_style(ax_style)
        self._render_suggestions(ax_suggestions, bad_traits)

        # Save
        plt.savefig(output_path, dpi=150, facecolor=COLORS['background'],
                    edgecolor='none', bbox_inches='tight')
        plt.close()
        print(f"Traits dashboard saved to {output_path}")

    def _setup_card(self, ax, title: str = None, title_color=None, icon: str = "💕"):
        """Set up card styling with romantic theme."""
        ax.set_facecolor(COLORS['card_bg'])
        for spine in ax.spines.values():
            spine.set_color(COLORS['card_border'])
            spine.set_linewidth(2.5)
        ax.tick_params(colors=COLORS['text_secondary'])

        if title:
            color = title_color or COLORS['love_dark']
            ax.set_title(f"{icon} {title}", color=color, fontsize=14,
                        fontweight='bold', loc='left', pad=15)

    def _render_header(self, ax):
        """Render beautiful romantic header."""
        ax.set_facecolor(COLORS['background'])
        ax.axis('off')

        # Decorative side hearts
        ax.text(0.08, 0.50, "✨", fontsize=30, ha='center', va='center',
                transform=ax.transAxes, alpha=0.6)
        ax.text(0.92, 0.50, "✨", fontsize=30, ha='center', va='center',
                transform=ax.transAxes, alpha=0.6)

        # Top subtitle
        ax.text(0.5, 0.78, "✨ Discover Your Unique Connection ✨", fontsize=14,
                color=COLORS['love_pink'], ha='center', va='center',
                transform=ax.transAxes)

        # Main title
        ax.text(0.5, 0.55, "Personality & Traits", fontsize=32,
                color=COLORS['love_dark'], ha='center', va='center',
                fontweight='bold', transform=ax.transAxes)

        # Names with hearts
        p1_name = self.get_display_name(self.participants[0])
        p2_name = self.get_display_name(self.participants[1]) if len(self.participants) > 1 else ""

        ax.text(0.5, 0.30, f"💙 {p1_name}  &  {p2_name} 💖", fontsize=18,
                color=COLORS['text_primary'], ha='center', va='center',
                fontweight='bold', transform=ax.transAxes)

        # Bottom subtitle
        ax.text(0.5, 0.08, "💕 Celebrating strengths & growing together 💕", fontsize=12,
                color=COLORS['text_secondary'], ha='center', va='center',
                transform=ax.transAxes, fontstyle='italic')

    def _render_good_traits(self, ax, sender: str, traits: List[Dict]):
        """Render beautiful good traits for a person."""
        name = self.get_display_name(sender)
        is_person1 = sender == self.participants[0]
        color = COLORS['person1'] if is_person1 else COLORS['person2']
        emoji = "💙" if is_person1 else "💖"

        self._setup_card(ax, f"{emoji} {name}'s Strengths", title_color=COLORS['good_green'], icon="⭐")
        ax.axis('off')

        if not traits:
            ax.text(0.5, 0.5, "✨ Every strength counts! ✨",
                   color=COLORS['text_muted'], ha='center', va='center',
                   transform=ax.transAxes, fontsize=12, fontstyle='italic')
            return

        # Decorative stars
        strength_icons = ["🌟", "⭐", "✨", "💫", "🌟"]

        y_pos = 0.86
        for i, trait in enumerate(traits[:5]):
            # Score bar background (rounded)
            bar_width = trait['score'] / 100 * 0.58

            ax.add_patch(mpatches.FancyBboxPatch(
                (0.30, y_pos - 0.025), 0.58, 0.04,
                boxstyle="round,pad=0.015",
                facecolor=COLORS['good_light'],
                alpha=0.3,
                transform=ax.transAxes
            ))

            # Score bar fill (gradient effect)
            ax.add_patch(mpatches.FancyBboxPatch(
                (0.30, y_pos - 0.025), bar_width, 0.04,
                boxstyle="round,pad=0.015",
                facecolor=COLORS['good_green'],
                alpha=0.75,
                transform=ax.transAxes
            ))

            # Strength icon
            ax.text(0.05, y_pos, strength_icons[i % len(strength_icons)], fontsize=16,
                   ha='center', va='center', transform=ax.transAxes)

            # Trait name (bold)
            ax.text(0.12, y_pos + 0.025, trait['trait'], fontsize=11,
                   color=COLORS['text_primary'], fontweight='bold',
                   transform=ax.transAxes, va='center')

            # Description
            desc = trait['description'][:42] + ('...' if len(trait['description']) > 42 else '')
            ax.text(0.12, y_pos - 0.03, desc, fontsize=8.5,
                   color=COLORS['text_secondary'], transform=ax.transAxes, va='center')

            # Score with check mark
            ax.text(0.92, y_pos, f"✓ {trait['score']:.0f}", fontsize=11,
                   color=COLORS['good_green'], fontweight='bold',
                   ha='right', va='center', transform=ax.transAxes)

            y_pos -= 0.165

    def _render_bad_traits(self, ax, sender: str, traits: List[Dict]):
        """Render gentle growth areas for a person."""
        name = self.get_display_name(sender)
        is_person1 = sender == self.participants[0]
        color = COLORS['person1'] if is_person1 else COLORS['person2']
        emoji = "💙" if is_person1 else "💖"

        self._setup_card(ax, f"{emoji} {name}'s Growth Journey", title_color=COLORS['purple'], icon="🌱")
        ax.axis('off')

        if not traits:
            ax.text(0.5, 0.5, "✨ Always room to grow together! ✨",
                   color=COLORS['text_muted'], ha='center', va='center',
                   transform=ax.transAxes, fontsize=12, fontstyle='italic')
            return

        # Growth-focused icons (softer, encouraging)
        growth_icons = ["🌱", "💪", "📈", "🎯", "💡"]

        y_pos = 0.86
        for i, trait in enumerate(traits[:5]):
            severity = trait.get('severity', 50)
            bar_width = severity / 100 * 0.58

            # Bar background (soft)
            ax.add_patch(mpatches.FancyBboxPatch(
                (0.30, y_pos - 0.025), 0.58, 0.04,
                boxstyle="round,pad=0.015",
                facecolor=COLORS['bad_light'],
                alpha=0.3,
                transform=ax.transAxes
            ))

            # Bar fill (soft coral, not harsh red)
            ax.add_patch(mpatches.FancyBboxPatch(
                (0.30, y_pos - 0.025), bar_width, 0.04,
                boxstyle="round,pad=0.015",
                facecolor=COLORS['bad_red'],
                alpha=0.6,
                transform=ax.transAxes
            ))

            # Growth icon
            ax.text(0.05, y_pos, growth_icons[i % len(growth_icons)], fontsize=16,
                   ha='center', va='center', transform=ax.transAxes)

            # Trait name
            ax.text(0.12, y_pos + 0.025, trait['trait'], fontsize=11,
                   color=COLORS['text_primary'], fontweight='bold',
                   transform=ax.transAxes, va='center')

            # Description (encouraging tone)
            desc = trait['description'][:42] + ('...' if len(trait['description']) > 42 else '')
            ax.text(0.12, y_pos - 0.03, desc, fontsize=8.5,
                   color=COLORS['text_secondary'], transform=ax.transAxes, va='center')

            y_pos -= 0.165

    def _render_detailed_metrics(self, ax):
        """Render beautiful detailed comparison metrics."""
        self._setup_card(ax, "Love Metrics Comparison", icon="📊")
        ax.axis('off')

        analysis = self.analyzer.get_all_analysis()['detailed']

        # Prepare comparison data with icons
        metrics = [
            ('💝 Support', 'supportiveness', 'rate', '%', True),
            ('💕 Affection', 'affection', 'rate', '%', True),
            ('❓ Curiosity', 'effort', 'questions_rate', '%', True),
            ('⚡ Quick Replies', 'responsiveness', 'immediate_reply_pct', '%', True),
            ('😄 Humor', 'humor', 'humor_rate', '%', True),
            ('😐 Passive', 'negativity', 'passive_rate', '%', False),
            ('🪞 Self Focus', 'self_centeredness', 'i_to_you_ratio', 'x', False),
            ('📅 Consistency', 'consistency', 'consistency_score', '%', True),
        ]

        p1, p2 = self.participants[0], self.participants[1] if len(self.participants) > 1 else self.participants[0]
        p1_name = self.get_display_name(p1)[:8]
        p2_name = self.get_display_name(p2)[:8]

        # Headers with hearts
        ax.text(0.42, 0.95, f"💙 {p1_name}", fontsize=12, fontweight='bold',
               color=COLORS['person1'], ha='center', transform=ax.transAxes)
        ax.text(0.65, 0.95, f"💖 {p2_name}", fontsize=12, fontweight='bold',
               color=COLORS['person2'], ha='center', transform=ax.transAxes)

        y_pos = 0.85
        for metric_name, category, key, unit, higher_better in metrics:
            p1_val = analysis[category][p1].get(key, 0)
            p2_val = analysis[category][p2].get(key, 0)

            # Metric name with icon
            ax.text(0.12, y_pos, metric_name, fontsize=10,
                   color=COLORS['text_secondary'], ha='left', va='center',
                   transform=ax.transAxes)

            # Values with color coding
            p1_color = COLORS['person1']
            p2_color = COLORS['person2']

            # Highlight better value with green
            if higher_better and p1_val > p2_val * 1.1:
                p1_color = COLORS['good_green']
            elif higher_better and p2_val > p1_val * 1.1:
                p2_color = COLORS['good_green']
            elif not higher_better and p1_val < p2_val * 0.9:
                p1_color = COLORS['good_green']
            elif not higher_better and p2_val < p1_val * 0.9:
                p2_color = COLORS['good_green']

            ax.text(0.42, y_pos, f"{p1_val:.1f}{unit}", fontsize=11,
                   color=p1_color, ha='center', va='center',
                   fontweight='bold', transform=ax.transAxes)

            ax.text(0.65, y_pos, f"{p2_val:.1f}{unit}", fontsize=11,
                   color=p2_color, ha='center', va='center',
                   fontweight='bold', transform=ax.transAxes)

            y_pos -= 0.10

    def _render_communication_style(self, ax):
        """Render beautiful communication style comparison."""
        self._setup_card(ax, "How You Express Love", icon="💬")

        analysis = self.analyzer.get_all_analysis()['detailed']
        p1, p2 = self.participants[0], self.participants[1] if len(self.participants) > 1 else self.participants[0]

        # Categories with emoji labels
        categories = ['💝\nSupportive', '💕\nAffectionate', '❓\nCurious', '⚡\nResponsive', '😄\nPlayful', '📅\nConsistent']
        p1_values = [
            min(100, analysis['supportiveness'][p1]['rate'] * 30),
            min(100, analysis['affection'][p1]['rate'] * 5),
            min(100, analysis['self_centeredness'][p1]['question_ratio'] * 3),
            analysis['responsiveness'][p1]['immediate_reply_pct'],
            min(100, analysis['humor'][p1]['humor_rate'] * 5),
            analysis['consistency'][p1]['consistency_score']
        ]
        p2_values = [
            min(100, analysis['supportiveness'][p2]['rate'] * 30),
            min(100, analysis['affection'][p2]['rate'] * 5),
            min(100, analysis['self_centeredness'][p2]['question_ratio'] * 3),
            analysis['responsiveness'][p2]['immediate_reply_pct'],
            min(100, analysis['humor'][p2]['humor_rate'] * 5),
            analysis['consistency'][p2]['consistency_score']
        ]

        x = np.arange(len(categories))
        width = 0.38

        # Beautiful bars with rounded edges effect
        bars1 = ax.bar(x - width/2, p1_values, width, label=f"💙 {self.get_display_name(p1)}",
                       color=COLORS['person1'], alpha=0.85, edgecolor='white', linewidth=1)
        bars2 = ax.bar(x + width/2, p2_values, width, label=f"💖 {self.get_display_name(p2)}",
                       color=COLORS['person2'], alpha=0.85, edgecolor='white', linewidth=1)

        ax.set_ylabel('Score ✨', color=COLORS['text_secondary'], fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=9)
        ax.legend(loc='upper right', frameon=False, fontsize=10)
        ax.set_ylim(0, 115)

        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=9,
                       color=COLORS['person1'], fontweight='bold')

        for bar in bars2:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=9,
                       color=COLORS['person2'], fontweight='bold')

    def _render_suggestions(self, ax, bad_traits: Dict):
        """Render encouraging growth suggestions for both."""
        self._setup_card(ax, "Growing Together", icon="🌱")
        ax.axis('off')

        # Encouraging header
        ax.text(0.5, 0.95, "✨ Small steps lead to big changes ✨", fontsize=11,
               color=COLORS['love_pink'], ha='center', transform=ax.transAxes,
               fontstyle='italic')

        y_pos = 0.85
        col = 0

        for sender in self.participants:
            name = self.get_display_name(sender)
            is_person1 = sender == self.participants[0]
            color = COLORS['person1'] if is_person1 else COLORS['person2']
            emoji = "💙" if is_person1 else "💖"

            x_base = 0.05 + col * 0.5

            ax.text(x_base, y_pos, f"{emoji} For {name}:", fontsize=12,
                   color=color, fontweight='bold', transform=ax.transAxes)

            y = y_pos - 0.14
            traits = bad_traits.get(sender, [])[:4]

            # Growth-focused icons
            growth_icons = ["💡", "🎯", "💪", "🌟"]

            for i, trait in enumerate(traits):
                suggestion = trait.get('suggestion', 'Keep being amazing!')
                icon = growth_icons[i % len(growth_icons)]

                ax.text(x_base, y, f"  {icon} {suggestion[:48]}{'...' if len(suggestion) > 48 else ''}",
                       fontsize=9.5, color=COLORS['text_secondary'],
                       transform=ax.transAxes, va='center')
                y -= 0.11

            col += 1


def main():
    """Run traits analysis and generate dashboard."""
    CHAT_FILE = '/Users/arvind/PythonProjects/Chatanaylsi/_chat.txt'
    OUTPUT_PATH = '/Users/arvind/PythonProjects/Chatanaylsi/output/traits_dashboard.png'

    PARTICIPANT_MAPPING = {
        "~~": "Arvind",
        "bae 🫶": "Palak"
    }

    print("Parsing chat file...")
    messages = parse_whatsapp_chat(CHAT_FILE)
    print(f"Parsed {len(messages):,} messages")

    print("Calculating metrics...")
    metrics = MetricsCalculator(messages, PARTICIPANT_MAPPING)

    print("Analyzing traits...")
    traits_analyzer = TraitsAnalyzer(messages, metrics, PARTICIPANT_MAPPING)

    # Print summary
    print("\n" + "="*60)
    print("GOOD TRAITS")
    print("="*60)
    good = traits_analyzer.get_good_traits()
    for sender, traits in good.items():
        name = PARTICIPANT_MAPPING.get(sender, sender)
        print(f"\n{name}:")
        for t in traits:
            print(f"  {t['icon']} {t['trait']}: {t['description']}")

    print("\n" + "="*60)
    print("AREAS FOR IMPROVEMENT")
    print("="*60)
    bad = traits_analyzer.get_bad_traits()
    for sender, traits in bad.items():
        name = PARTICIPANT_MAPPING.get(sender, sender)
        print(f"\n{name}:")
        for t in traits:
            print(f"  {t['icon']} {t['trait']}: {t['description']}")
            print(f"     Suggestion: {t['suggestion']}")

    print("\nGenerating dashboard...")
    dashboard = TraitsDashboardGenerator(traits_analyzer, PARTICIPANT_MAPPING)
    dashboard.create_dashboard(OUTPUT_PATH)

    print(f"\nDashboard saved to: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
