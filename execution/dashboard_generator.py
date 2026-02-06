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


# Romantic Love Theme Color Palette
COLORS = {
    'background': '#fff5f7',       # Soft pink background
    'card_bg': '#ffffff',          # White cards
    'card_border': '#ffb6c1',      # Light pink border
    'text_primary': '#4a3540',     # Dark rose text
    'text_secondary': '#7d6070',   # Muted rose text
    'text_muted': '#b8a0aa',       # Light muted text
    'accent_green': '#10b981',     # Teal green for positive
    'accent_orange': '#f97316',    # Warm orange
    'accent_purple': '#a855f7',    # Soft purple
    'accent_pink': '#ec4899',      # Hot pink
    'accent_blue': '#6366f1',      # Soft indigo
    'accent_cyan': '#06b6d4',      # Cyan
    'accent_red': '#f43f5e',       # Rose red
    'accent_rose': '#fb7185',      # Soft rose
    'person1': '#6366f1',          # Indigo for Person 1
    'person2': '#ec4899',          # Pink for Person 2
    'love_pink': '#ff6b9d',        # Love pink
    'love_dark': '#c44569',        # Dark rose
    'heart_red': '#e11d48',        # Heart red
    'chart_colors': ['#ec4899', '#6366f1', '#10b981', '#f97316', '#a855f7', '#06b6d4', '#f43f5e']
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

    def _setup_card(self, ax, title: str = None):
        """Set up a card-style subplot with light romantic background."""
        ax.set_facecolor(COLORS['card_bg'])
        for spine in ax.spines.values():
            spine.set_color(COLORS['card_border'])
            spine.set_linewidth(2)
        ax.tick_params(colors=COLORS['text_secondary'])

        if title:
            ax.set_title(f"💕 {title}", color=COLORS['love_dark'], fontsize=12,
                        fontweight='bold', loc='left', pad=10)

    def _render_header(self, ax):
        """Render title and date range with romantic styling."""
        ax.set_facecolor(COLORS['background'])
        ax.axis('off')

        # Get date range
        start, end = self.metrics.get_date_range()
        date_range = f"From {start.strftime('%d %b %Y')} - {end.strftime('%d %b %Y')}"

        # Get display names
        names = list(self.participant_mapping.values())
        title_text = f"💕 {names[0]} & {names[1]}'s Love Story 💕" if len(names) >= 2 else "Your Love Story 💕"

        # Title with romantic styling
        ax.text(0.5, 0.7, title_text, fontsize=28,
                color=COLORS['love_dark'], ha='center', va='center',
                fontweight='bold', transform=ax.transAxes)

        # Subtitle
        ax.text(0.5, 0.35, date_range, fontsize=14,
                color=COLORS['text_secondary'], ha='center', va='center',
                transform=ax.transAxes)

        # Heart decoration
        ax.text(0.5, 0.05, "❤️ 💕 ❤️", fontsize=18, ha='center', va='center',
                transform=ax.transAxes)

    def _render_relationship_rating(self, ax):
        """Render rating box with score and romantic styling."""
        self._setup_card(ax, "LOVE SCORE")
        ax.axis('off')

        label, desc, score = self.sentiment.calculate_relationship_rating()

        # Heart-shaped score display with gradient circle
        circle = plt.Circle((0.5, 0.6), 0.25, color=COLORS['love_pink'],
                            fill=False, linewidth=5, transform=ax.transAxes)
        ax.add_patch(circle)

        # Inner fill
        circle_fill = plt.Circle((0.5, 0.6), 0.23, color=COLORS['love_pink'],
                                 alpha=0.15, transform=ax.transAxes)
        ax.add_patch(circle_fill)

        # Score text with heart
        ax.text(0.5, 0.62, f"{score:.0f}", fontsize=34, color=COLORS['love_dark'],
                ha='center', va='center', fontweight='bold', transform=ax.transAxes)
        ax.text(0.5, 0.45, "💕", fontsize=14, ha='center', va='center', transform=ax.transAxes)

        # Label
        ax.text(0.5, 0.25, label, fontsize=16, color=COLORS['love_dark'],
                ha='center', va='center', fontweight='bold', transform=ax.transAxes)

        # Description
        ax.text(0.5, 0.08, desc, fontsize=8, color=COLORS['text_secondary'],
                ha='center', va='center', wrap=True, transform=ax.transAxes)

    def _render_key_insights(self, ax):
        """Render insights list with romantic styling."""
        self._setup_card(ax, "KEY INSIGHTS")
        ax.axis('off')

        insights = self.sentiment.generate_key_insights()

        y_pos = 0.85
        for i, insight in enumerate(insights[:5]):
            # Heart bullet point
            ax.text(0.05, y_pos, "💗", fontsize=10, color=COLORS['love_pink'],
                   transform=ax.transAxes)
            # Insight text (wrap long text)
            wrapped = insight[:60] + ('...' if len(insight) > 60 else '')
            ax.text(0.12, y_pos, wrapped, fontsize=9, color=COLORS['text_primary'],
                   transform=ax.transAxes, va='center')
            y_pos -= 0.17

    def _render_conversation_analysis(self, ax):
        """Render message counts table."""
        self._setup_card(ax, "CONVERSATION ANALYSIS")
        ax.axis('off')

        msg_counts = self.metrics.get_message_counts()
        double_msgs = self.metrics.get_double_messages()

        y_pos = 0.8
        for i, (sender, count) in enumerate(sorted(msg_counts.items(), key=lambda x: -x[1])):
            name = self.get_display_name(sender)
            color = COLORS['person1'] if i == 0 else COLORS['person2']

            # Name and count
            ax.text(0.1, y_pos, name, fontsize=11, color=color,
                   fontweight='bold', transform=ax.transAxes)
            ax.text(0.7, y_pos, f"{count:,}", fontsize=14, color=COLORS['text_primary'],
                   fontweight='bold', transform=ax.transAxes, ha='right')
            ax.text(0.75, y_pos, "msgs", fontsize=9, color=COLORS['text_muted'],
                   transform=ax.transAxes)
            y_pos -= 0.18

        # Quality level
        label, _, score = self.sentiment.calculate_relationship_rating()
        ax.text(0.1, y_pos, "Quality Level", fontsize=10, color=COLORS['text_secondary'],
               transform=ax.transAxes)
        ax.text(0.9, y_pos, label, fontsize=10, color=COLORS['accent_green'],
               fontweight='bold', transform=ax.transAxes, ha='right')
        y_pos -= 0.15

        # Double messages
        total_double = sum(double_msgs.values())
        ax.text(0.1, y_pos, "Double Messages", fontsize=10, color=COLORS['text_secondary'],
               transform=ax.transAxes)
        ax.text(0.9, y_pos, f"{total_double:,}", fontsize=10, color=COLORS['text_primary'],
               transform=ax.transAxes, ha='right')

    def _render_balance_of_power(self, ax):
        """Render horizontal bar chart of message ratio."""
        self._setup_card(ax, "BALANCE OF POWER")

        ratio = self.metrics.get_message_ratio()
        sorted_ratio = sorted(ratio.items(), key=lambda x: -x[1])

        if len(sorted_ratio) >= 2:
            names = [self.get_display_name(s[0]) for s in sorted_ratio]
            values = [s[1] for s in sorted_ratio]
            colors = [COLORS['person1'], COLORS['person2']]

            # Horizontal stacked bar
            ax.barh([0], [values[0]], color=colors[0], height=0.4, label=names[0])
            ax.barh([0], [values[1]], left=[values[0]], color=colors[1], height=0.4, label=names[1])

            # Percentage labels
            ax.text(values[0]/2, 0, f"{values[0]:.1f}%", ha='center', va='center',
                   color='white', fontsize=12, fontweight='bold')
            ax.text(values[0] + values[1]/2, 0, f"{values[1]:.1f}%", ha='center', va='center',
                   color='white', fontsize=12, fontweight='bold')

            # Name labels
            ax.text(values[0]/2, -0.35, names[0], ha='center', va='center',
                   color=colors[0], fontsize=10)
            ax.text(values[0] + values[1]/2, -0.35, names[1], ha='center', va='center',
                   color=colors[1], fontsize=10)

        ax.set_xlim(0, 100)
        ax.set_ylim(-0.6, 0.6)
        ax.axis('off')

    def _render_direction_stats(self, ax):
        """Render conversation initiation stats."""
        self._setup_card(ax, "DIRECTION OF CONVERSATION")
        ax.axis('off')

        initiations = self.metrics.get_conversation_initiations()
        total = sum(initiations.values())

        y_pos = 0.75
        ax.text(0.5, 0.9, "Who starts conversations", fontsize=10,
               color=COLORS['text_secondary'], ha='center', transform=ax.transAxes)

        for i, (sender, count) in enumerate(sorted(initiations.items(), key=lambda x: -x[1])):
            name = self.get_display_name(sender)
            pct = (count / total * 100) if total > 0 else 0
            color = COLORS['person1'] if i == 0 else COLORS['person2']

            # Progress bar
            bar_width = pct / 100 * 0.7
            ax.add_patch(mpatches.Rectangle((0.15, y_pos - 0.05), 0.7, 0.08,
                        facecolor=COLORS['card_border'], transform=ax.transAxes))
            ax.add_patch(mpatches.Rectangle((0.15, y_pos - 0.05), bar_width, 0.08,
                        facecolor=color, transform=ax.transAxes))

            ax.text(0.1, y_pos, name, fontsize=10, color=color,
                   transform=ax.transAxes, ha='right', va='center')
            ax.text(0.9, y_pos, f"{pct:.0f}%", fontsize=10, color=COLORS['text_primary'],
                   transform=ax.transAxes, ha='left', va='center')

            y_pos -= 0.25

        ax.text(0.5, 0.1, f"Total: {total} conversations started", fontsize=9,
               color=COLORS['text_muted'], ha='center', transform=ax.transAxes)

    def _render_responding_metrics(self, ax):
        """Render response time statistics."""
        self._setup_card(ax, "RESPONDING")
        ax.axis('off')

        immediate = self.metrics.get_immediate_replies_percentage()
        avg_response = self.metrics.get_average_response_time()
        median_response = self.metrics.get_median_response_time()

        metrics_data = [
            ("Immediate Replies", f"{np.mean(list(immediate.values())):.1f}%", COLORS['accent_green']),
            ("Avg Response Time", f"{np.mean(list(avg_response.values())):.1f} min", COLORS['accent_orange']),
            ("Median Response", f"{np.mean(list(median_response.values())):.1f} min", COLORS['accent_cyan']),
        ]

        y_pos = 0.8
        for label, value, color in metrics_data:
            ax.text(0.1, y_pos, label, fontsize=10, color=COLORS['text_secondary'],
                   transform=ax.transAxes)
            ax.text(0.9, y_pos, value, fontsize=12, color=color,
                   fontweight='bold', transform=ax.transAxes, ha='right')
            y_pos -= 0.22

        # Per-person breakdown
        y_pos -= 0.05
        ax.text(0.5, y_pos, "By Person:", fontsize=9, color=COLORS['text_muted'],
               ha='center', transform=ax.transAxes)
        y_pos -= 0.12

        for i, (sender, time) in enumerate(sorted(avg_response.items(), key=lambda x: x[1])):
            name = self.get_display_name(sender)
            color = COLORS['person1'] if i == 0 else COLORS['person2']
            ax.text(0.15, y_pos, f"{name}: {time:.1f} min avg", fontsize=9,
                   color=color, transform=ax.transAxes)
            y_pos -= 0.1

    def _render_chat_focus_pie(self, ax):
        """Render topic distribution pie chart."""
        self._setup_card(ax, "CHAT FOCUS")

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

        colors = COLORS['chart_colors'][:len(labels)]

        wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.0f%%',
                                          colors=colors, startangle=90,
                                          pctdistance=0.75)

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)

        # Legend
        ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(0.9, 0.5),
                 fontsize=8, frameon=False,
                 labelcolor=COLORS['text_secondary'])

    def _render_message_analysis(self, ax):
        """Render word/character statistics."""
        self._setup_card(ax, "MESSAGE ANALYSIS")
        ax.axis('off')

        word_counts = self.metrics.get_word_counts()
        unique_words = self.metrics.get_unique_words()
        avg_length = self.metrics.get_average_message_length()
        char_counts = self.metrics.get_character_counts()

        y_pos = 0.85

        # Total words
        total_words = sum(word_counts.values())
        ax.text(0.1, y_pos, "Total Words", fontsize=10, color=COLORS['text_secondary'],
               transform=ax.transAxes)
        ax.text(0.9, y_pos, f"{total_words:,}", fontsize=12, color=COLORS['text_primary'],
               fontweight='bold', transform=ax.transAxes, ha='right')
        y_pos -= 0.18

        # Per person words
        for i, (sender, count) in enumerate(sorted(word_counts.items(), key=lambda x: -x[1])):
            name = self.get_display_name(sender)
            color = COLORS['person1'] if i == 0 else COLORS['person2']
            ax.text(0.15, y_pos, f"  {name}", fontsize=9, color=color, transform=ax.transAxes)
            ax.text(0.9, y_pos, f"{count:,}", fontsize=10, color=COLORS['text_secondary'],
                   transform=ax.transAxes, ha='right')
            y_pos -= 0.12

        y_pos -= 0.05

        # Unique words
        ax.text(0.1, y_pos, "Unique Words", fontsize=10, color=COLORS['text_secondary'],
               transform=ax.transAxes)
        for i, (sender, count) in enumerate(sorted(unique_words.items(), key=lambda x: -x[1])):
            name = self.get_display_name(sender)[:3]
            ax.text(0.7 + i*0.15, y_pos, f"{count:,}", fontsize=10,
                   color=COLORS['person1'] if i == 0 else COLORS['person2'],
                   transform=ax.transAxes, ha='right')
        y_pos -= 0.15

        # Avg message length
        ax.text(0.1, y_pos, "Avg Words/Msg", fontsize=10, color=COLORS['text_secondary'],
               transform=ax.transAxes)
        avg_all = np.mean(list(avg_length.values()))
        ax.text(0.9, y_pos, f"{avg_all:.1f}", fontsize=10, color=COLORS['text_primary'],
               transform=ax.transAxes, ha='right')

    def _render_content_analysis(self, ax):
        """Render media counts comparison table."""
        self._setup_card(ax, "CONTENT ANALYSIS")
        ax.axis('off')

        emoji_counts = self.metrics.get_emoji_counts()
        media_counts = self.metrics.get_media_counts()
        link_counts = self.metrics.get_link_counts()
        call_counts = self.metrics.get_call_counts()

        # Prepare data rows
        sorted_participants = sorted(self.participants,
                                    key=lambda x: self.metrics.get_message_counts().get(x, 0),
                                    reverse=True)

        # Header
        y_pos = 0.88
        ax.text(0.4, y_pos, self.get_display_name(sorted_participants[0])[:6], fontsize=9,
               color=COLORS['person1'], fontweight='bold', transform=ax.transAxes, ha='center')
        if len(sorted_participants) > 1:
            ax.text(0.7, y_pos, self.get_display_name(sorted_participants[1])[:6], fontsize=9,
                   color=COLORS['person2'], fontweight='bold', transform=ax.transAxes, ha='center')
        y_pos -= 0.12

        # Data rows
        rows = [
            ("Emojis", emoji_counts),
            ("Images", {s: media_counts.get(s, {}).get('images', 0) for s in sorted_participants}),
            ("Videos", {s: media_counts.get(s, {}).get('videos', 0) for s in sorted_participants}),
            ("Audio", {s: media_counts.get(s, {}).get('audio', 0) for s in sorted_participants}),
            ("Links", link_counts),
            ("Video Calls", {s: call_counts.get(s, {}).get('video_calls', 0) for s in sorted_participants}),
        ]

        for label, data in rows:
            ax.text(0.05, y_pos, label, fontsize=9, color=COLORS['text_secondary'],
                   transform=ax.transAxes)

            val1 = data.get(sorted_participants[0], 0)
            ax.text(0.4, y_pos, f"{val1:,}", fontsize=9, color=COLORS['person1'],
                   transform=ax.transAxes, ha='center')

            if len(sorted_participants) > 1:
                val2 = data.get(sorted_participants[1], 0)
                ax.text(0.7, y_pos, f"{val2:,}", fontsize=9, color=COLORS['person2'],
                       transform=ax.transAxes, ha='center')

            y_pos -= 0.11

    def _render_messaging_heatmap(self, ax):
        """Render 7x24 activity heatmap with romantic colors."""
        self._setup_card(ax, "WHEN YOU TALK THE MOST")

        heatmap_data = self.metrics.get_hourly_heatmap()

        # Day labels
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        # Create romantic pink colormap
        from matplotlib.colors import LinearSegmentedColormap
        romantic_colors = ['#fff5f7', '#ffe4ec', '#ffb6c1', '#ff6b9d', '#c44569']
        romantic_cmap = LinearSegmentedColormap.from_list('romantic', romantic_colors)

        # Create heatmap
        sns.heatmap(heatmap_data, ax=ax, cmap=romantic_cmap, cbar=True,
                   xticklabels=[f'{h}' for h in range(24)],
                   yticklabels=days, linewidths=0.5, linecolor='#ffe4ec')

        ax.set_xlabel('Hour of Day', color=COLORS['text_secondary'], fontsize=10)
        ax.set_ylabel('', color=COLORS['text_secondary'])

        # Style ticks
        ax.tick_params(colors=COLORS['text_secondary'], labelsize=8)
        plt.setp(ax.get_xticklabels(), rotation=0)
        plt.setp(ax.get_yticklabels(), rotation=0)

    def _render_growth_timeline(self, ax):
        """Render relationship growth over time."""
        self._setup_card(ax, "RELATIONSHIP GROWTH OVER TIME")

        growth_data = self.sentiment.get_relationship_growth_data()
        months = growth_data['months']
        volumes = growth_data['message_volumes']

        if len(months) < 2:
            ax.text(0.5, 0.5, "Not enough data for timeline", ha='center', va='center',
                   color=COLORS['text_muted'], transform=ax.transAxes)
            return

        # Create x positions
        x = np.arange(len(months))

        # Plot message volume
        ax.fill_between(x, volumes, alpha=0.3, color=COLORS['accent_purple'])
        ax.plot(x, volumes, color=COLORS['accent_purple'], linewidth=2, label='Messages')

        # Plot call frequency if available
        calls = growth_data.get('call_counts', [])
        if calls and any(c > 0 for c in calls):
            ax2 = ax.twinx()
            ax2.plot(x, calls, color=COLORS['accent_orange'], linewidth=2,
                    linestyle='--', label='Calls')
            ax2.set_ylabel('Calls', color=COLORS['accent_orange'], fontsize=10)
            ax2.tick_params(colors=COLORS['accent_orange'], labelsize=8)
            ax2.spines['right'].set_color(COLORS['accent_orange'])

        # Style main axis
        ax.set_xlim(0, len(months) - 1)
        ax.set_ylim(0, max(volumes) * 1.1)

        # Show every 3rd month label
        tick_positions = list(range(0, len(months), max(1, len(months) // 10)))
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([months[i] for i in tick_positions], rotation=45, ha='right')

        ax.set_ylabel('Messages', color=COLORS['accent_purple'], fontsize=10)
        ax.tick_params(colors=COLORS['text_secondary'], labelsize=8)

        # Growth trend annotation
        trend = growth_data.get('growth_trend', 'stable')
        trend_colors = {'growing': COLORS['accent_green'], 'stable': COLORS['accent_cyan'],
                       'declining': COLORS['accent_orange']}
        ax.text(0.98, 0.95, f"Trend: {trend.title()}", fontsize=10,
               color=trend_colors.get(trend, COLORS['text_secondary']),
               transform=ax.transAxes, ha='right', va='top', fontweight='bold')

        # Add milestone markers
        milestones = growth_data.get('milestones', [])
        for date, label in milestones[:5]:  # Show first 5 milestones
            if isinstance(date, datetime):
                month_key = date.strftime('%Y-%m')
                if month_key in months:
                    idx = months.index(month_key)
                    ax.axvline(x=idx, color=COLORS['accent_green'], linestyle=':',
                              alpha=0.5, linewidth=1)

    def _render_milestones(self, ax):
        """Render key milestones with romantic styling."""
        self._setup_card(ax, "YOUR LOVE MILESTONES")
        ax.axis('off')

        milestones = self.sentiment.detect_milestones()

        if not milestones:
            ax.text(0.5, 0.5, "Your journey is just beginning! 💕", ha='center', va='center',
                   color=COLORS['text_muted'], transform=ax.transAxes)
            return

        # Show milestones horizontally
        num_milestones = min(6, len(milestones))
        spacing = 1.0 / (num_milestones + 1)

        for i, (date, label) in enumerate(milestones[:num_milestones]):
            x_pos = spacing * (i + 1)

            # Date
            if isinstance(date, datetime):
                date_str = date.strftime('%b %Y')
            else:
                date_str = str(date)[:10]

            # Heart marker instead of diamond
            ax.text(x_pos, 0.7, "💕", fontsize=16, color=COLORS['love_pink'],
                   ha='center', va='center', transform=ax.transAxes)
            ax.text(x_pos, 0.45, date_str, fontsize=9, color=COLORS['love_dark'],
                   ha='center', va='center', transform=ax.transAxes, fontweight='bold')
            ax.text(x_pos, 0.2, label, fontsize=8, color=COLORS['text_primary'],
                   ha='center', va='center', transform=ax.transAxes, wrap=True)


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
