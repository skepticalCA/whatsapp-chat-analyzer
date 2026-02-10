#!/usr/bin/env python3
"""
WhatsApp Chat Analyzer - Main Orchestrator
Generates a comprehensive visual dashboard from WhatsApp chat exports.
"""

import os
import sys
import json
from datetime import datetime

# Add execution directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_parser import parse_whatsapp_chat, get_participants, save_parsed_messages
from metrics_calculator import MetricsCalculator
from topic_classifier import TopicClassifier
from sentiment_analyzer import SentimentAnalyzer
from dashboard_generator import DashboardGenerator
from word_cloud_analyzer import WordCloudGenerator


def analyze_chat(chat_file: str, output_dir: str, participant_mapping: dict = None):
    """
    Main analysis pipeline.

    Args:
        chat_file: Path to WhatsApp chat export txt file
        output_dir: Directory to save outputs
        participant_mapping: Optional dict mapping raw names to display names
    """
    print("=" * 60)
    print("WhatsApp Chat Analyzer")
    print("=" * 60)

    # Ensure output directories exist
    os.makedirs(output_dir, exist_ok=True)
    tmp_dir = os.path.join(os.path.dirname(output_dir), '.tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    # Step 1: Parse chat file
    print(f"\n[1/5] Parsing chat file: {chat_file}")
    messages = parse_whatsapp_chat(chat_file)
    print(f"      Parsed {len(messages):,} messages")

    # Get participants if not provided
    raw_participants = get_participants(messages)
    print(f"      Participants: {raw_participants}")

    if participant_mapping is None:
        # Auto-generate mapping (use raw names)
        participant_mapping = {p: p for p in raw_participants}
        print("      Using raw participant names (no mapping provided)")

    # Save parsed messages for debugging
    parsed_path = os.path.join(tmp_dir, 'parsed_messages.json')
    save_parsed_messages(messages, parsed_path)
    print(f"      Saved parsed messages to {parsed_path}")

    # Step 2: Calculate metrics
    print(f"\n[2/5] Calculating metrics...")
    metrics = MetricsCalculator(messages, participant_mapping)

    # Get summary stats
    msg_counts = metrics.get_message_counts()
    date_range = metrics.get_date_range()
    print(f"      Message counts: {msg_counts}")
    print(f"      Date range: {date_range[0].date()} to {date_range[1].date()}")
    print(f"      Active days: {metrics.get_active_days()} / {metrics.get_total_days()}")

    # Save metrics
    metrics_path = os.path.join(tmp_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics.get_all_metrics(), f, indent=2, default=str)
    print(f"      Saved metrics to {metrics_path}")

    # Step 3: Classify topics
    print(f"\n[3/5] Classifying message topics...")
    topics = TopicClassifier(messages)
    topic_pcts = topics.get_topic_percentages()
    print(f"      Top topics: {dict(list(topic_pcts.items())[:3])}")

    # Save topics
    topics_path = os.path.join(tmp_dir, 'topics.json')
    with open(topics_path, 'w') as f:
        json.dump({
            'percentages': topic_pcts,
            'counts': topics.classify_all_messages()
        }, f, indent=2)
    print(f"      Saved topics to {topics_path}")

    # Step 4: Analyze sentiment
    print(f"\n[4/5] Analyzing relationship sentiment...")
    sentiment = SentimentAnalyzer(messages, metrics, participant_mapping)

    rating_label, rating_desc, rating_score = sentiment.calculate_relationship_rating()
    print(f"      Relationship Rating: {rating_label} ({rating_score}/100)")

    insights = sentiment.generate_key_insights()
    print(f"      Key Insights:")
    for insight in insights[:3]:
        print(f"        - {insight[:60]}...")

    milestones = sentiment.detect_milestones()
    print(f"      Milestones detected: {len(milestones)}")

    # Save sentiment
    sentiment_path = os.path.join(tmp_dir, 'sentiment.json')
    with open(sentiment_path, 'w') as f:
        json.dump({
            'rating': {'label': rating_label, 'description': rating_desc, 'score': rating_score},
            'insights': insights,
            'milestones': [(str(d), m) for d, m in milestones],
            'growth': sentiment.get_relationship_growth_data()
        }, f, indent=2, default=str)
    print(f"      Saved sentiment to {sentiment_path}")

    # Step 5: Generate dashboard
    print(f"\n[5/6] Generating main visual dashboard...")
    dashboard = DashboardGenerator(messages, metrics, sentiment, topics, participant_mapping)

    output_path = os.path.join(output_dir, 'dashboard.png')
    dashboard.create_dashboard(output_path)

    # Step 6: Generate Word Cloud Dashboard
    print(f"\n[6/6] Generating word cloud dashboard...")
    wc_generator = WordCloudGenerator(messages, participant_mapping)
    wc_output_path = os.path.join(output_dir, 'word_cloud_dashboard.png')
    wc_generator.create_dashboard(wc_output_path)

    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"\nDashboard saved to: {output_path}")
    print(f"Intermediate files in: {tmp_dir}")

    return {
        'dashboard_path': output_path,
        'messages_count': len(messages),
        'rating': rating_score,
        'rating_label': rating_label
    }


def main():
    """Main entry point."""
    # Configuration
    CHAT_FILE = '/Users/arvind/PythonProjects/Chatanaylsi/_chat.txt'
    OUTPUT_DIR = '/Users/arvind/PythonProjects/Chatanaylsi/output'

    # Participant mapping (raw name -> display name)
    # The raw names are extracted from the chat file
    PARTICIPANT_MAPPING = {
        "~~": "Arvind",
        "bae \U0001FAF6": "Palak",  # bae followed by heart hands emoji
        "bae 🫶": "Palak"  # alternative encoding
    }

    # Check if chat file exists
    if not os.path.exists(CHAT_FILE):
        print(f"Error: Chat file not found: {CHAT_FILE}")
        sys.exit(1)

    # Run analysis
    try:
        result = analyze_chat(CHAT_FILE, OUTPUT_DIR, PARTICIPANT_MAPPING)
        print(f"\nFinal Rating: {result['rating_label']} ({result['rating']}/100)")
        print(f"Total Messages Analyzed: {result['messages_count']:,}")
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
