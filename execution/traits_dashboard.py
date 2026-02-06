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


# Romantic Love Theme Color Palette
COLORS = {
    'background': '#fff5f7',       # Soft pink background
    'card_bg': '#ffffff',          # White cards
    'card_border': '#ffb6c1',      # Light pink border
    'text_primary': '#4a3540',     # Dark rose text
    'text_secondary': '#7d6070',   # Muted rose text
    'text_muted': '#b8a0aa',       # Light muted text
    'good_green': '#10b981',       # Teal green for positive
    'good_light': '#34d399',       # Light green
    'bad_red': '#f43f5e',          # Rose red for improvement areas
    'bad_light': '#fb7185',        # Light rose
    'person1': '#6366f1',          # Indigo for Person 1
    'person2': '#ec4899',          # Pink for Person 2
    'gold': '#f59e0b',             # Warm gold
    'purple': '#a855f7',           # Soft purple
    'cyan': '#06b6d4',             # Cyan
    'love_pink': '#ff6b9d',        # Love pink
    'love_dark': '#c44569',        # Dark rose
}


class TraitsDashboardGenerator:
    """Generate visual dashboard for traits analysis."""

    def __init__(self, traits_analyzer: TraitsAnalyzer, participant_mapping: Dict[str, str]):
        self.analyzer = traits_analyzer
        self.participant_mapping = participant_mapping
        self.participants = list(participant_mapping.keys())

        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['font.family'] = 'sans-serif'
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

    def _setup_card(self, ax, title: str = None, title_color=None):
        """Set up card styling with romantic theme."""
        ax.set_facecolor(COLORS['card_bg'])
        for spine in ax.spines.values():
            spine.set_color(COLORS['card_border'])
            spine.set_linewidth(2)
        ax.tick_params(colors=COLORS['text_secondary'])

        if title:
            color = title_color or COLORS['love_dark']
            ax.set_title(f"💕 {title}", color=color, fontsize=14,
                        fontweight='bold', loc='left', pad=15)

    def _render_header(self, ax):
        """Render title header with romantic styling."""
        ax.set_facecolor(COLORS['background'])
        ax.axis('off')

        ax.text(0.5, 0.70, "💕 Personality & Traits Analysis 💕", fontsize=28,
                color=COLORS['love_dark'], ha='center', va='center',
                fontweight='bold', transform=ax.transAxes)

        p1_name = self.get_display_name(self.participants[0])
        p2_name = self.get_display_name(self.participants[1]) if len(self.participants) > 1 else ""

        ax.text(0.5, 0.35, f"{p1_name} & {p2_name}", fontsize=20,
                color=COLORS['love_pink'], ha='center', va='center',
                fontweight='bold', transform=ax.transAxes)

        ax.text(0.5, 0.08, "Celebrating your strengths & growing together", fontsize=12,
                color=COLORS['text_secondary'], ha='center', va='center',
                transform=ax.transAxes)

    def _render_good_traits(self, ax, sender: str, traits: List[Dict]):
        """Render good traits for a person."""
        name = self.get_display_name(sender)
        color = COLORS['person1'] if sender == self.participants[0] else COLORS['person2']

        self._setup_card(ax, f"{name}'s Strengths", title_color=COLORS['good_green'])
        ax.axis('off')

        if not traits:
            ax.text(0.5, 0.5, "No notable traits detected",
                   color=COLORS['text_muted'], ha='center', va='center',
                   transform=ax.transAxes, fontsize=12)
            return

        y_pos = 0.88
        for i, trait in enumerate(traits[:5]):
            # Score bar background
            bar_width = trait['score'] / 100 * 0.65

            ax.add_patch(mpatches.FancyBboxPatch(
                (0.28, y_pos - 0.025), 0.65, 0.035,
                boxstyle="round,pad=0.01",
                facecolor=COLORS['card_border'],
                transform=ax.transAxes
            ))

            # Score bar fill
            ax.add_patch(mpatches.FancyBboxPatch(
                (0.28, y_pos - 0.025), bar_width, 0.035,
                boxstyle="round,pad=0.01",
                facecolor=COLORS['good_green'],
                alpha=0.7,
                transform=ax.transAxes
            ))

            # Icon
            ax.text(0.05, y_pos, trait.get('icon', '+'), fontsize=18,
                   ha='center', va='center', transform=ax.transAxes)

            # Trait name
            ax.text(0.12, y_pos + 0.02, trait['trait'], fontsize=11,
                   color=COLORS['text_primary'], fontweight='bold',
                   transform=ax.transAxes, va='center')

            # Description
            desc = trait['description'][:45] + ('...' if len(trait['description']) > 45 else '')
            ax.text(0.12, y_pos - 0.035, desc, fontsize=9,
                   color=COLORS['text_secondary'], transform=ax.transAxes, va='center')

            # Score
            ax.text(0.95, y_pos, f"{trait['score']:.0f}", fontsize=12,
                   color=COLORS['good_green'], fontweight='bold',
                   ha='right', va='center', transform=ax.transAxes)

            y_pos -= 0.17

    def _render_bad_traits(self, ax, sender: str, traits: List[Dict]):
        """Render areas for improvement for a person."""
        name = self.get_display_name(sender)
        color = COLORS['person1'] if sender == self.participants[0] else COLORS['person2']

        self._setup_card(ax, f"{name}'s Growth Areas", title_color=COLORS['bad_red'])
        ax.axis('off')

        if not traits:
            ax.text(0.5, 0.5, "No areas for improvement detected",
                   color=COLORS['text_muted'], ha='center', va='center',
                   transform=ax.transAxes, fontsize=12)
            return

        y_pos = 0.88
        for i, trait in enumerate(traits[:5]):
            severity = trait.get('severity', 50)
            bar_width = severity / 100 * 0.65

            # Bar background
            ax.add_patch(mpatches.FancyBboxPatch(
                (0.28, y_pos - 0.025), 0.65, 0.035,
                boxstyle="round,pad=0.01",
                facecolor=COLORS['card_border'],
                transform=ax.transAxes
            ))

            # Bar fill
            ax.add_patch(mpatches.FancyBboxPatch(
                (0.28, y_pos - 0.025), bar_width, 0.035,
                boxstyle="round,pad=0.01",
                facecolor=COLORS['bad_red'],
                alpha=0.6,
                transform=ax.transAxes
            ))

            # Icon
            ax.text(0.05, y_pos, trait.get('icon', '!'), fontsize=18,
                   ha='center', va='center', transform=ax.transAxes)

            # Trait name
            ax.text(0.12, y_pos + 0.02, trait['trait'], fontsize=11,
                   color=COLORS['text_primary'], fontweight='bold',
                   transform=ax.transAxes, va='center')

            # Description
            desc = trait['description'][:45] + ('...' if len(trait['description']) > 45 else '')
            ax.text(0.12, y_pos - 0.035, desc, fontsize=9,
                   color=COLORS['text_secondary'], transform=ax.transAxes, va='center')

            y_pos -= 0.17

    def _render_detailed_metrics(self, ax):
        """Render detailed comparison metrics."""
        self._setup_card(ax, "Detailed Comparison")
        ax.axis('off')

        analysis = self.analyzer.get_all_analysis()['detailed']

        # Prepare comparison data
        metrics = [
            ('Support Rate', 'supportiveness', 'rate', '%', True),
            ('Affection Rate', 'affection', 'rate', '%', True),
            ('Questions Asked', 'effort', 'questions_rate', '%', True),
            ('Immediate Replies', 'responsiveness', 'immediate_reply_pct', '%', True),
            ('Humor Rate', 'humor', 'humor_rate', '%', True),
            ('Passive Responses', 'negativity', 'passive_rate', '%', False),
            ('I/You Ratio', 'self_centeredness', 'i_to_you_ratio', 'x', False),
            ('Consistency', 'consistency', 'consistency_score', '%', True),
        ]

        p1, p2 = self.participants[0], self.participants[1] if len(self.participants) > 1 else self.participants[0]
        p1_name = self.get_display_name(p1)[:8]
        p2_name = self.get_display_name(p2)[:8]

        # Headers
        ax.text(0.4, 0.95, p1_name, fontsize=12, fontweight='bold',
               color=COLORS['person1'], ha='center', transform=ax.transAxes)
        ax.text(0.6, 0.95, p2_name, fontsize=12, fontweight='bold',
               color=COLORS['person2'], ha='center', transform=ax.transAxes)

        y_pos = 0.85
        for metric_name, category, key, unit, higher_better in metrics:
            p1_val = analysis[category][p1].get(key, 0)
            p2_val = analysis[category][p2].get(key, 0)

            # Metric name
            ax.text(0.15, y_pos, metric_name, fontsize=10,
                   color=COLORS['text_secondary'], ha='left', va='center',
                   transform=ax.transAxes)

            # Values with color coding
            p1_color = COLORS['person1']
            p2_color = COLORS['person2']

            # Highlight better value
            if higher_better and p1_val > p2_val * 1.1:
                p1_color = COLORS['good_green']
            elif higher_better and p2_val > p1_val * 1.1:
                p2_color = COLORS['good_green']
            elif not higher_better and p1_val < p2_val * 0.9:
                p1_color = COLORS['good_green']
            elif not higher_better and p2_val < p1_val * 0.9:
                p2_color = COLORS['good_green']

            ax.text(0.4, y_pos, f"{p1_val:.1f}{unit}", fontsize=11,
                   color=p1_color, ha='center', va='center',
                   fontweight='bold', transform=ax.transAxes)

            ax.text(0.6, y_pos, f"{p2_val:.1f}{unit}", fontsize=11,
                   color=p2_color, ha='center', va='center',
                   fontweight='bold', transform=ax.transAxes)

            y_pos -= 0.105

    def _render_communication_style(self, ax):
        """Render communication style radar-like comparison."""
        self._setup_card(ax, "Communication Style Overview")

        analysis = self.analyzer.get_all_analysis()['detailed']
        p1, p2 = self.participants[0], self.participants[1] if len(self.participants) > 1 else self.participants[0]

        categories = ['Supportive', 'Affectionate', 'Curious', 'Responsive', 'Playful', 'Consistent']
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
        width = 0.35

        bars1 = ax.bar(x - width/2, p1_values, width, label=self.get_display_name(p1),
                       color=COLORS['person1'], alpha=0.8)
        bars2 = ax.bar(x + width/2, p2_values, width, label=self.get_display_name(p2),
                       color=COLORS['person2'], alpha=0.8)

        ax.set_ylabel('Score', color=COLORS['text_secondary'])
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=10)
        ax.legend(loc='upper right', frameon=False)
        ax.set_ylim(0, 110)

        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=8,
                       color=COLORS['text_secondary'])

        for bar in bars2:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=8,
                       color=COLORS['text_secondary'])

    def _render_suggestions(self, ax, bad_traits: Dict):
        """Render improvement suggestions for both."""
        self._setup_card(ax, "Growth Suggestions")
        ax.axis('off')

        y_pos = 0.9
        col = 0

        for sender in self.participants:
            name = self.get_display_name(sender)
            color = COLORS['person1'] if sender == self.participants[0] else COLORS['person2']

            x_base = 0.05 + col * 0.5

            ax.text(x_base, y_pos, f"For {name}:", fontsize=13,
                   color=color, fontweight='bold', transform=ax.transAxes)

            y = y_pos - 0.12
            traits = bad_traits.get(sender, [])[:4]

            for trait in traits:
                suggestion = trait.get('suggestion', 'Keep improving!')
                icon = trait.get('icon', 'o')

                ax.text(x_base, y, f"  {icon} {suggestion[:50]}{'...' if len(suggestion) > 50 else ''}",
                       fontsize=10, color=COLORS['text_secondary'],
                       transform=ax.transAxes, va='center')
                y -= 0.1

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
