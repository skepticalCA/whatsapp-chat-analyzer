"""
Sentiment Analyzer Module
Analyzes relationship health, generates insights, and tracks growth over time.
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np
from chat_parser import Message, MessageType
from metrics_calculator import MetricsCalculator


class SentimentAnalyzer:
    """Analyze relationship sentiment and generate insights."""

    # Positive sentiment words
    POSITIVE_WORDS = [
        'love', 'happy', 'great', 'amazing', 'wonderful', 'beautiful', 'awesome',
        'perfect', 'best', 'fun', 'nice', 'good', 'excited', 'yay', 'wow',
        'haha', 'lol', 'cute', 'sweet', 'lovely', 'adorable', 'miss', 'like',
        'enjoy', 'glad', 'thanks', 'thank', 'appreciate', 'lucky', 'blessed'
    ]

    # Negative sentiment words
    NEGATIVE_WORDS = [
        'sad', 'angry', 'upset', 'hate', 'bad', 'terrible', 'awful', 'worst',
        'annoyed', 'frustrated', 'disappointed', 'sorry', 'hurt', 'cry', 'tears',
        'stressed', 'worried', 'scared', 'nervous', 'anxious', 'tired', 'bored',
        'lonely', 'miss', 'sick', 'ill', 'pain'
    ]

    # Affectionate terms
    AFFECTION_TERMS = [
        'baby', 'babe', 'love', 'dear', 'honey', 'sweetheart', 'darling',
        'cutie', 'cutu', 'jaan', 'jaanu', 'princess', 'prince', 'bb', 'bub',
        'hubby', 'wifey', 'bf', 'gf', 'bae', 'bubba', 'soulmate'
    ]

    def __init__(self, messages: List[Message], metrics: MetricsCalculator,
                 participant_mapping: Dict[str, str]):
        """
        Initialize with messages, calculated metrics, and participant mapping.
        """
        self.messages = messages
        self.metrics = metrics
        self.participant_mapping = participant_mapping
        self.participants = list(participant_mapping.keys())
        self.text_messages = [m for m in messages if m.message_type == MessageType.TEXT]

    def get_display_name(self, raw_name: str) -> str:
        """Get display name for a participant."""
        return self.participant_mapping.get(raw_name, raw_name)

    def calculate_sentiment_scores(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate positive/negative sentiment ratio per person.
        Returns scores between 0 and 1.
        """
        scores = {}

        for participant in self.participants:
            positive_count = 0
            negative_count = 0
            total_words = 0

            for msg in self.text_messages:
                if msg.sender == participant:
                    words = msg.content.lower().split()
                    total_words += len(words)

                    for word in words:
                        if any(pw in word for pw in self.POSITIVE_WORDS):
                            positive_count += 1
                        if any(nw in word for nw in self.NEGATIVE_WORDS):
                            negative_count += 1

            if total_words > 0:
                scores[participant] = {
                    'positive': positive_count / total_words,
                    'negative': negative_count / total_words,
                    'overall': (positive_count - negative_count * 0.5) / total_words
                }
            else:
                scores[participant] = {'positive': 0, 'negative': 0, 'overall': 0}

        return scores

    def calculate_relationship_rating(self) -> Tuple[str, str, float]:
        """
        Calculate overall relationship rating.
        Returns (rating_label, description, score 0-100)
        """
        score = 0.0

        # 1. Balance Score (25 points) - How equal is message distribution
        ratio = self.metrics.get_message_ratio()
        ratios = list(ratio.values())
        if len(ratios) >= 2:
            balance_diff = abs(ratios[0] - ratios[1])
            balance_score = max(0, 25 - balance_diff * 0.5)
            score += balance_score

        # 2. Response Time Score (25 points) - Fast responses indicate engagement
        avg_response = self.metrics.get_average_response_time()
        if avg_response:
            avg_time = np.mean(list(avg_response.values()))
            # Under 5 min = full points, degrades after
            response_score = max(0, 25 - (avg_time / 60) * 5)
            score += response_score

        # 3. Initiation Balance Score (20 points)
        initiations = self.metrics.get_conversation_initiations()
        if initiations:
            init_values = list(initiations.values())
            if len(init_values) >= 2 and sum(init_values) > 0:
                init_ratio = min(init_values) / max(init_values) if max(init_values) > 0 else 0
                score += init_ratio * 20

        # 4. Engagement Score (15 points) - Media sharing, calls
        call_counts = self.metrics.get_call_counts()
        total_calls = sum(
            sum(counts.values())
            for counts in call_counts.values()
        )
        # Normalize: 100+ calls = full points
        engagement_score = min(15, (total_calls / 100) * 15)
        score += engagement_score

        # 5. Sentiment Score (15 points) - Positive language use
        sentiments = self.calculate_sentiment_scores()
        if sentiments:
            avg_sentiment = np.mean([s['overall'] for s in sentiments.values()])
            sentiment_score = min(15, max(0, avg_sentiment * 1000))
            score += sentiment_score

        # Clamp to 0-100
        score = min(100, max(0, score))

        # Determine rating label and description
        if score >= 90:
            label = "Excellent"
            desc = "An exceptional relationship with strong communication and mutual engagement."
        elif score >= 75:
            label = "Strong"
            desc = "A healthy relationship with good balance and consistent communication."
        elif score >= 60:
            label = "Good"
            desc = "A solid relationship with room for deeper connection."
        elif score >= 45:
            label = "Developing"
            desc = "The relationship is growing. Keep nurturing the connection."
        else:
            label = "Building"
            desc = "Early stages of connection. Focus on consistent communication."

        return label, desc, round(score, 1)

    def generate_key_insights(self) -> List[str]:
        """
        Generate 4-5 personalized insights about the relationship.
        """
        insights = []

        # Get metrics
        msg_counts = self.metrics.get_message_counts()
        msg_ratio = self.metrics.get_message_ratio()
        initiations = self.metrics.get_conversation_initiations()
        avg_response = self.metrics.get_average_response_time()
        immediate_replies = self.metrics.get_immediate_replies_percentage()
        double_msgs = self.metrics.get_double_messages()

        # Determine who messages more
        if msg_counts:
            sorted_senders = sorted(msg_counts.items(), key=lambda x: -x[1])
            more_sender = self.get_display_name(sorted_senders[0][0])
            less_sender = self.get_display_name(sorted_senders[1][0]) if len(sorted_senders) > 1 else None

        # 1. Message balance insight
        if msg_ratio:
            ratio_values = list(msg_ratio.values())
            if len(ratio_values) >= 2:
                diff = abs(ratio_values[0] - ratio_values[1])
                if diff < 10:
                    insights.append("You both contribute equally to conversations - great balance!")
                elif diff < 20:
                    insights.append(f"{more_sender} sends more messages, but the conversation is still balanced.")
                else:
                    insights.append(f"{more_sender} drives most conversations. Try to balance participation more.")

        # 2. Conversation initiation insight
        if initiations and len(initiations) >= 2:
            sorted_init = sorted(initiations.items(), key=lambda x: -x[1])
            initiator = self.get_display_name(sorted_init[0][0])
            init_ratio = sorted_init[1][1] / sorted_init[0][1] if sorted_init[0][1] > 0 else 0

            if init_ratio > 0.8:
                insights.append("You both initiate conversations equally - shows mutual interest!")
            elif init_ratio > 0.5:
                insights.append(f"{initiator} starts more conversations, but both reach out.")
            else:
                other = self.get_display_name(sorted_init[1][0])
                insights.append(f"Try being the one to reach out first, {other}!")

        # 3. Response time insight
        if avg_response:
            avg_times = list(avg_response.values())
            overall_avg = np.mean(avg_times)
            if overall_avg < 5:
                insights.append("Lightning-fast responses! You're both very attentive.")
            elif overall_avg < 15:
                insights.append("Good response times show you prioritize each other.")
            elif overall_avg < 60:
                insights.append("Response times are reasonable, but quicker replies show care.")
            else:
                insights.append("Consider responding more promptly to show engagement.")

        # 4. Immediate replies insight
        if immediate_replies:
            avg_immediate = np.mean(list(immediate_replies.values()))
            if avg_immediate > 30:
                insights.append(f"Over {int(avg_immediate)}% of replies are immediate - you're very engaged!")
            elif avg_immediate > 15:
                insights.append("Good instant response rate shows active conversations.")

        # 5. Double texting insight (shows enthusiasm)
        if double_msgs:
            total_doubles = sum(double_msgs.values())
            if total_doubles > 1000:
                insights.append("Lots of double-texting shows enthusiasm and energy in conversations!")

        # 6. Call frequency insight
        call_counts = self.metrics.get_call_counts()
        if call_counts:
            total_video = sum(c.get('video_calls', 0) for c in call_counts.values())
            if total_video > 500:
                insights.append(f"Over {total_video} video calls! Face-to-face time strengthens bonds.")
            elif total_video > 100:
                insights.append("Regular video calls help maintain closeness.")

        # Limit to 5 insights
        return insights[:5]

    def detect_milestones(self) -> List[Tuple[datetime, str]]:
        """
        Detect key relationship milestones.
        Returns list of (date, milestone_description)
        """
        milestones = []

        if not self.messages:
            return milestones

        # First message
        milestones.append((
            self.messages[0].timestamp,
            "First message"
        ))

        # First "I love you" or equivalent
        love_pattern = re.compile(r'\bi\s*(love|luv)\s*(you|u)\b', re.IGNORECASE)
        for msg in self.text_messages:
            if love_pattern.search(msg.content):
                milestones.append((msg.timestamp, "First 'I love you'"))
                break

        # First call
        for msg in self.messages:
            if msg.message_type in [MessageType.VIDEO_CALL, MessageType.VOICE_CALL]:
                milestones.append((msg.timestamp, "First call"))
                break

        # First video call specifically
        for msg in self.messages:
            if msg.message_type == MessageType.VIDEO_CALL:
                milestones.append((msg.timestamp, "First video call"))
                break

        # First shared image
        for msg in self.messages:
            if msg.message_type == MessageType.IMAGE:
                milestones.append((msg.timestamp, "First photo shared"))
                break

        # 1000th message
        if len(self.messages) >= 1000:
            milestones.append((self.messages[999].timestamp, "1,000th message"))

        # 10,000th message
        if len(self.messages) >= 10000:
            milestones.append((self.messages[9999].timestamp, "10,000th message"))

        # 100,000th message
        if len(self.messages) >= 100000:
            milestones.append((self.messages[99999].timestamp, "100,000th message"))

        # Sort by date
        milestones.sort(key=lambda x: x[0])
        return milestones

    def get_relationship_growth_data(self) -> Dict:
        """
        Get data showing relationship growth over time.
        """
        monthly_totals = self.metrics.get_monthly_totals()
        monthly_response = self.metrics.get_monthly_response_times()
        affection_timeline = self.metrics.get_affection_words_timeline()
        call_timeline = self.metrics.get_call_frequency_timeline()

        # Calculate growth metrics
        months = sorted(monthly_totals.keys())

        if len(months) < 2:
            return {
                'months': months,
                'message_volumes': list(monthly_totals.values()),
                'growth_trend': 'stable'
            }

        # Calculate average response time trend
        response_trend = []
        for month in months:
            if month in monthly_response:
                times = list(monthly_response[month].values())
                response_trend.append(np.mean(times) if times else None)
            else:
                response_trend.append(None)

        # Determine growth trend
        first_quarter_avg = np.mean(list(monthly_totals.values())[:3])
        last_quarter_avg = np.mean(list(monthly_totals.values())[-3:])

        if last_quarter_avg > first_quarter_avg * 1.2:
            growth_trend = 'growing'
        elif last_quarter_avg < first_quarter_avg * 0.8:
            growth_trend = 'declining'
        else:
            growth_trend = 'stable'

        return {
            'months': months,
            'message_volumes': [monthly_totals.get(m, 0) for m in months],
            'response_times': response_trend,
            'affection_counts': [affection_timeline.get(m, 0) for m in months],
            'call_counts': [call_timeline.get(m, 0) for m in months],
            'growth_trend': growth_trend,
            'milestones': self.detect_milestones()
        }

    def get_communication_style(self) -> Dict[str, str]:
        """
        Analyze communication style for each person.
        """
        styles = {}

        for participant in self.participants:
            participant_msgs = [m for m in self.text_messages if m.sender == participant]

            if not participant_msgs:
                styles[participant] = "Unknown"
                continue

            # Calculate metrics
            avg_length = np.mean([len(m.content.split()) for m in participant_msgs])
            emoji_ratio = sum(1 for m in participant_msgs if re.search(r'[\U0001F600-\U0001F64F]', m.content)) / len(participant_msgs)
            question_ratio = sum(1 for m in participant_msgs if '?' in m.content) / len(participant_msgs)

            # Determine style
            if avg_length > 15:
                if emoji_ratio > 0.3:
                    style = "Expressive & Detailed"
                else:
                    style = "Thoughtful & Detailed"
            elif avg_length > 8:
                if emoji_ratio > 0.3:
                    style = "Balanced & Warm"
                else:
                    style = "Conversational"
            else:
                if emoji_ratio > 0.4:
                    style = "Quick & Playful"
                else:
                    style = "Concise & Direct"

            if question_ratio > 0.15:
                style += ", Curious"

            styles[participant] = style

        return styles


if __name__ == '__main__':
    from chat_parser import parse_whatsapp_chat
    import json

    file_path = '/Users/arvind/PythonProjects/Chatanaylsi/_chat.txt'
    print(f"Parsing {file_path}...")
    messages = parse_whatsapp_chat(file_path)

    participant_mapping = {
        "~~": "Arvind",
        "bae \U0001FAF6": "Palak"
    }

    print("Calculating metrics...")
    metrics = MetricsCalculator(messages, participant_mapping)

    print("Analyzing sentiment...")
    analyzer = SentimentAnalyzer(messages, metrics, participant_mapping)

    # Relationship rating
    label, desc, score = analyzer.calculate_relationship_rating()
    print(f"\n=== Relationship Rating ===")
    print(f"Rating: {label} ({score}/100)")
    print(f"Description: {desc}")

    # Key insights
    print(f"\n=== Key Insights ===")
    for i, insight in enumerate(analyzer.generate_key_insights(), 1):
        print(f"{i}. {insight}")

    # Milestones
    print(f"\n=== Milestones ===")
    for date, milestone in analyzer.detect_milestones():
        print(f"  {date.strftime('%b %d, %Y')}: {milestone}")

    # Communication styles
    print(f"\n=== Communication Styles ===")
    for sender, style in analyzer.get_communication_style().items():
        print(f"  {analyzer.get_display_name(sender)}: {style}")

    # Save results
    output_path = '/Users/arvind/PythonProjects/Chatanaylsi/.tmp/sentiment.json'
    with open(output_path, 'w') as f:
        json.dump({
            'rating': {'label': label, 'description': desc, 'score': score},
            'insights': analyzer.generate_key_insights(),
            'milestones': [(str(d), m) for d, m in analyzer.detect_milestones()],
            'styles': analyzer.get_communication_style(),
            'growth': analyzer.get_relationship_growth_data()
        }, f, indent=2, default=str)
    print(f"\nSaved to {output_path}")
