#!/usr/bin/env python3
"""
Word Cloud & Frequency Analyzer
Generates word clouds and frequency charts for the chat.
"""

import os
import sys
import re
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
from typing import List, Dict
import numpy as np

# Add execution directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_parser import Message, MessageType
from font_setup import setup_fonts

# Romantic Love Theme Color Palette
COLORS = {
    'background': '#fef7f9',
    'card_bg': '#ffffff',
    'card_border': '#ffc0cb',
    'text_primary': '#5c4a52',
    'text_secondary': '#8b7580',
    'person1': '#818cf8',  # Soft indigo
    'person2': '#f472b6',  # Rose pink
    'love_dark': '#db2777',
    'love_pink': '#ff85a2',
    'gradient_start': '#fce7f3',
    'gradient_end': '#ddd6fe',
}

# Extended stop words including Hinglish
HINGLISH_STOPWORDS = {
    'hai', 'ha', 'ho', 'hun', 'tha', 'thi', 'the', 'kar', 'ra', 'rha', 'rhe', 'rhi',
    'ko', 'me', 'mein', 'se', 'ki', 'ka', 'ke', 'ye', 'yeh', 'wo', 'woh', 'aur',
    'kya', 'kyu', 'kyun', 'nahi', 'nhi', 'na', 'hn', 'hmm', 'hmmm', 'hmmmm',
    'ok', 'okay', 'accha', 'acha', 'tik', 'thik', 'bhi', 'fi', 'hi', 'to', 'toh',
    'mai', 'main', 'tum', 'tu', 'aap', 'jo', 'jis', 'jin', 'un', 'us', 'iss', 'is',
    'k', 'n', 'u', 'ur', 'dis', 'dat', 'd', 'img', 'omitted', 'media', 'image',
    'video', 'sticker', 'gif', 'deleted', 'message', 'edited', 'null', 'nan',
    'haha', 'hahaha', 'lol', 'lmao', 'rofl', 'hehe', 'hehehe', 'are', 'yaar',
    'ni', 'ne', 'ab', 'bb', 'fir', 'phir'
}

CUSTOM_STOPWORDS = set(STOPWORDS).union(HINGLISH_STOPWORDS)

class WordCloudGenerator:
    """Generates word analytics and visualizations."""

    def __init__(self, messages: List[Message], participant_mapping: Dict[str, str]):
        self.messages = messages
        self.participant_mapping = participant_mapping
        self.participants = list(participant_mapping.keys())
        
        # Filter text messages
        self.text_messages = [m for m in messages if m.message_type == MessageType.TEXT]
        
        # Setup fonts and style
        plt.style.use('seaborn-v0_8-whitegrid')
        setup_fonts()
        plt.rcParams['axes.facecolor'] = COLORS['card_bg']
        plt.rcParams['figure.facecolor'] = COLORS['background']
        plt.rcParams['text.color'] = COLORS['text_primary']

    def get_display_name(self, raw_name: str) -> str:
        return self.participant_mapping.get(raw_name, raw_name)

    def _clean_text(self, text: str) -> str:
        """Clean text for word analysis."""
        # Convert to lower case
        text = text.lower()
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Remove special characters but keep basic punctuation for sentence structure
        # actually for word cloud we want just words
        text = re.sub(r'[^\w\s]', ' ', text) 
        return text

    def get_word_frequencies(self, sender: str = None) -> Counter:
        """Get word frequencies, optionally filtered by sender."""
        text_content = ""
        for msg in self.text_messages:
            if sender and msg.sender != sender:
                continue
            text_content += " " + self._clean_text(msg.content)
            
        words = text_content.split()
        # Remove stopwords
        filtered_words = [w for w in words if w not in CUSTOM_STOPWORDS and len(w) > 2]
        return Counter(filtered_words)

    def create_dashboard(self, output_path: str, figsize=(20, 24)):
        """Generate the word cloud dashboard."""
        fig = plt.figure(figsize=figsize, facecolor=COLORS['background'])
        
        # Create grid layout
        gs = GridSpec(5, 2, figure=fig, hspace=0.3, wspace=0.2,
                      left=0.05, right=0.95, top=0.95, bottom=0.05)

        # Row 0: Header
        ax_header = fig.add_subplot(gs[0, :])
        self._render_header(ax_header)

        # Get participants
        p1, p2 = self.participants[0], self.participants[1] if len(self.participants) > 1 else self.participants[0]

        # Row 1: Word Clouds
        ax_cloud1 = fig.add_subplot(gs[1, 0])
        ax_cloud2 = fig.add_subplot(gs[1, 1])
        
        self._render_word_cloud(ax_cloud1, p1, COLORS['person1'])
        self._render_word_cloud(ax_cloud2, p2, COLORS['person2'])

        # Row 2: Top Words Bar Charts
        ax_bar1 = fig.add_subplot(gs[2, 0])
        ax_bar2 = fig.add_subplot(gs[2, 1])

        self._render_top_words(ax_bar1, p1, COLORS['person1'])
        self._render_top_words(ax_bar2, p2, COLORS['person2'])

        # Row 3: Distinctive words (words unique to each person mostly)
        ax_distinct = fig.add_subplot(gs[3, :])
        self._render_distinctive_words(ax_distinct, p1, p2)

        # Row 4: Common phrases / n-grams (3-word phrases)
        ax_phrases = fig.add_subplot(gs[4, :])
        self._render_common_phrases(ax_phrases)

        plt.savefig(output_path, dpi=150, facecolor=COLORS['background'],
                    edgecolor='none', bbox_inches='tight')
        plt.close()
        print(f"Word Cloud Dashboard saved to {output_path}")

    def _render_header(self, ax):
        """Render romantic header."""
        ax.set_facecolor(COLORS['background'])
        ax.axis('off')
        
        ax.text(0.5, 0.7, "✨ Words of Love ✨", fontsize=32,
                color=COLORS['love_dark'], ha='center', va='center',
                fontweight='bold', transform=ax.transAxes)
                
        ax.text(0.5, 0.3, "Analyzing the language of your hearts 💬", fontsize=14,
                color=COLORS['text_secondary'], ha='center', va='center',
                transform=ax.transAxes, fontstyle='italic')

    def _render_word_cloud(self, ax, sender: str, color_func):
        """Render word cloud for a participant."""
        name = self.get_display_name(sender)
        
        # Get frequency
        frequencies = self.get_word_frequencies(sender)
        
        if not frequencies:
            ax.text(0.5, 0.5, "Not enough data", ha='center', va='center')
            return

        # Create coloring function based on the theme color
        def simple_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
            return color_func

        wc = WordCloud(
            background_color='white',
            width=800, height=500,
            max_words=100,
            stopwords=CUSTOM_STOPWORDS,
            color_func=simple_color_func,
            font_path=None  # Use default font or pass path if available
        ).generate_from_frequencies(frequencies)

        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f"☁️ {name}'s Word Cloud", fontsize=16, color=color_func, pad=20, fontweight='bold')
        
        # Add a border
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color(COLORS['card_border'])
            spine.set_linewidth(2)

    def _render_top_words(self, ax, sender: str, color: str):
        """Render horizontal bar chart of top 10 words."""
        name = self.get_display_name(sender)
        frequencies = self.get_word_frequencies(sender)
        
        top_10 = frequencies.most_common(10)
        
        if not top_10:
            return

        words = [x[0] for x in top_10][::-1]
        counts = [x[1] for x in top_10][::-1]
        
        ax.set_facecolor(COLORS['card_bg'])
        ax.barh(words, counts, color=color, alpha=0.7)
        
        # Style
        ax.set_title(f"📊 {name}'s Top 10 Words", fontsize=14, color=color, loc='left', fontweight='bold')
        ax.tick_params(colors=COLORS['text_secondary'])
        
        # Remove spines except bottom
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color(COLORS['card_border'])

    def _render_distinctive_words(self, ax, p1: str, p2: str):
        """Render distinctive words for each person."""
        ax.set_facecolor(COLORS['card_bg'])
        # Add border
        for spine in ax.spines.values():
            spine.set_color(COLORS['card_border'])
            spine.set_linewidth(2)
            
        ax.axis('off')
        ax.set_title("✨ Unique Vocabulary ✨", fontsize=16, color=COLORS['love_dark'], loc='center', pad=15)
        
        freq1 = self.get_word_frequencies(p1)
        freq2 = self.get_word_frequencies(p2)
        
        # Words used by p1 much more than p2 (ratio)
        distinctive1 = []
        distinctive2 = []
        
        all_words = set(list(freq1.keys()) + list(freq2.keys()))
        
        for word in all_words:
            c1 = freq1.get(word, 0)
            c2 = freq2.get(word, 0)
            total = c1 + c2
            if total < 10: continue # Skip rare words
            
            if c1 > 0 and c2 == 0:
                distinctive1.append((word, c1))
            elif c2 > 0 and c1 == 0:
                distinctive2.append((word, c2))
            elif c1 / total > 0.8:
                distinctive1.append((word, c1))
            elif c2 / total > 0.8:
                distinctive2.append((word, c2))
                
        # Sort by frequency
        distinctive1.sort(key=lambda x: -x[1])
        distinctive2.sort(key=lambda x: -x[1])
        
        # Display
        p1_words = ", ".join([w[0] for w in distinctive1[:15]])
        p2_words = ", ".join([w[0] for w in distinctive2[:15]])
        
        name1 = self.get_display_name(p1)
        name2 = self.get_display_name(p2)
        
        ax.text(0.25, 0.8, f"💙 Only {name1} uses:", fontsize=12, color=COLORS['person1'],
                ha='center', fontweight='bold', transform=ax.transAxes)
        
        ax.text(0.25, 0.5, p1_words, fontsize=11, color=COLORS['text_primary'],
                ha='center', va='top', wrap=True, transform=ax.transAxes)
                
        ax.text(0.75, 0.8, f"💖 Only {name2} uses:", fontsize=12, color=COLORS['person2'],
                ha='center', fontweight='bold', transform=ax.transAxes)
                
        ax.text(0.75, 0.5, p2_words, fontsize=11, color=COLORS['text_primary'],
                ha='center', va='top', wrap=True, transform=ax.transAxes)

    def _render_common_phrases(self, ax):
        """Analyze commonly used 3-word phrases."""
        ax.set_facecolor(COLORS['card_bg'])
        # Add border
        for spine in ax.spines.values():
            spine.set_color(COLORS['card_border'])
            spine.set_linewidth(2)
            
        ax.axis('off')
        ax.set_title("💞 Phrases You Both Use 💞", fontsize=16, color=COLORS['love_pink'], loc='center', pad=15)
        
        text_content = ""
        for msg in self.text_messages:
            text_content += " " + self._clean_text(msg.content)
            
        words = text_content.split()
        words = [w for w in words if len(w) > 0]
        
        # Generate trigrams (3 words)
        trigrams = [" ".join(words[i:i+3]) for i in range(len(words)-2)]
        
        # Filter trigrams that contain stopwords only (boring)
        filtered = []
        for t in trigrams:
            parts = t.split()
            # Keep if at least one word is NOT a stopword
            if any(w not in CUSTOM_STOPWORDS for w in parts):
                filtered.append(t)
                
        counts = Counter(filtered).most_common(10)
        
        phrases_text = "\n".join([f"✨ {phrase} ({count})" for phrase, count in counts])
        
        ax.text(0.5, 0.5, phrases_text, fontsize=12, color=COLORS['text_primary'],
                ha='center', va='center', transform=ax.transAxes, linespacing=1.8)

if __name__ == '__main__':
    from chat_parser import parse_whatsapp_chat
    
    file_path = '/Users/arvind/PythonProjects/Chatanaylsi/_chat.txt'
    output_path = '/Users/arvind/PythonProjects/Chatanaylsi/output/word_cloud_dashboard.png'

    print(f"Parsing {file_path}...")
    messages = parse_whatsapp_chat(file_path)

    participant_mapping = {
        "~~": "Arvind",
        "bae \U0001FAF6": "Palak"
    }
    
    print("Generating Word Cloud Dashboard...")
    generator = WordCloudGenerator(messages, participant_mapping)
    generator.create_dashboard(output_path)
    print("Done!")
