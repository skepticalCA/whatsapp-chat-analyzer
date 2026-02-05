"""
Metrics Calculator Module
Calculates all dashboard metrics from parsed messages.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import numpy as np
from chat_parser import Message, MessageType


class MetricsCalculator:
    """Calculate comprehensive chat metrics."""

    def __init__(self, messages: List[Message], participant_mapping: Dict[str, str]):
        """
        Initialize with parsed messages and participant name mapping.

        Args:
            messages: List of parsed Message objects
            participant_mapping: Dict mapping raw names to display names
                                e.g., {"~~": "Arvind", "bae": "Palak"}
        """
        self.messages = messages
        self.participant_mapping = participant_mapping
        self.participants = list(participant_mapping.keys())

        # Filter out non-human messages for some calculations
        self.text_messages = [m for m in messages if m.message_type == MessageType.TEXT]

        # Emoji regex pattern
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"  # dingbats
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA00-\U0001FA6F"  # chess symbols
            "\U0001FA70-\U0001FAFF"  # symbols extended
            "\U00002600-\U000026FF"  # misc symbols
            "\U00002700-\U000027BF"  # dingbats
            "\U0001F000-\U0001F02F"  # mahjong
            "\U0001F0A0-\U0001F0FF"  # playing cards
            "]+", flags=re.UNICODE
        )

    def get_display_name(self, raw_name: str) -> str:
        """Get display name for a participant."""
        return self.participant_mapping.get(raw_name, raw_name)

    # ============== Message Counts ==============

    def get_message_counts(self) -> Dict[str, int]:
        """Total messages per person."""
        counts = defaultdict(int)
        for msg in self.messages:
            counts[msg.sender] += 1
        return dict(counts)

    def get_text_message_counts(self) -> Dict[str, int]:
        """Text messages only per person."""
        counts = defaultdict(int)
        for msg in self.text_messages:
            counts[msg.sender] += 1
        return dict(counts)

    def get_message_ratio(self) -> Dict[str, float]:
        """Percentage of messages from each person."""
        counts = self.get_message_counts()
        total = sum(counts.values())
        if total == 0:
            return {p: 0.0 for p in self.participants}
        return {p: (counts.get(p, 0) / total) * 100 for p in self.participants}

    # ============== Double Messages ==============

    def get_double_messages(self) -> Dict[str, int]:
        """
        Count of double-texting (2+ consecutive messages by same person).
        """
        double_counts = defaultdict(int)
        if not self.messages:
            return dict(double_counts)

        current_sender = self.messages[0].sender
        streak = 1

        for msg in self.messages[1:]:
            if msg.sender == current_sender:
                streak += 1
            else:
                if streak >= 2:
                    double_counts[current_sender] += streak - 1
                current_sender = msg.sender
                streak = 1

        # Handle last streak
        if streak >= 2:
            double_counts[current_sender] += streak - 1

        return dict(double_counts)

    # ============== Conversation Initiation ==============

    def get_conversation_initiations(self, gap_hours: int = 6) -> Dict[str, int]:
        """
        Who starts conversations (first message after gap_hours hour gap).
        """
        initiations = defaultdict(int)
        if not self.messages:
            return dict(initiations)

        gap = timedelta(hours=gap_hours)
        prev_time = self.messages[0].timestamp
        initiations[self.messages[0].sender] += 1

        for msg in self.messages[1:]:
            if msg.timestamp - prev_time >= gap:
                initiations[msg.sender] += 1
            prev_time = msg.timestamp

        return dict(initiations)

    # ============== Response Times ==============

    def get_response_times(self) -> Dict[str, List[float]]:
        """
        Calculate all response times (in minutes) for each person.
        Response = time from other person's message to this person's reply.
        """
        response_times = defaultdict(list)
        if len(self.messages) < 2:
            return dict(response_times)

        for i in range(1, len(self.messages)):
            current = self.messages[i]
            prev = self.messages[i - 1]

            # Only count if different sender (it's a response)
            if current.sender != prev.sender:
                delta = (current.timestamp - prev.timestamp).total_seconds() / 60
                # Filter out unreasonably long gaps (> 24 hours)
                if delta <= 1440:  # 24 hours in minutes
                    response_times[current.sender].append(delta)

        return dict(response_times)

    def get_average_response_time(self) -> Dict[str, float]:
        """Average response time in minutes per person."""
        response_times = self.get_response_times()
        return {
            sender: np.mean(times) if times else 0
            for sender, times in response_times.items()
        }

    def get_median_response_time(self) -> Dict[str, float]:
        """Median response time in minutes per person."""
        response_times = self.get_response_times()
        return {
            sender: np.median(times) if times else 0
            for sender, times in response_times.items()
        }

    def get_immediate_replies_percentage(self, threshold_minutes: float = 1.0) -> Dict[str, float]:
        """Percentage of replies within threshold minutes."""
        response_times = self.get_response_times()
        result = {}
        for sender, times in response_times.items():
            if not times:
                result[sender] = 0.0
            else:
                immediate = sum(1 for t in times if t <= threshold_minutes)
                result[sender] = (immediate / len(times)) * 100
        return result

    def get_first_response_time(self) -> Dict[str, float]:
        """
        Average time of first message of the day (hour of day).
        """
        first_msg_times = defaultdict(list)

        # Group by date and sender
        date_sender_first = {}
        for msg in self.messages:
            date = msg.timestamp.date()
            key = (date, msg.sender)
            if key not in date_sender_first:
                date_sender_first[key] = msg.timestamp

        for (date, sender), timestamp in date_sender_first.items():
            # Convert to hour (decimal)
            hour = timestamp.hour + timestamp.minute / 60
            first_msg_times[sender].append(hour)

        return {
            sender: np.mean(times) if times else 12.0
            for sender, times in first_msg_times.items()
        }

    # ============== Word & Character Counts ==============

    def get_word_counts(self) -> Dict[str, int]:
        """Total words per person (text messages only)."""
        counts = defaultdict(int)
        for msg in self.text_messages:
            words = msg.content.split()
            counts[msg.sender] += len(words)
        return dict(counts)

    def get_character_counts(self) -> Dict[str, int]:
        """Total characters per person (text messages only)."""
        counts = defaultdict(int)
        for msg in self.text_messages:
            counts[msg.sender] += len(msg.content)
        return dict(counts)

    def get_unique_words(self) -> Dict[str, int]:
        """Count of unique words used per person."""
        words_by_sender = defaultdict(set)
        for msg in self.text_messages:
            words = re.findall(r'\b\w+\b', msg.content.lower())
            words_by_sender[msg.sender].update(words)
        return {sender: len(words) for sender, words in words_by_sender.items()}

    def get_average_message_length(self) -> Dict[str, float]:
        """Average words per message."""
        word_counts = self.get_word_counts()
        msg_counts = self.get_text_message_counts()
        return {
            sender: word_counts.get(sender, 0) / msg_counts.get(sender, 1)
            for sender in self.participants
        }

    # ============== Emoji Counts ==============

    def get_emoji_counts(self) -> Dict[str, int]:
        """Total emojis per person."""
        counts = defaultdict(int)
        for msg in self.text_messages:
            emojis = self.emoji_pattern.findall(msg.content)
            counts[msg.sender] += sum(len(e) for e in emojis)
        return dict(counts)

    def get_most_used_emojis(self, top_n: int = 10) -> Dict[str, List[Tuple[str, int]]]:
        """Most used emojis per person."""
        emoji_counts = defaultdict(lambda: defaultdict(int))
        for msg in self.text_messages:
            emojis = self.emoji_pattern.findall(msg.content)
            for emoji_group in emojis:
                for emoji in emoji_group:
                    emoji_counts[msg.sender][emoji] += 1

        result = {}
        for sender, emojis in emoji_counts.items():
            sorted_emojis = sorted(emojis.items(), key=lambda x: -x[1])[:top_n]
            result[sender] = sorted_emojis
        return result

    # ============== Media Counts ==============

    def get_media_counts(self) -> Dict[str, Dict[str, int]]:
        """Count of different media types per person."""
        media_types = {
            'images': MessageType.IMAGE,
            'videos': MessageType.VIDEO,
            'audio': MessageType.AUDIO,
            'stickers': MessageType.STICKER,
            'gifs': MessageType.GIF,
            'documents': MessageType.DOCUMENT,
        }

        counts = {sender: {media: 0 for media in media_types} for sender in self.participants}

        for msg in self.messages:
            for media_name, media_type in media_types.items():
                if msg.message_type == media_type:
                    if msg.sender in counts:
                        counts[msg.sender][media_name] += 1

        return counts

    def get_link_counts(self) -> Dict[str, int]:
        """Count of URLs shared per person."""
        url_pattern = re.compile(r'https?://\S+')
        counts = defaultdict(int)
        for msg in self.text_messages:
            links = url_pattern.findall(msg.content)
            counts[msg.sender] += len(links)
        return dict(counts)

    # ============== Call Statistics ==============

    def get_call_counts(self) -> Dict[str, Dict[str, int]]:
        """Count of calls by type per person."""
        call_types = {
            'video_calls': MessageType.VIDEO_CALL,
            'voice_calls': MessageType.VOICE_CALL,
            'missed_video': MessageType.MISSED_VIDEO_CALL,
            'missed_voice': MessageType.MISSED_VOICE_CALL,
        }

        counts = {sender: {call: 0 for call in call_types} for sender in self.participants}

        for msg in self.messages:
            for call_name, call_type in call_types.items():
                if msg.message_type == call_type:
                    if msg.sender in counts:
                        counts[msg.sender][call_name] += 1

        return counts

    def get_total_call_duration(self) -> Dict[str, int]:
        """Total call duration in minutes per person."""
        durations = defaultdict(int)
        for msg in self.messages:
            if msg.call_duration_seconds:
                durations[msg.sender] += msg.call_duration_seconds
        # Convert to minutes
        return {sender: dur // 60 for sender, dur in durations.items()}

    # ============== Time Analysis ==============

    def get_hourly_heatmap(self) -> np.ndarray:
        """
        7x24 array of message counts by day of week (0=Mon) and hour.
        """
        heatmap = np.zeros((7, 24))
        for msg in self.messages:
            dow = msg.timestamp.weekday()
            hour = msg.timestamp.hour
            heatmap[dow, hour] += 1
        return heatmap

    def get_hourly_distribution(self) -> Dict[int, int]:
        """Message count by hour of day."""
        counts = defaultdict(int)
        for msg in self.messages:
            counts[msg.timestamp.hour] += 1
        return dict(counts)

    def get_daily_distribution(self) -> Dict[int, int]:
        """Message count by day of week (0=Monday)."""
        counts = defaultdict(int)
        for msg in self.messages:
            counts[msg.timestamp.weekday()] += 1
        return dict(counts)

    def get_monthly_message_counts(self) -> Dict[str, Dict[str, int]]:
        """
        Message counts per month for each person.
        Key format: 'YYYY-MM'
        """
        counts = defaultdict(lambda: defaultdict(int))
        for msg in self.messages:
            month_key = msg.timestamp.strftime('%Y-%m')
            counts[month_key][msg.sender] += 1
        return {k: dict(v) for k, v in counts.items()}

    def get_monthly_totals(self) -> Dict[str, int]:
        """Total messages per month."""
        counts = defaultdict(int)
        for msg in self.messages:
            month_key = msg.timestamp.strftime('%Y-%m')
            counts[month_key] += 1
        return dict(counts)

    # ============== Relationship Growth Metrics ==============

    def get_monthly_response_times(self) -> Dict[str, Dict[str, float]]:
        """
        Average response time per month for each person.
        Used to track improvement over time.
        """
        monthly_responses = defaultdict(lambda: defaultdict(list))

        for i in range(1, len(self.messages)):
            current = self.messages[i]
            prev = self.messages[i - 1]

            if current.sender != prev.sender:
                delta = (current.timestamp - prev.timestamp).total_seconds() / 60
                if delta <= 1440:
                    month_key = current.timestamp.strftime('%Y-%m')
                    monthly_responses[month_key][current.sender].append(delta)

        result = {}
        for month, sender_times in monthly_responses.items():
            result[month] = {
                sender: np.mean(times) if times else 0
                for sender, times in sender_times.items()
            }
        return result

    def get_affection_words_timeline(self) -> Dict[str, int]:
        """
        Count affectionate words per month.
        Tracks relationship warmth over time.
        """
        affection_words = [
            'love', 'miss', 'baby', 'babe', 'cutie', 'cutu', 'sweetheart',
            'darling', 'dear', 'honey', 'jaan', 'jaanu', 'princess', 'prince',
            'beautiful', 'handsome', 'gorgeous', 'pyaar', 'pyar', 'dil',
            'heart', 'hug', 'kiss', 'care', 'special', 'best', 'favorite',
            'adore', 'precious', 'amazing', 'wonderful', 'perfect'
        ]

        counts = defaultdict(int)
        for msg in self.text_messages:
            month_key = msg.timestamp.strftime('%Y-%m')
            content_lower = msg.content.lower()
            for word in affection_words:
                counts[month_key] += content_lower.count(word)

        return dict(counts)

    def get_call_frequency_timeline(self) -> Dict[str, int]:
        """Calls per month."""
        call_types = [
            MessageType.VIDEO_CALL, MessageType.VOICE_CALL,
            MessageType.MISSED_VIDEO_CALL, MessageType.MISSED_VOICE_CALL
        ]
        counts = defaultdict(int)
        for msg in self.messages:
            if msg.message_type in call_types:
                month_key = msg.timestamp.strftime('%Y-%m')
                counts[month_key] += 1
        return dict(counts)

    # ============== Summary Statistics ==============

    def get_date_range(self) -> Tuple[datetime, datetime]:
        """Get first and last message timestamps."""
        if not self.messages:
            return None, None
        return self.messages[0].timestamp, self.messages[-1].timestamp

    def get_total_days(self) -> int:
        """Total days of conversation."""
        start, end = self.get_date_range()
        if start and end:
            return (end.date() - start.date()).days + 1
        return 0

    def get_active_days(self) -> int:
        """Number of days with at least one message."""
        dates = set()
        for msg in self.messages:
            dates.add(msg.timestamp.date())
        return len(dates)

    def get_edited_message_counts(self) -> Dict[str, int]:
        """Count of edited messages per person."""
        counts = defaultdict(int)
        for msg in self.messages:
            if msg.is_edited:
                counts[msg.sender] += 1
        return dict(counts)

    def get_all_metrics(self) -> dict:
        """Get all metrics as a dictionary."""
        return {
            'message_counts': self.get_message_counts(),
            'message_ratio': self.get_message_ratio(),
            'double_messages': self.get_double_messages(),
            'conversation_initiations': self.get_conversation_initiations(),
            'average_response_time': self.get_average_response_time(),
            'median_response_time': self.get_median_response_time(),
            'immediate_replies': self.get_immediate_replies_percentage(),
            'first_response_time': self.get_first_response_time(),
            'word_counts': self.get_word_counts(),
            'character_counts': self.get_character_counts(),
            'unique_words': self.get_unique_words(),
            'average_message_length': self.get_average_message_length(),
            'emoji_counts': self.get_emoji_counts(),
            'media_counts': self.get_media_counts(),
            'link_counts': self.get_link_counts(),
            'call_counts': self.get_call_counts(),
            'total_call_duration': self.get_total_call_duration(),
            'hourly_distribution': self.get_hourly_distribution(),
            'daily_distribution': self.get_daily_distribution(),
            'monthly_totals': self.get_monthly_totals(),
            'date_range': [str(d) for d in self.get_date_range()],
            'total_days': self.get_total_days(),
            'active_days': self.get_active_days(),
        }


if __name__ == '__main__':
    from chat_parser import parse_whatsapp_chat
    import json

    file_path = '/Users/arvind/PythonProjects/Chatanaylsi/_chat.txt'
    print(f"Parsing {file_path}...")
    messages = parse_whatsapp_chat(file_path)

    participant_mapping = {
        "~~": "Arvind",
        "bae \U0001FAF6": "Palak"  # bae followed by emoji
    }

    print("Calculating metrics...")
    calc = MetricsCalculator(messages, participant_mapping)

    metrics = calc.get_all_metrics()

    print("\n=== Metrics Summary ===")
    print(f"\nMessage Counts: {metrics['message_counts']}")
    print(f"Message Ratio: {metrics['message_ratio']}")
    print(f"Double Messages: {metrics['double_messages']}")
    print(f"Conversation Initiations: {metrics['conversation_initiations']}")
    print(f"Avg Response Time (min): {metrics['average_response_time']}")
    print(f"Immediate Replies %: {metrics['immediate_replies']}")
    print(f"Word Counts: {metrics['word_counts']}")
    print(f"Emoji Counts: {metrics['emoji_counts']}")
    print(f"Date Range: {metrics['date_range']}")
    print(f"Active Days: {metrics['active_days']} / {metrics['total_days']}")

    # Save metrics
    output_path = '/Users/arvind/PythonProjects/Chatanaylsi/.tmp/metrics.json'
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"\nSaved to {output_path}")
