"""
Dashboard Generator Module
Creates the visual dashboard PNG using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from chat_parser import Message
from metrics_calculator import MetricsCalculator
from topic_classifier import TopicClassifier
from sentiment_analyzer import SentimentAnalyzer


# Romantic Love Theme Color Palette - Soft & Dreamy
COLORS = {
    'background': '#fef7f9',       # Softer blush background
    'card_bg': '#ffffff',          # White cards
    'card_border': '#ffc0cb',      # Soft pink border
    'card_shadow': '#ffe4ec',      # Pink shadow effect
    'text_primary': '#5c4a52',     # Warm dark text
    'text_secondary': '#8b7580',   # Muted rose text
    'text_muted': '#c4b0b8',       # Light muted text
    'accent_green': '#4ade80',     # Soft mint green
    'accent_orange': '#fb923c',    # Warm peach
    'accent_purple': '#c084fc',    # Soft lavender
    'accent_pink': '#f472b6',      # Rose pink
    'accent_blue': '#818cf8',      # Soft periwinkle
    'accent_cyan': '#22d3ee',      # Soft cyan
    'accent_red': '#fb7185',       # Soft coral
    'accent_rose': '#fda4af',      # Blush rose
    'person1': '#818cf8',          # Soft indigo for Person 1
    'person2': '#f472b6',          # Rose pink for Person 2
    'love_pink': '#ff85a2',        # Romantic pink
    'love_light': '#ffb3c6',       # Light romantic pink
    'love_dark': '#db2777',        # Deep magenta
    'heart_red': '#f43f5e',        # Heart red
    'gradient_start': '#fce7f3',   # Gradient start (soft pink)
    'gradient_end': '#ddd6fe',     # Gradient end (soft purple)
    'chart_colors': ['#f472b6', '#818cf8', '#4ade80', '#fb923c', '#c084fc', '#22d3ee', '#fda4af']
}


class DashboardGenerator:
    """Generate visual dashboard from chat analysis."""

    def __init__(self, messages: List[Message], metrics: MetricsCalculator,
                 sentiment: SentimentAnalyzer, topics: TopicClassifier,
                 participant_mapping: Dict[str, str]):
        """
        Initialize with all calculated data.
        """
        self.messages = messages
        self.metrics = metrics
        self.sentiment = sentiment
        self.topics = topics
        self.participant_mapping = participant_mapping
        self.participants = list(participant_mapping.keys())

        # Set up matplotlib style - Light romantic theme
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
        plt.rcParams['axes.facecolor'] = COLORS['card_bg']
        plt.rcParams['figure.facecolor'] = COLORS['background']
        plt.rcParams['text.color'] = COLORS['text_primary']
        plt.rcParams['axes.labelcolor'] = COLORS['text_secondary']
        plt.rcParams['xtick.color'] = COLORS['text_secondary']
        plt.rcParams['ytick.color'] = COLORS['text_secondary']

    def get_display_name(self, raw_name: str) -> str:
        """Get display name for a participant."""
        return self.participant_mapping.get(raw_name, raw_name)

    def create_dashboard(self, output_path: str, figsize: Tuple[int, int] = (20, 28)):
        """Generate complete dashboard PNG."""
        fig = plt.figure(figsize=figsize, facecolor=COLORS['background'])

        # Create grid layout
        gs = GridSpec(8, 3, figure=fig, hspace=0.3, wspace=0.25,
                      left=0.05, right=0.95, top=0.95, bottom=0.03)

        # Row 0: Header (spans all columns)
        ax_header = fig.add_subplot(gs[0, :])
        self._render_header(ax_header)

        # Row 1: Relationship Rating | Key Insights | Conversation Analysis
        ax_rating = fig.add_subplot(gs[1, 0])
        ax_insights = fig.add_subplot(gs[1, 1])
        ax_conv = fig.add_subplot(gs[1, 2])
        self._render_relationship_rating(ax_rating)
        self._render_key_insights(ax_insights)
        self._render_conversation_analysis(ax_conv)

        # Row 2: Balance of Power | Direction | Responding
        ax_balance = fig.add_subplot(gs[2, 0])
        ax_direction = fig.add_subplot(gs[2, 1])
        ax_responding = fig.add_subplot(gs[2, 2])
        self._render_balance_of_power(ax_balance)
        self._render_direction_stats(ax_direction)
        self._render_responding_metrics(ax_responding)

        # Row 3: Chat Focus Pie | Message Analysis | Content Analysis
        ax_pie = fig.add_subplot(gs[3, 0])
        ax_msg_analysis = fig.add_subplot(gs[3, 1])
        ax_content = fig.add_subplot(gs[3, 2])
        self._render_chat_focus_pie(ax_pie)
        self._render_message_analysis(ax_msg_analysis)
        self._render_content_analysis(ax_content)

        # Row 4: Messaging Times Heatmap (spans all columns)
        ax_heatmap = fig.add_subplot(gs[4, :])
        self._render_messaging_heatmap(ax_heatmap)

        # Row 5-6: Relationship Growth Timeline (spans all columns, double height)
        ax_timeline = fig.add_subplot(gs[5:7, :])
        self._render_growth_timeline(ax_timeline)

        # Row 7: Milestones
        ax_milestones = fig.add_subplot(gs[7, :])
        self._render_milestones(ax_milestones)

        # Save
        plt.savefig(output_path, dpi=150, facecolor=COLORS['background'],
                    edgecolor='none', bbox_inches='tight')
        plt.close()
        print(f"Dashboard saved to {output_path}")

    def _setup_card(self, ax, title: str = None, icon: str = "💕"):
        """Set up a card-style subplot with romantic styling."""
        ax.set_facecolor(COLORS['card_bg'])
        for spine in ax.spines.values():
            spine.set_color(COLORS['card_border'])
            spine.set_linewidth(2.5)
        ax.tick_params(colors=COLORS['text_secondary'])

        if title:
            ax.set_title(f"{icon} {title}", color=COLORS['love_dark'], fontsize=13,
                        fontweight='bold', loc='left', pad=12,
                        fontfamily='sans-serif')

    def _render_header(self, ax):
        """Render beautiful romantic header with decorative elements."""
        ax.set_facecolor(COLORS['background'])
        ax.axis('off')

        # Get date range
        start, end = self.metrics.get_date_range()
        days_together = (end - start).days
        date_range = f"{start.strftime('%b %d, %Y')} — {end.strftime('%b %d, %Y')}"

        # Get display names
        names = list(self.participant_mapping.values())
        title_text = f"{names[0]} & {names[1]}" if len(names) >= 2 else "Your Love Story"

        # Decorative hearts on sides
        ax.text(0.08, 0.55, "💕", fontsize=32, ha='center', va='center',
                transform=ax.transAxes, alpha=0.6)
        ax.text(0.92, 0.55, "💕", fontsize=32, ha='center', va='center',
                transform=ax.transAxes, alpha=0.6)

        # Main title with romantic styling
        ax.text(0.5, 0.72, "✨ Your Love Story ✨", fontsize=18,
                color=COLORS['love_pink'], ha='center', va='center',
                fontweight='normal', transform=ax.transAxes, alpha=0.9)

        ax.text(0.5, 0.50, title_text, fontsize=34,
                color=COLORS['love_dark'], ha='center', va='center',
                fontweight='bold', transform=ax.transAxes)

        # Date range with heart
        ax.text(0.5, 0.28, f"💖 {date_range} 💖", fontsize=13,
                color=COLORS['text_secondary'], ha='center', va='center',
                transform=ax.transAxes)

        # Days together stat
        ax.text(0.5, 0.08, f"✨ {days_together} days of love ✨", fontsize=11,
                color=COLORS['love_pink'], ha='center', va='center',
                transform=ax.transAxes, fontstyle='italic')

    def _render_relationship_rating(self, ax):
        """Render beautiful love score with decorative heart design."""
        self._setup_card(ax, "LOVE SCORE", icon="💖")
        ax.axis('off')

        label, desc, score = self.sentiment.calculate_relationship_rating()

        # Outer decorative ring
        circle_outer = plt.Circle((0.5, 0.58), 0.28, color=COLORS['love_light'],
                                  fill=False, linewidth=3, transform=ax.transAxes,
                                  linestyle='--', alpha=0.5)
        ax.add_patch(circle_outer)

        # Main score circle with gradient effect
        circle = plt.Circle((0.5, 0.58), 0.24, color=COLORS['love_pink'],
                            fill=False, linewidth=6, transform=ax.transAxes)
        ax.add_patch(circle)

        # Inner soft fill
        circle_fill = plt.Circle((0.5, 0.58), 0.22, color=COLORS['gradient_start'],
                                 alpha=0.4, transform=ax.transAxes)
        ax.add_patch(circle_fill)

        # Score number
        ax.text(0.5, 0.60, f"{score:.0f}", fontsize=38, color=COLORS['love_dark'],
                ha='center', va='center', fontweight='bold', transform=ax.transAxes)

        # Heart below score
        ax.text(0.5, 0.42, "❤️", fontsize=16, ha='center', va='center', transform=ax.transAxes)

        # Label with stars
        ax.text(0.5, 0.22, f"✨ {label} ✨", fontsize=14, color=COLORS['love_dark'],
                ha='center', va='center', fontweight='bold', transform=ax.transAxes)

        # Description
        ax.text(0.5, 0.07, desc, fontsize=8, color=COLORS['text_secondary'],
                ha='center', va='center', wrap=True, transform=ax.transAxes,
                fontstyle='italic')

    def _render_key_insights(self, ax):
        """Render insights list with beautiful romantic styling."""
        self._setup_card(ax, "KEY INSIGHTS", icon="✨")
        ax.axis('off')

        insights = self.sentiment.generate_key_insights()

        # Alternating heart icons for variety
        hearts = ["💕", "💗", "💖", "💘", "💝"]

        y_pos = 0.85
        for i, insight in enumerate(insights[:5]):
            # Decorative heart bullet
            ax.text(0.04, y_pos, hearts[i % len(hearts)], fontsize=11,
                   transform=ax.transAxes, va='center')

            # Insight text with nice wrapping
            wrapped = insight[:55] + ('...' if len(insight) > 55 else '')
            ax.text(0.12, y_pos, wrapped, fontsize=9.5, color=COLORS['text_primary'],
                   transform=ax.transAxes, va='center')
            y_pos -= 0.165

    def _render_conversation_analysis(self, ax):
        """Render beautiful message counts."""
        self._setup_card(ax, "MESSAGE COUNT", icon="💬")
        ax.axis('off')

        msg_counts = self.metrics.get_message_counts()
        double_msgs = self.metrics.get_double_messages()
        total_msgs = sum(msg_counts.values())

        # Total at top
        ax.text(0.5, 0.88, f"✨ {total_msgs:,} messages ✨", fontsize=14,
               color=COLORS['love_dark'], ha='center', transform=ax.transAxes,
               fontweight='bold')

        y_pos = 0.72
        for i, (sender, count) in enumerate(sorted(msg_counts.items(), key=lambda x: -x[1])):
            name = self.get_display_name(sender)
            color = COLORS['person1'] if i == 0 else COLORS['person2']
            emoji = "💙" if i == 0 else "💖"
            pct = (count / total_msgs * 100) if total_msgs > 0 else 0

            # Name with emoji
            ax.text(0.08, y_pos, f"{emoji} {name}", fontsize=11, color=color,
                   fontweight='bold', transform=ax.transAxes)
            ax.text(0.92, y_pos, f"{count:,}", fontsize=13, color=color,
                   fontweight='bold', transform=ax.transAxes, ha='right')
            ax.text(0.72, y_pos - 0.08, f"({pct:.0f}%)", fontsize=9, color=COLORS['text_muted'],
                   transform=ax.transAxes, ha='right')
            y_pos -= 0.22

        # Quality level with star
        label, _, score = self.sentiment.calculate_relationship_rating()
        ax.text(0.08, y_pos, "⭐ Quality", fontsize=10, color=COLORS['text_secondary'],
               transform=ax.transAxes)
        ax.text(0.92, y_pos, label, fontsize=11, color=COLORS['accent_green'],
               fontweight='bold', transform=ax.transAxes, ha='right')
        y_pos -= 0.15

        # Double messages
        total_double = sum(double_msgs.values())
        ax.text(0.08, y_pos, "💕 Double texts", fontsize=10, color=COLORS['text_secondary'],
               transform=ax.transAxes)
        ax.text(0.92, y_pos, f"{total_double:,}", fontsize=10, color=COLORS['love_pink'],
               transform=ax.transAxes, ha='right', fontweight='bold')

    def _render_balance_of_power(self, ax):
        """Render beautiful message balance visualization."""
        self._setup_card(ax, "BALANCE OF LOVE", icon="⚖️")

        ratio = self.metrics.get_message_ratio()
        sorted_ratio = sorted(ratio.items(), key=lambda x: -x[1])

        if len(sorted_ratio) >= 2:
            names = [self.get_display_name(s[0]) for s in sorted_ratio]
            values = [s[1] for s in sorted_ratio]
            colors = [COLORS['person1'], COLORS['person2']]

            # Rounded horizontal bars with gradient-like effect
            ax.barh([0], [values[0]], color=colors[0], height=0.5, alpha=0.85,
                   edgecolor=colors[0], linewidth=2)
            ax.barh([0], [values[1]], left=[values[0]], color=colors[1], height=0.5,
                   alpha=0.85, edgecolor=colors[1], linewidth=2)

            # Percentage labels with emoji
            ax.text(values[0]/2, 0.02, f"{values[0]:.0f}%", ha='center', va='center',
                   color='white', fontsize=13, fontweight='bold')
            ax.text(values[0] + values[1]/2, 0.02, f"{values[1]:.0f}%", ha='center', va='center',
                   color='white', fontsize=13, fontweight='bold')

            # Name labels with hearts
            ax.text(values[0]/2, -0.42, f"💙 {names[0]}", ha='center', va='center',
                   color=colors[0], fontsize=11, fontweight='bold')
            ax.text(values[0] + values[1]/2, -0.42, f"💖 {names[1]}", ha='center', va='center',
                   color=colors[1], fontsize=11, fontweight='bold')

        ax.set_xlim(0, 100)
        ax.set_ylim(-0.7, 0.7)
        ax.axis('off')

    def _render_direction_stats(self, ax):
        """Render who initiates conversations with nice visual."""
        self._setup_card(ax, "WHO STARTS THE CHAT", icon="💌")
        ax.axis('off')

        initiations = self.metrics.get_conversation_initiations()
        total = sum(initiations.values())

        y_pos = 0.78
        ax.text(0.5, 0.92, "Who reaches out first? 💬", fontsize=10,
               color=COLORS['text_secondary'], ha='center', transform=ax.transAxes,
               fontstyle='italic')

        for i, (sender, count) in enumerate(sorted(initiations.items(), key=lambda x: -x[1])):
            name = self.get_display_name(sender)
            pct = (count / total * 100) if total > 0 else 0
            color = COLORS['person1'] if i == 0 else COLORS['person2']
            emoji = "💙" if i == 0 else "💖"

            # Progress bar background (rounded look)
            ax.add_patch(mpatches.FancyBboxPatch((0.18, y_pos - 0.04), 0.64, 0.07,
                        boxstyle="round,pad=0.02", facecolor=COLORS['card_shadow'],
                        transform=ax.transAxes))

            # Progress bar fill
            bar_width = pct / 100 * 0.64
            ax.add_patch(mpatches.FancyBboxPatch((0.18, y_pos - 0.04), bar_width, 0.07,
                        boxstyle="round,pad=0.02", facecolor=color, alpha=0.8,
                        transform=ax.transAxes))

            ax.text(0.05, y_pos, f"{emoji}", fontsize=12, transform=ax.transAxes, va='center')
            ax.text(0.88, y_pos, f"{pct:.0f}%", fontsize=11, color=color,
                   transform=ax.transAxes, ha='left', va='center', fontweight='bold')
            ax.text(0.5, y_pos, name, fontsize=10, color='white',
                   transform=ax.transAxes, ha='center', va='center', fontweight='bold')

            y_pos -= 0.28

        ax.text(0.5, 0.08, f"✨ {total:,} conversations started ✨", fontsize=9,
               color=COLORS['love_pink'], ha='center', transform=ax.transAxes)

    def _render_responding_metrics(self, ax):
        """Render beautiful response time statistics."""
        self._setup_card(ax, "RESPONSE LOVE", icon="⚡")
        ax.axis('off')

        immediate = self.metrics.get_immediate_replies_percentage()
        avg_response = self.metrics.get_average_response_time()
        median_response = self.metrics.get_median_response_time()

        metrics_data = [
            ("⚡ Quick Replies", f"{np.mean(list(immediate.values())):.0f}%", COLORS['accent_green']),
            ("⏱️ Avg Response", f"{np.mean(list(avg_response.values())):.0f} min", COLORS['accent_purple']),
            ("📊 Median Time", f"{np.mean(list(median_response.values())):.0f} min", COLORS['accent_cyan']),
        ]

        y_pos = 0.82
        for label, value, color in metrics_data:
            ax.text(0.08, y_pos, label, fontsize=10, color=COLORS['text_secondary'],
                   transform=ax.transAxes)
            ax.text(0.92, y_pos, value, fontsize=13, color=color,
                   fontweight='bold', transform=ax.transAxes, ha='right')
            y_pos -= 0.21

        # Divider
        ax.axhline(y=0.22, xmin=0.1, xmax=0.9, color=COLORS['card_border'],
                  linewidth=1, linestyle='--')

        # Per-person breakdown
        y_pos = 0.15
        for i, (sender, time) in enumerate(sorted(avg_response.items(), key=lambda x: x[1])):
            name = self.get_display_name(sender)
            color = COLORS['person1'] if i == 0 else COLORS['person2']
            emoji = "💙" if i == 0 else "💖"
            ax.text(0.08, y_pos, f"{emoji} {name}: {time:.0f} min", fontsize=9,
                   color=color, transform=ax.transAxes, fontweight='bold')
            y_pos -= 0.1

    def _render_chat_focus_pie(self, ax):
        """Render beautiful topic distribution donut chart."""
        self._setup_card(ax, "WHAT YOU TALK ABOUT", icon="💭")

        percentages = self.topics.get_topic_percentages()

        # Filter to top 6 topics
        sorted_topics = sorted(percentages.items(), key=lambda x: -x[1])[:6]
        labels = [t[0] for t in sorted_topics]
        sizes = [t[1] for t in sorted_topics]

        # Add 'Other' for remaining
        other_pct = 100 - sum(sizes)
        if other_pct > 1:
            labels.append('Other')
            sizes.append(other_pct)

        # Beautiful soft colors
        soft_colors = ['#f472b6', '#818cf8', '#4ade80', '#fbbf24', '#c084fc', '#22d3ee', '#fda4af']
        colors = soft_colors[:len(labels)]

        # Create donut chart (more modern look)
        wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.0f%%',
                                          colors=colors, startangle=90,
                                          pctdistance=0.78, wedgeprops={'width': 0.55,
                                          'edgecolor': 'white', 'linewidth': 2})

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')

        # Center decoration
        ax.text(0, 0, "💬", fontsize=20, ha='center', va='center')

        # Legend with nicer styling
        ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(0.88, 0.5),
                 fontsize=9, frameon=False, labelcolor=COLORS['text_secondary'])

    def _render_message_analysis(self, ax):
        """Render beautiful word statistics."""
        self._setup_card(ax, "WORDS OF LOVE", icon="📝")
        ax.axis('off')

        word_counts = self.metrics.get_word_counts()
        unique_words = self.metrics.get_unique_words()
        avg_length = self.metrics.get_average_message_length()

        # Total words highlight
        total_words = sum(word_counts.values())
        ax.text(0.5, 0.88, f"📚 {total_words:,} words shared", fontsize=12,
               color=COLORS['love_dark'], ha='center', transform=ax.transAxes,
               fontweight='bold')

        y_pos = 0.70

        # Per person words with nice bars
        for i, (sender, count) in enumerate(sorted(word_counts.items(), key=lambda x: -x[1])):
            name = self.get_display_name(sender)
            color = COLORS['person1'] if i == 0 else COLORS['person2']
            emoji = "💙" if i == 0 else "💖"
            pct = count / total_words * 100

            ax.text(0.08, y_pos, f"{emoji} {name}", fontsize=10, color=color,
                   fontweight='bold', transform=ax.transAxes)
            ax.text(0.92, y_pos, f"{count:,}", fontsize=11, color=color,
                   transform=ax.transAxes, ha='right', fontweight='bold')
            y_pos -= 0.14

        y_pos -= 0.05

        # Unique words
        ax.text(0.08, y_pos, "🎨 Unique Words", fontsize=10, color=COLORS['text_secondary'],
               transform=ax.transAxes)
        total_unique = sum(unique_words.values())
        ax.text(0.92, y_pos, f"{total_unique:,}", fontsize=11, color=COLORS['accent_purple'],
               transform=ax.transAxes, ha='right', fontweight='bold')
        y_pos -= 0.14

        # Avg message length
        ax.text(0.08, y_pos, "📏 Avg Words/Msg", fontsize=10, color=COLORS['text_secondary'],
               transform=ax.transAxes)
        avg_all = np.mean(list(avg_length.values()))
        ax.text(0.92, y_pos, f"{avg_all:.1f}", fontsize=11, color=COLORS['accent_cyan'],
               transform=ax.transAxes, ha='right', fontweight='bold')

    def _render_content_analysis(self, ax):
        """Render beautiful media sharing comparison."""
        self._setup_card(ax, "SHARED WITH LOVE", icon="📸")
        ax.axis('off')

        emoji_counts = self.metrics.get_emoji_counts()
        media_counts = self.metrics.get_media_counts()
        link_counts = self.metrics.get_link_counts()
        call_counts = self.metrics.get_call_counts()

        # Prepare data rows
        sorted_participants = sorted(self.participants,
                                    key=lambda x: self.metrics.get_message_counts().get(x, 0),
                                    reverse=True)

        # Header with emojis
        y_pos = 0.88
        ax.text(0.42, y_pos, f"💙 {self.get_display_name(sorted_participants[0])[:6]}", fontsize=10,
               color=COLORS['person1'], fontweight='bold', transform=ax.transAxes, ha='center')
        if len(sorted_participants) > 1:
            ax.text(0.75, y_pos, f"💖 {self.get_display_name(sorted_participants[1])[:6]}", fontsize=10,
                   color=COLORS['person2'], fontweight='bold', transform=ax.transAxes, ha='center')
        y_pos -= 0.13

        # Data rows with icons
        rows = [
            ("😊 Emojis", emoji_counts),
            ("📷 Photos", {s: media_counts.get(s, {}).get('images', 0) for s in sorted_participants}),
            ("🎬 Videos", {s: media_counts.get(s, {}).get('videos', 0) for s in sorted_participants}),
            ("🎵 Audio", {s: media_counts.get(s, {}).get('audio', 0) for s in sorted_participants}),
            ("🔗 Links", link_counts),
            ("📹 Calls", {s: call_counts.get(s, {}).get('video_calls', 0) for s in sorted_participants}),
        ]

        for label, data in rows:
            ax.text(0.05, y_pos, label, fontsize=9, color=COLORS['text_secondary'],
                   transform=ax.transAxes)

            val1 = data.get(sorted_participants[0], 0)
            ax.text(0.42, y_pos, f"{val1:,}", fontsize=10, color=COLORS['person1'],
                   transform=ax.transAxes, ha='center', fontweight='bold')

            if len(sorted_participants) > 1:
                val2 = data.get(sorted_participants[1], 0)
                ax.text(0.75, y_pos, f"{val2:,}", fontsize=10, color=COLORS['person2'],
                       transform=ax.transAxes, ha='center', fontweight='bold')

            y_pos -= 0.115

    def _render_messaging_heatmap(self, ax):
        """Render beautiful activity heatmap with romantic gradient."""
        self._setup_card(ax, "WHEN YOUR HEARTS CONNECT", icon="💬")

        heatmap_data = self.metrics.get_hourly_heatmap()

        # Day labels with emojis
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat ✨', 'Sun ✨']

        # Create beautiful romantic pink-to-magenta colormap
        from matplotlib.colors import LinearSegmentedColormap
        romantic_colors = ['#fef7f9', '#fce7f3', '#fbcfe8', '#f9a8d4', '#f472b6', '#ec4899', '#db2777']
        romantic_cmap = LinearSegmentedColormap.from_list('romantic', romantic_colors)

        # Create heatmap with nicer styling
        sns.heatmap(heatmap_data, ax=ax, cmap=romantic_cmap, cbar=True,
                   xticklabels=[f'{h}' for h in range(24)],
                   yticklabels=days, linewidths=0.8, linecolor='#fff0f3',
                   cbar_kws={'label': 'Messages', 'shrink': 0.8})

        ax.set_xlabel('Hour of Day 🕐', color=COLORS['text_secondary'], fontsize=11)
        ax.set_ylabel('', color=COLORS['text_secondary'])

        # Style ticks
        ax.tick_params(colors=COLORS['text_secondary'], labelsize=9)
        plt.setp(ax.get_xticklabels(), rotation=0)
        plt.setp(ax.get_yticklabels(), rotation=0)

    def _render_growth_timeline(self, ax):
        """Render beautiful relationship growth timeline."""
        self._setup_card(ax, "YOUR LOVE GROWING OVER TIME", icon="📈")

        growth_data = self.sentiment.get_relationship_growth_data()
        months = growth_data['months']
        volumes = growth_data['message_volumes']

        if len(months) < 2:
            ax.text(0.5, 0.5, "✨ Your story is just beginning! ✨", ha='center', va='center',
                   color=COLORS['love_pink'], transform=ax.transAxes, fontsize=14)
            return

        # Create x positions
        x = np.arange(len(months))

        # Beautiful gradient fill under the line
        ax.fill_between(x, volumes, alpha=0.25, color=COLORS['love_pink'])
        ax.fill_between(x, volumes, alpha=0.15, color=COLORS['accent_purple'])

        # Main line with romantic color
        ax.plot(x, volumes, color=COLORS['love_dark'], linewidth=3, label='Messages 💌')

        # Add dots at key points
        ax.scatter(x[::max(1, len(x)//12)], [volumes[i] for i in range(0, len(volumes), max(1, len(x)//12))],
                  color=COLORS['love_dark'], s=50, zorder=5, alpha=0.8)

        # Plot call frequency if available
        calls = growth_data.get('call_counts', [])
        if calls and any(c > 0 for c in calls):
            ax2 = ax.twinx()
            ax2.plot(x, calls, color=COLORS['accent_purple'], linewidth=2.5,
                    linestyle='--', label='Calls 📞', alpha=0.8)
            ax2.set_ylabel('Calls 📞', color=COLORS['accent_purple'], fontsize=11)
            ax2.tick_params(colors=COLORS['accent_purple'], labelsize=9)
            ax2.spines['right'].set_color(COLORS['accent_purple'])

        # Style main axis
        ax.set_xlim(0, len(months) - 1)
        ax.set_ylim(0, max(volumes) * 1.15)

        # Show month labels nicely
        tick_positions = list(range(0, len(months), max(1, len(months) // 10)))
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([months[i] for i in tick_positions], rotation=45, ha='right', fontsize=9)

        ax.set_ylabel('Messages 💌', color=COLORS['love_dark'], fontsize=11)
        ax.tick_params(colors=COLORS['text_secondary'], labelsize=9)

        # Growth trend annotation with emoji
        trend = growth_data.get('growth_trend', 'stable')
        trend_emojis = {'growing': '📈 Growing!', 'stable': '💕 Steady', 'declining': '📉 Slowing'}
        trend_colors = {'growing': COLORS['accent_green'], 'stable': COLORS['accent_cyan'],
                       'declining': COLORS['accent_orange']}
        ax.text(0.98, 0.95, trend_emojis.get(trend, 'Trend'), fontsize=12,
               color=trend_colors.get(trend, COLORS['text_secondary']),
               transform=ax.transAxes, ha='right', va='top', fontweight='bold')

        # Add milestone markers with hearts
        milestones = growth_data.get('milestones', [])
        for date, label in milestones[:5]:
            if isinstance(date, datetime):
                month_key = date.strftime('%Y-%m')
                if month_key in months:
                    idx = months.index(month_key)
                    ax.axvline(x=idx, color=COLORS['love_pink'], linestyle=':',
                              alpha=0.6, linewidth=2)

    def _render_milestones(self, ax):
        """Render beautiful love milestones timeline."""
        self._setup_card(ax, "YOUR LOVE MILESTONES", icon="🌟")
        ax.axis('off')

        milestones = self.sentiment.detect_milestones()

        if not milestones:
            ax.text(0.5, 0.5, "✨ Your beautiful journey is just beginning! ✨",
                   ha='center', va='center', color=COLORS['love_pink'],
                   transform=ax.transAxes, fontsize=14, fontstyle='italic')
            return

        # Draw connecting line
        num_milestones = min(6, len(milestones))
        start_x = 1.0 / (num_milestones + 1)
        end_x = num_milestones / (num_milestones + 1)
        ax.plot([start_x, end_x], [0.55, 0.55], color=COLORS['love_light'],
               linewidth=3, linestyle='--', alpha=0.6, transform=ax.transAxes)

        # Alternating milestone icons
        icons = ["💖", "💕", "✨", "💝", "🌸", "💗"]

        spacing = 1.0 / (num_milestones + 1)
        for i, (date, label) in enumerate(milestones[:num_milestones]):
            x_pos = spacing * (i + 1)

            # Date string
            if isinstance(date, datetime):
                date_str = date.strftime('%b %Y')
            else:
                date_str = str(date)[:10]

            # Heart marker with glow effect (larger background)
            ax.text(x_pos, 0.55, "⭕", fontsize=28, color=COLORS['gradient_start'],
                   ha='center', va='center', transform=ax.transAxes, alpha=0.5)
            ax.text(x_pos, 0.55, icons[i % len(icons)], fontsize=22,
                   ha='center', va='center', transform=ax.transAxes)

            # Date below
            ax.text(x_pos, 0.32, date_str, fontsize=10, color=COLORS['love_dark'],
                   ha='center', va='center', transform=ax.transAxes, fontweight='bold')

            # Label
            label_short = label[:18] + ('...' if len(label) > 18 else '')
            ax.text(x_pos, 0.15, label_short, fontsize=9, color=COLORS['text_secondary'],
                   ha='center', va='center', transform=ax.transAxes)


if __name__ == '__main__':
    from chat_parser import parse_whatsapp_chat

    file_path = '/Users/arvind/PythonProjects/Chatanaylsi/_chat.txt'
    output_path = '/Users/arvind/PythonProjects/Chatanaylsi/output/dashboard.png'

    print(f"Parsing {file_path}...")
    messages = parse_whatsapp_chat(file_path)

    participant_mapping = {
        "~~": "Arvind",
        "bae \U0001FAF6": "Palak"
    }

    print("Calculating metrics...")
    metrics = MetricsCalculator(messages, participant_mapping)

    print("Analyzing sentiment...")
    sentiment = SentimentAnalyzer(messages, metrics, participant_mapping)

    print("Classifying topics...")
    topics = TopicClassifier(messages)

    print("Generating dashboard...")
    dashboard = DashboardGenerator(messages, metrics, sentiment, topics, participant_mapping)
    dashboard.create_dashboard(output_path)
