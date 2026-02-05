"""
Topic Classifier Module
Categorizes messages into conversation topics for the pie chart.
"""

import re
from typing import List, Dict, Tuple
from collections import defaultdict
from chat_parser import Message, MessageType


class TopicClassifier:
    """Classify messages into conversation topics."""

    # Topic keywords with weights
    TOPIC_KEYWORDS = {
        'Love & Affection': {
            'keywords': [
                'love', 'miss', 'baby', 'babe', 'cutie', 'cutu', 'sweetheart',
                'darling', 'dear', 'honey', 'jaan', 'jaanu', 'princess', 'bub',
                'beautiful', 'gorgeous', 'pyaar', 'pyar', 'dil', 'heart', 'hug',
                'kiss', 'care', 'special', 'adore', 'precious', 'bb', 'bubba',
                'cutuu', 'babyyy', 'lovee', 'missss', 'aww', 'awww', 'mwah'
            ],
            'weight': 1.5
        },
        'Daily Life': {
            'keywords': [
                'morning', 'night', 'sleep', 'wake', 'tired', 'rest', 'home',
                'work', 'office', 'college', 'class', 'study', 'exam', 'test',
                'busy', 'free', 'done', 'reached', 'coming', 'going', 'left',
                'goodnight', 'goodmorning', 'gm', 'gn', 'bye', 'hello', 'hey',
                'hi', 'hii', 'hiii', 'hellu', 'byee', 'cya', 'ttyl'
            ],
            'weight': 1.0
        },
        'Planning & Meetups': {
            'keywords': [
                'meet', 'plan', 'tomorrow', 'today', 'weekend', 'time', 'place',
                'where', 'when', 'come', 'pick', 'drop', 'metro', 'cab', 'auto',
                'uber', 'ola', 'mall', 'cafe', 'restaurant', 'movie', 'date',
                'outing', 'trip', 'travel', 'visit', 'station', 'airport'
            ],
            'weight': 1.3
        },
        'Food & Dining': {
            'keywords': [
                'food', 'eat', 'lunch', 'dinner', 'breakfast', 'hungry', 'khana',
                'restaurant', 'cafe', 'coffee', 'tea', 'chai', 'snack', 'pizza',
                'burger', 'biryani', 'momo', 'maggi', 'cook', 'cooking', 'recipe',
                'yummy', 'tasty', 'delicious', 'order', 'swiggy', 'zomato'
            ],
            'weight': 1.2
        },
        'Entertainment': {
            'keywords': [
                'movie', 'film', 'watch', 'netflix', 'prime', 'hotstar', 'series',
                'show', 'episode', 'song', 'music', 'spotify', 'game', 'play',
                'youtube', 'video', 'reel', 'instagram', 'meme', 'funny', 'lol',
                'haha', 'rofl', 'comedy', 'drama', 'thriller', 'horror'
            ],
            'weight': 1.1
        },
        'Emotions & Support': {
            'keywords': [
                'happy', 'sad', 'angry', 'upset', 'worried', 'scared', 'nervous',
                'excited', 'anxious', 'stressed', 'cry', 'crying', 'tears', 'hurt',
                'sorry', 'apologize', 'forgive', 'understand', 'support', 'help',
                'problem', 'issue', 'feeling', 'feel', 'mood', 'fine', 'okay'
            ],
            'weight': 1.4
        },
        'Random Chat': {
            'keywords': [
                'what', 'why', 'how', 'lol', 'haha', 'okay', 'ok', 'hmm', 'umm',
                'acha', 'achha', 'theek', 'thik', 'haan', 'nahi', 'yes', 'no',
                'maybe', 'idk', 'wbu', 'wby', 'nothing', 'kuch', 'bas', 'chalo',
                'btw', 'actually', 'literally', 'basically', 'anyway'
            ],
            'weight': 0.8
        }
    }

    def __init__(self, messages: List[Message]):
        """Initialize with text messages only."""
        self.messages = [m for m in messages if m.message_type == MessageType.TEXT]

    def classify_message(self, content: str) -> Tuple[str, float]:
        """
        Classify a single message into a topic.
        Returns (topic_name, confidence_score)
        """
        content_lower = content.lower()
        scores = defaultdict(float)

        for topic, config in self.TOPIC_KEYWORDS.items():
            for keyword in config['keywords']:
                # Count occurrences
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', content_lower))
                if count > 0:
                    scores[topic] += count * config['weight']

        if not scores:
            return 'Other', 0.0

        best_topic = max(scores.items(), key=lambda x: x[1])
        return best_topic[0], best_topic[1]

    def classify_all_messages(self) -> Dict[str, int]:
        """
        Classify all messages into topics.
        Returns count per topic.
        """
        topic_counts = defaultdict(int)

        for msg in self.messages:
            topic, _ = self.classify_message(msg.content)
            topic_counts[topic] += 1

        # Ensure all topics have entries
        for topic in self.TOPIC_KEYWORDS:
            if topic not in topic_counts:
                topic_counts[topic] = 0

        return dict(topic_counts)

    def get_topic_percentages(self) -> Dict[str, float]:
        """Return topic distribution as percentages."""
        counts = self.classify_all_messages()
        total = sum(counts.values())

        if total == 0:
            return {topic: 0.0 for topic in self.TOPIC_KEYWORDS}

        percentages = {
            topic: (count / total) * 100
            for topic, count in counts.items()
        }

        return dict(sorted(percentages.items(), key=lambda x: -x[1]))

    def get_topic_by_sender(self) -> Dict[str, Dict[str, int]]:
        """Get topic distribution per sender."""
        sender_topics = defaultdict(lambda: defaultdict(int))

        for msg in self.messages:
            topic, _ = self.classify_message(msg.content)
            sender_topics[msg.sender][topic] += 1

        return {
            sender: dict(topics)
            for sender, topics in sender_topics.items()
        }

    def get_monthly_topic_trends(self) -> Dict[str, Dict[str, int]]:
        """
        Topic distribution by month.
        Useful for seeing how conversation focus evolved.
        """
        monthly_topics = defaultdict(lambda: defaultdict(int))

        for msg in self.messages:
            month_key = msg.timestamp.strftime('%Y-%m')
            topic, _ = self.classify_message(msg.content)
            monthly_topics[month_key][topic] += 1

        return {
            month: dict(topics)
            for month, topics in monthly_topics.items()
        }


if __name__ == '__main__':
    from chat_parser import parse_whatsapp_chat
    import json

    file_path = '/Users/arvind/PythonProjects/Chatanaylsi/_chat.txt'
    print(f"Parsing {file_path}...")
    messages = parse_whatsapp_chat(file_path)

    print("Classifying topics...")
    classifier = TopicClassifier(messages)

    percentages = classifier.get_topic_percentages()

    print("\n=== Topic Distribution ===")
    for topic, pct in percentages.items():
        bar = '#' * int(pct / 2)
        print(f"{topic:20s}: {pct:5.1f}% {bar}")

    # Save results
    output_path = '/Users/arvind/PythonProjects/Chatanaylsi/.tmp/topics.json'
    with open(output_path, 'w') as f:
        json.dump({
            'percentages': percentages,
            'counts': classifier.classify_all_messages(),
            'by_sender': classifier.get_topic_by_sender()
        }, f, indent=2)
    print(f"\nSaved to {output_path}")
