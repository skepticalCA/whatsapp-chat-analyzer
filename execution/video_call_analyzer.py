#!/usr/bin/env python3
"""
Video Call Analyzer Module
Comprehensive analysis of video and voice calls in the chat.
"""

import os
import sys
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_parser import parse_whatsapp_chat, Message, MessageType


# Color palette
COLORS = {
    'background': '#0a0a14',
    'card_bg': '#141428',
    'card_border': '#252550',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0c0',
    'text_muted': '#606080',
    'video_call': '#8b5cf6',  # Purple for video
    'voice_call': '#22d3ee',  # Cyan for voice
    'missed': '#ef4444',  # Red for missed
    'person1': '#3b82f6',
    'person2': '#ec4899',
    'gold': '#fbbf24',
    'green': '#10b981'
}


class VideoCallAnalyzer:
    """Analyze video and voice call patterns."""

    def __init__(self, messages: List[Message], participant_mapping: Dict[str, str]):
        self.messages = messages
        self.participant_mapping = participant_mapping
        self.participants = list(participant_mapping.keys())

        # Filter call messages
        self.video_calls = [m for m in messages if m.message_type == MessageType.VIDEO_CALL]
        self.voice_calls = [m for m in messages if m.message_type == MessageType.VOICE_CALL]
        self.missed_video = [m for m in messages if m.message_type == MessageType.MISSED_VIDEO_CALL]
        self.missed_voice = [m for m in messages if m.message_type == MessageType.MISSED_VOICE_CALL]

        self.all_calls = self.video_calls + self.voice_calls + self.missed_video + self.missed_voice

    def get_display_name(self, raw_name: str) -> str:
        return self.participant_mapping.get(raw_name, raw_name)

    def get_call_summary(self) -> Dict:
        """Get overall call statistics."""
        total_video = len(self.video_calls)
        total_voice = len(self.voice_calls)
        missed_video = len(self.missed_video)
        missed_voice = len(self.missed_voice)

        # Duration stats for answered calls
        video_durations = [c.call_duration_seconds for c in self.video_calls if c.call_duration_seconds]
        voice_durations = [c.call_duration_seconds for c in self.voice_calls if c.call_duration_seconds]

        total_video_time = sum(video_durations) if video_durations else 0
        total_voice_time = sum(voice_durations) if voice_durations else 0

        return {
            'total_video_calls': total_video,
            'total_voice_calls': total_voice,
            'total_calls': total_video + total_voice,
            'missed_video_calls': missed_video,
            'missed_voice_calls': missed_voice,
            'total_missed': missed_video + missed_voice,
            'answer_rate': ((total_video + total_voice) / max(total_video + total_voice + missed_video + missed_voice, 1)) * 100,
            'total_video_time_hours': total_video_time / 3600,
            'total_voice_time_hours': total_voice_time / 3600,
            'total_call_time_hours': (total_video_time + total_voice_time) / 3600,
            'avg_video_duration_min': np.mean(video_durations) / 60 if video_durations else 0,
            'avg_voice_duration_min': np.mean(voice_durations) / 60 if voice_durations else 0,
            'longest_video_call_min': max(video_durations) / 60 if video_durations else 0,
            'longest_voice_call_min': max(voice_durations) / 60 if voice_durations else 0,
            'median_video_duration_min': np.median(video_durations) / 60 if video_durations else 0,
        }

    def get_calls_by_person(self) -> Dict[str, Dict]:
        """Get call statistics per person (who initiated)."""
        stats = {sender: {
            'video_calls': 0,
            'voice_calls': 0,
            'missed_video': 0,
            'missed_voice': 0,
            'total_video_time': 0,
            'total_voice_time': 0,
            'call_durations': []
        } for sender in self.participants}

        for call in self.video_calls:
            if call.sender in stats:
                stats[call.sender]['video_calls'] += 1
                if call.call_duration_seconds:
                    stats[call.sender]['total_video_time'] += call.call_duration_seconds
                    stats[call.sender]['call_durations'].append(call.call_duration_seconds)

        for call in self.voice_calls:
            if call.sender in stats:
                stats[call.sender]['voice_calls'] += 1
                if call.call_duration_seconds:
                    stats[call.sender]['total_voice_time'] += call.call_duration_seconds
                    stats[call.sender]['call_durations'].append(call.call_duration_seconds)

        for call in self.missed_video:
            if call.sender in stats:
                stats[call.sender]['missed_video'] += 1

        for call in self.missed_voice:
            if call.sender in stats:
                stats[call.sender]['missed_voice'] += 1

        # Calculate averages
        for sender in stats:
            durations = stats[sender]['call_durations']
            stats[sender]['avg_call_duration_min'] = np.mean(durations) / 60 if durations else 0
            stats[sender]['total_calls'] = stats[sender]['video_calls'] + stats[sender]['voice_calls']
            stats[sender]['total_missed'] = stats[sender]['missed_video'] + stats[sender]['missed_voice']

        return stats

    def get_monthly_call_trends(self) -> Dict[str, Dict]:
        """Get call frequency and duration by month."""
        monthly = defaultdict(lambda: {
            'video_calls': 0,
            'voice_calls': 0,
            'total_duration': 0,
            'call_count': 0
        })

        for call in self.video_calls + self.voice_calls:
            month_key = call.timestamp.strftime('%Y-%m')
            if call.message_type == MessageType.VIDEO_CALL:
                monthly[month_key]['video_calls'] += 1
            else:
                monthly[month_key]['voice_calls'] += 1
            monthly[month_key]['call_count'] += 1
            if call.call_duration_seconds:
                monthly[month_key]['total_duration'] += call.call_duration_seconds

        # Convert total_duration to hours
        for month in monthly:
            monthly[month]['total_duration_hours'] = monthly[month]['total_duration'] / 3600

        return dict(sorted(monthly.items()))

    def get_hourly_distribution(self) -> Dict[int, int]:
        """Get call distribution by hour of day."""
        hourly = defaultdict(int)
        for call in self.video_calls + self.voice_calls:
            hourly[call.timestamp.hour] += 1
        return dict(hourly)

    def get_daily_distribution(self) -> Dict[int, int]:
        """Get call distribution by day of week."""
        daily = defaultdict(int)
        for call in self.video_calls + self.voice_calls:
            daily[call.timestamp.weekday()] += 1
        return dict(daily)

    def get_call_heatmap(self) -> np.ndarray:
        """Get 7x24 heatmap of calls (day of week x hour)."""
        heatmap = np.zeros((7, 24))
        for call in self.video_calls + self.voice_calls:
            dow = call.timestamp.weekday()
            hour = call.timestamp.hour
            heatmap[dow, hour] += 1
        return heatmap

    def get_longest_calls(self, top_n: int = 10) -> List[Dict]:
        """Get top N longest calls."""
        all_answered = self.video_calls + self.voice_calls
        with_duration = [(c, c.call_duration_seconds) for c in all_answered if c.call_duration_seconds]
        sorted_calls = sorted(with_duration, key=lambda x: -x[1])[:top_n]

        return [{
            'date': call.timestamp.strftime('%b %d, %Y'),
            'time': call.timestamp.strftime('%I:%M %p'),
            'type': 'Video' if call.message_type == MessageType.VIDEO_CALL else 'Voice',
            'duration_min': duration / 60,
            'duration_str': self._format_duration(duration),
            'initiated_by': self.get_display_name(call.sender)
        } for call, duration in sorted_calls]

    def get_call_streaks(self) -> Dict:
        """Analyze consecutive days with calls."""
        if not self.all_calls:
            return {'longest_streak': 0, 'current_streak': 0, 'total_call_days': 0}

        call_dates = sorted(set(c.timestamp.date() for c in self.video_calls + self.voice_calls))

        if not call_dates:
            return {'longest_streak': 0, 'current_streak': 0, 'total_call_days': 0}

        longest_streak = 1
        current_streak = 1

        for i in range(1, len(call_dates)):
            if (call_dates[i] - call_dates[i-1]).days == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

        # Check if current streak includes today
        today = datetime.now().date()
        if call_dates and (today - call_dates[-1]).days <= 1:
            final_streak = current_streak
        else:
            final_streak = 0

        return {
            'longest_streak': longest_streak,
            'current_streak': final_streak,
            'total_call_days': len(call_dates)
        }

    def get_call_duration_distribution(self) -> Dict[str, int]:
        """Categorize calls by duration."""
        categories = {
            'Quick (<5 min)': 0,
            'Short (5-15 min)': 0,
            'Medium (15-30 min)': 0,
            'Long (30-60 min)': 0,
            'Very Long (1-2 hr)': 0,
            'Marathon (2+ hr)': 0
        }

        for call in self.video_calls + self.voice_calls:
            if call.call_duration_seconds:
                mins = call.call_duration_seconds / 60
                if mins < 5:
                    categories['Quick (<5 min)'] += 1
                elif mins < 15:
                    categories['Short (5-15 min)'] += 1
                elif mins < 30:
                    categories['Medium (15-30 min)'] += 1
                elif mins < 60:
                    categories['Long (30-60 min)'] += 1
                elif mins < 120:
                    categories['Very Long (1-2 hr)'] += 1
                else:
                    categories['Marathon (2+ hr)'] += 1

        return categories

    def _format_duration(self, seconds: int) -> str:
        """Format duration in human readable form."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    def get_all_analysis(self) -> Dict:
        """Get complete call analysis."""
        return {
            'summary': self.get_call_summary(),
            'by_person': self.get_calls_by_person(),
            'monthly_trends': self.get_monthly_call_trends(),
            'hourly_distribution': self.get_hourly_distribution(),
            'daily_distribution': self.get_daily_distribution(),
            'longest_calls': self.get_longest_calls(),
            'streaks': self.get_call_streaks(),
            'duration_distribution': self.get_call_duration_distribution()
        }


class VideoCallDashboard:
    """Generate video call analysis dashboard."""

    def __init__(self, analyzer: VideoCallAnalyzer, participant_mapping: Dict[str, str]):
        self.analyzer = analyzer
        self.participant_mapping = participant_mapping
        self.participants = list(participant_mapping.keys())

        plt.style.use('dark_background')

    def get_display_name(self, raw_name: str) -> str:
        return self.participant_mapping.get(raw_name, raw_name)

    def create_dashboard(self, output_path: str, figsize=(22, 28)):
        """Generate the complete video call dashboard."""
        fig = plt.figure(figsize=figsize, facecolor=COLORS['background'])

        gs = GridSpec(7, 3, figure=fig, hspace=0.3, wspace=0.25,
                      left=0.05, right=0.95, top=0.95, bottom=0.03)

        # Row 0: Header
        ax_header = fig.add_subplot(gs[0, :])
        self._render_header(ax_header)

        # Row 1: Summary stats | Call type breakdown | By person
        ax_summary = fig.add_subplot(gs[1, 0])
        ax_types = fig.add_subplot(gs[1, 1])
        ax_person = fig.add_subplot(gs[1, 2])

        # Row 2: Monthly trends (full width)
        ax_monthly = fig.add_subplot(gs[2, :])

        # Row 3: Hourly distribution | Daily distribution | Duration distribution
        ax_hourly = fig.add_subplot(gs[3, 0])
        ax_daily = fig.add_subplot(gs[3, 1])
        ax_duration = fig.add_subplot(gs[3, 2])

        # Row 4: Call heatmap (full width)
        ax_heatmap = fig.add_subplot(gs[4, :])

        # Row 5: Longest calls | Streaks
        ax_longest = fig.add_subplot(gs[5, :2])
        ax_streaks = fig.add_subplot(gs[5, 2])

        # Row 6: Fun facts
        ax_facts = fig.add_subplot(gs[6, :])

        # Render all sections
        self._render_summary(ax_summary)
        self._render_call_types(ax_types)
        self._render_by_person(ax_person)
        self._render_monthly_trends(ax_monthly)
        self._render_hourly(ax_hourly)
        self._render_daily(ax_daily)
        self._render_duration_dist(ax_duration)
        self._render_heatmap(ax_heatmap)
        self._render_longest_calls(ax_longest)
        self._render_streaks(ax_streaks)
        self._render_fun_facts(ax_facts)

        plt.savefig(output_path, dpi=150, facecolor=COLORS['background'],
                    edgecolor='none', bbox_inches='tight')
        plt.close()
        print(f"Video call dashboard saved to {output_path}")

    def _setup_card(self, ax, title: str = None, title_color=None):
        ax.set_facecolor(COLORS['card_bg'])
        for spine in ax.spines.values():
            spine.set_color(COLORS['card_border'])
        if title:
            ax.set_title(title, color=title_color or COLORS['text_primary'],
                        fontsize=12, fontweight='bold', loc='left', pad=10)

    def _render_header(self, ax):
        ax.set_facecolor(COLORS['background'])
        ax.axis('off')

        summary = self.analyzer.get_call_summary()
        total_hours = summary['total_call_time_hours']

        ax.text(0.5, 0.7, "Video & Voice Call Analysis", fontsize=28,
                color=COLORS['text_primary'], ha='center', va='center',
                fontweight='bold', transform=ax.transAxes)

        ax.text(0.5, 0.35, f"Total: {summary['total_calls']:,} calls | {total_hours:.1f} hours together",
                fontsize=14, color=COLORS['video_call'], ha='center', va='center',
                transform=ax.transAxes)

        p1 = self.get_display_name(self.participants[0])
        p2 = self.get_display_name(self.participants[1]) if len(self.participants) > 1 else ""
        ax.text(0.5, 0.1, f"{p1} & {p2}", fontsize=12,
                color=COLORS['text_muted'], ha='center', transform=ax.transAxes)

    def _render_summary(self, ax):
        self._setup_card(ax, "Call Summary")
        ax.axis('off')

        summary = self.analyzer.get_call_summary()

        metrics = [
            ("Total Calls", f"{summary['total_calls']:,}", COLORS['video_call']),
            ("Video Calls", f"{summary['total_video_calls']:,}", COLORS['video_call']),
            ("Voice Calls", f"{summary['total_voice_calls']:,}", COLORS['voice_call']),
            ("Total Time", f"{summary['total_call_time_hours']:.1f} hrs", COLORS['gold']),
            ("Answer Rate", f"{summary['answer_rate']:.1f}%", COLORS['green']),
            ("Missed Calls", f"{summary['total_missed']:,}", COLORS['missed']),
        ]

        y_pos = 0.85
        for label, value, color in metrics:
            ax.text(0.1, y_pos, label, fontsize=10, color=COLORS['text_secondary'],
                   transform=ax.transAxes)
            ax.text(0.9, y_pos, value, fontsize=11, color=color,
                   fontweight='bold', ha='right', transform=ax.transAxes)
            y_pos -= 0.14

    def _render_call_types(self, ax):
        self._setup_card(ax, "Call Type Breakdown")

        summary = self.analyzer.get_call_summary()

        labels = ['Video Calls', 'Voice Calls', 'Missed Video', 'Missed Voice']
        sizes = [
            summary['total_video_calls'],
            summary['total_voice_calls'],
            summary['missed_video_calls'],
            summary['missed_voice_calls']
        ]
        colors = [COLORS['video_call'], COLORS['voice_call'], '#7c3aed', '#ef4444']

        # Filter out zeros
        filtered = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
        if filtered:
            labels, sizes, colors = zip(*filtered)
            wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.0f%%',
                                              colors=colors, startangle=90)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(9)

            ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(0.85, 0.5),
                     fontsize=8, frameon=False, labelcolor=COLORS['text_secondary'])

    def _render_by_person(self, ax):
        self._setup_card(ax, "Who Initiates Calls")
        ax.axis('off')

        by_person = self.analyzer.get_calls_by_person()

        y_pos = 0.8
        total_calls = sum(p['total_calls'] for p in by_person.values())

        for i, (sender, stats) in enumerate(by_person.items()):
            name = self.get_display_name(sender)
            color = COLORS['person1'] if i == 0 else COLORS['person2']
            pct = (stats['total_calls'] / max(total_calls, 1)) * 100

            ax.text(0.1, y_pos, name, fontsize=12, color=color,
                   fontweight='bold', transform=ax.transAxes)

            # Progress bar
            bar_width = pct / 100 * 0.6
            ax.add_patch(mpatches.Rectangle((0.1, y_pos - 0.12), 0.6, 0.06,
                        facecolor=COLORS['card_border'], transform=ax.transAxes))
            ax.add_patch(mpatches.Rectangle((0.1, y_pos - 0.12), bar_width, 0.06,
                        facecolor=color, transform=ax.transAxes))

            ax.text(0.75, y_pos - 0.09, f"{stats['total_calls']} ({pct:.0f}%)",
                   fontsize=10, color=COLORS['text_secondary'],
                   transform=ax.transAxes, va='center')

            # Call time
            total_time = (stats['total_video_time'] + stats['total_voice_time']) / 3600
            ax.text(0.1, y_pos - 0.22, f"  Total time: {total_time:.1f} hrs",
                   fontsize=9, color=COLORS['text_muted'], transform=ax.transAxes)

            y_pos -= 0.45

    def _render_monthly_trends(self, ax):
        self._setup_card(ax, "Monthly Call Trends")

        monthly = self.analyzer.get_monthly_call_trends()
        months = list(monthly.keys())
        video = [monthly[m]['video_calls'] for m in months]
        voice = [monthly[m]['voice_calls'] for m in months]
        duration = [monthly[m]['total_duration_hours'] for m in months]

        x = np.arange(len(months))

        # Bar chart for call counts
        ax.bar(x - 0.2, video, 0.4, label='Video Calls', color=COLORS['video_call'], alpha=0.8)
        ax.bar(x + 0.2, voice, 0.4, label='Voice Calls', color=COLORS['voice_call'], alpha=0.8)

        # Line for duration on secondary axis
        ax2 = ax.twinx()
        ax2.plot(x, duration, color=COLORS['gold'], linewidth=2, marker='o',
                markersize=4, label='Hours')
        ax2.set_ylabel('Hours', color=COLORS['gold'], fontsize=10)
        ax2.tick_params(colors=COLORS['gold'], labelsize=8)

        # Style
        tick_positions = list(range(0, len(months), max(1, len(months) // 8)))
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([months[i] for i in tick_positions], rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('Number of Calls', color=COLORS['text_secondary'], fontsize=10)
        ax.tick_params(colors=COLORS['text_secondary'], labelsize=8)
        ax.legend(loc='upper left', frameon=False, fontsize=9)

    def _render_hourly(self, ax):
        self._setup_card(ax, "Calls by Hour")

        hourly = self.analyzer.get_hourly_distribution()
        hours = list(range(24))
        counts = [hourly.get(h, 0) for h in hours]

        ax.bar(hours, counts, color=COLORS['video_call'], alpha=0.8)
        ax.set_xlabel('Hour', fontsize=9, color=COLORS['text_secondary'])
        ax.set_ylabel('Calls', fontsize=9, color=COLORS['text_secondary'])
        ax.set_xticks([0, 6, 12, 18, 23])
        ax.set_xticklabels(['12AM', '6AM', '12PM', '6PM', '11PM'], fontsize=8)
        ax.tick_params(colors=COLORS['text_secondary'], labelsize=8)

    def _render_daily(self, ax):
        self._setup_card(ax, "Calls by Day")

        daily = self.analyzer.get_daily_distribution()
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        counts = [daily.get(i, 0) for i in range(7)]

        bars = ax.bar(days, counts, color=COLORS['voice_call'], alpha=0.8)

        # Highlight weekend
        bars[5].set_color(COLORS['gold'])
        bars[6].set_color(COLORS['gold'])

        ax.set_ylabel('Calls', fontsize=9, color=COLORS['text_secondary'])
        ax.tick_params(colors=COLORS['text_secondary'], labelsize=8)

    def _render_duration_dist(self, ax):
        self._setup_card(ax, "Call Duration Distribution")

        dist = self.analyzer.get_call_duration_distribution()
        labels = list(dist.keys())
        values = list(dist.values())

        colors = [COLORS['voice_call'], COLORS['video_call'], COLORS['green'],
                 COLORS['gold'], '#f59e0b', COLORS['missed']]

        bars = ax.barh(labels, values, color=colors[:len(labels)], alpha=0.8)
        ax.set_xlabel('Number of Calls', fontsize=9, color=COLORS['text_secondary'])
        ax.tick_params(colors=COLORS['text_secondary'], labelsize=8)

        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                   str(val), va='center', fontsize=8, color=COLORS['text_secondary'])

    def _render_heatmap(self, ax):
        self._setup_card(ax, "Call Activity Heatmap (Day x Hour)")

        heatmap = self.analyzer.get_call_heatmap()
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        sns.heatmap(heatmap, ax=ax, cmap='Purples', cbar=True,
                   xticklabels=[f'{h}' for h in range(24)],
                   yticklabels=days, linewidths=0.5, linecolor=COLORS['card_border'])

        ax.set_xlabel('Hour of Day', color=COLORS['text_secondary'], fontsize=10)
        ax.tick_params(colors=COLORS['text_secondary'], labelsize=8)

    def _render_longest_calls(self, ax):
        self._setup_card(ax, "Top 10 Longest Calls")
        ax.axis('off')

        longest = self.analyzer.get_longest_calls(10)

        if not longest:
            ax.text(0.5, 0.5, "No call duration data available",
                   color=COLORS['text_muted'], ha='center', transform=ax.transAxes)
            return

        # Headers
        ax.text(0.02, 0.92, "#", fontsize=9, color=COLORS['text_muted'],
               fontweight='bold', transform=ax.transAxes)
        ax.text(0.08, 0.92, "Date", fontsize=9, color=COLORS['text_muted'],
               fontweight='bold', transform=ax.transAxes)
        ax.text(0.30, 0.92, "Time", fontsize=9, color=COLORS['text_muted'],
               fontweight='bold', transform=ax.transAxes)
        ax.text(0.48, 0.92, "Type", fontsize=9, color=COLORS['text_muted'],
               fontweight='bold', transform=ax.transAxes)
        ax.text(0.62, 0.92, "Duration", fontsize=9, color=COLORS['text_muted'],
               fontweight='bold', transform=ax.transAxes)
        ax.text(0.82, 0.92, "Started By", fontsize=9, color=COLORS['text_muted'],
               fontweight='bold', transform=ax.transAxes)

        y_pos = 0.82
        for i, call in enumerate(longest, 1):
            color = COLORS['gold'] if i <= 3 else COLORS['text_secondary']

            ax.text(0.02, y_pos, str(i), fontsize=9, color=color, transform=ax.transAxes)
            ax.text(0.08, y_pos, call['date'], fontsize=9, color=COLORS['text_secondary'],
                   transform=ax.transAxes)
            ax.text(0.30, y_pos, call['time'], fontsize=9, color=COLORS['text_secondary'],
                   transform=ax.transAxes)

            type_color = COLORS['video_call'] if call['type'] == 'Video' else COLORS['voice_call']
            ax.text(0.48, y_pos, call['type'], fontsize=9, color=type_color,
                   transform=ax.transAxes)

            ax.text(0.62, y_pos, call['duration_str'], fontsize=9, color=color,
                   fontweight='bold', transform=ax.transAxes)
            ax.text(0.82, y_pos, call['initiated_by'], fontsize=9,
                   color=COLORS['text_secondary'], transform=ax.transAxes)

            y_pos -= 0.085

    def _render_streaks(self, ax):
        self._setup_card(ax, "Call Streaks")
        ax.axis('off')

        streaks = self.analyzer.get_call_streaks()

        metrics = [
            ("Longest Streak", f"{streaks['longest_streak']} days", COLORS['gold']),
            ("Current Streak", f"{streaks['current_streak']} days", COLORS['green']),
            ("Days with Calls", f"{streaks['total_call_days']}", COLORS['video_call']),
        ]

        y_pos = 0.75
        for label, value, color in metrics:
            ax.text(0.1, y_pos, label, fontsize=11, color=COLORS['text_secondary'],
                   transform=ax.transAxes)
            ax.text(0.9, y_pos, value, fontsize=14, color=color,
                   fontweight='bold', ha='right', transform=ax.transAxes)
            y_pos -= 0.25

    def _render_fun_facts(self, ax):
        self._setup_card(ax, "Call Fun Facts")
        ax.axis('off')

        summary = self.analyzer.get_call_summary()
        longest = self.analyzer.get_longest_calls(1)

        facts = []

        # Total time in different units
        total_hours = summary['total_call_time_hours']
        facts.append(f"Total call time: {total_hours:.1f} hours = {total_hours/24:.1f} full days!")

        # Average per month
        monthly = self.analyzer.get_monthly_call_trends()
        if monthly:
            avg_calls = summary['total_calls'] / len(monthly)
            avg_hours = total_hours / len(monthly)
            facts.append(f"Average: {avg_calls:.0f} calls and {avg_hours:.1f} hours per month")

        # Longest call
        if longest:
            facts.append(f"Longest call: {longest[0]['duration_str']} on {longest[0]['date']}")

        # Most active hour
        hourly = self.analyzer.get_hourly_distribution()
        if hourly:
            peak_hour = max(hourly.items(), key=lambda x: x[1])
            time_str = f"{peak_hour[0]}:00" if peak_hour[0] >= 10 else f"0{peak_hour[0]}:00"
            facts.append(f"Most calls happen around {time_str} ({peak_hour[1]} calls)")

        # Video vs Voice preference
        if summary['total_video_calls'] > summary['total_voice_calls'] * 1.5:
            facts.append("You clearly prefer video calls over voice calls!")
        elif summary['total_voice_calls'] > summary['total_video_calls'] * 1.5:
            facts.append("You prefer voice calls - keeping it simple!")

        y_pos = 0.8
        for fact in facts[:5]:
            ax.text(0.05, y_pos, f"* {fact}", fontsize=10,
                   color=COLORS['text_secondary'], transform=ax.transAxes, wrap=True)
            y_pos -= 0.18


def main():
    """Run video call analysis."""
    CHAT_FILE = '/Users/arvind/PythonProjects/Chatanaylsi/_chat.txt'
    OUTPUT_PATH = '/Users/arvind/PythonProjects/Chatanaylsi/output/videocall_dashboard.png'

    PARTICIPANT_MAPPING = {
        "~~": "Arvind",
        "bae 🫶": "Palak"
    }

    print("Parsing chat file...")
    messages = parse_whatsapp_chat(CHAT_FILE)
    print(f"Parsed {len(messages):,} messages")

    print("Analyzing video calls...")
    analyzer = VideoCallAnalyzer(messages, PARTICIPANT_MAPPING)

    # Print summary
    summary = analyzer.get_call_summary()
    print("\n" + "="*60)
    print("VIDEO CALL ANALYSIS SUMMARY")
    print("="*60)
    print(f"Total Calls: {summary['total_calls']:,}")
    print(f"  - Video Calls: {summary['total_video_calls']:,}")
    print(f"  - Voice Calls: {summary['total_voice_calls']:,}")
    print(f"  - Missed Calls: {summary['total_missed']:,}")
    print(f"\nTotal Call Time: {summary['total_call_time_hours']:.1f} hours")
    print(f"  - Video: {summary['total_video_time_hours']:.1f} hours")
    print(f"  - Voice: {summary['total_voice_time_hours']:.1f} hours")
    print(f"\nAverage Call Duration:")
    print(f"  - Video: {summary['avg_video_duration_min']:.1f} minutes")
    print(f"  - Voice: {summary['avg_voice_duration_min']:.1f} minutes")
    print(f"\nLongest Video Call: {summary['longest_video_call_min']:.1f} minutes")
    print(f"Answer Rate: {summary['answer_rate']:.1f}%")

    # By person
    print("\n" + "="*60)
    print("BY PERSON")
    print("="*60)
    by_person = analyzer.get_calls_by_person()
    for sender, stats in by_person.items():
        name = PARTICIPANT_MAPPING.get(sender, sender)
        print(f"\n{name}:")
        print(f"  Initiated {stats['total_calls']} calls ({stats['video_calls']} video, {stats['voice_calls']} voice)")
        print(f"  Missed {stats['total_missed']} calls")
        total_time = (stats['total_video_time'] + stats['total_voice_time']) / 3600
        print(f"  Total call time: {total_time:.1f} hours")

    # Top calls
    print("\n" + "="*60)
    print("LONGEST CALLS")
    print("="*60)
    for i, call in enumerate(analyzer.get_longest_calls(5), 1):
        print(f"{i}. {call['duration_str']} - {call['type']} call on {call['date']} at {call['time']}")

    print("\nGenerating dashboard...")
    dashboard = VideoCallDashboard(analyzer, PARTICIPANT_MAPPING)
    dashboard.create_dashboard(OUTPUT_PATH)

    print(f"\nDashboard saved to: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
