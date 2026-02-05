# WhatsApp Chat Analyzer

A comprehensive WhatsApp chat analysis tool that generates beautiful visual dashboards with relationship insights, communication patterns, and call statistics.

## Features

### 1. Main Dashboard (`whatsapp_analyzer.py`)
- **Relationship Rating** - Overall score based on communication patterns
- **Key Insights** - Personalized observations about the relationship
- **Message Statistics** - Total messages, balance, double-texting patterns
- **Response Metrics** - Average response time, immediate reply percentage
- **Topic Analysis** - Pie chart of conversation topics
- **Messaging Heatmap** - Activity by day of week and hour
- **Relationship Growth Timeline** - How communication evolved over time
- **Key Milestones** - First message, first call, first "I love you", etc.

### 2. Traits Analysis (`traits_dashboard.py`)
- **Good Traits** - Supportiveness, affection, humor, responsiveness
- **Growth Areas** - Areas for improvement with actionable suggestions
- **Communication Style Comparison** - Side-by-side comparison of both partners
- **Detailed Metrics** - Support rate, affection rate, question ratio, etc.

### 3. Video Call Analysis (`video_call_analyzer.py`)
- **Call Summary** - Total calls, video vs voice, missed calls
- **Time Statistics** - Total hours, average duration, longest calls
- **Who Initiates** - Call initiation patterns by person
- **Monthly Trends** - Call frequency over time
- **Call Heatmap** - When calls happen (day x hour)
- **Longest Calls** - Top 10 longest calls ever
- **Call Streaks** - Consecutive days with calls

## Installation

```bash
pip install matplotlib seaborn pandas numpy pillow python-dateutil
```

## Usage

1. Export your WhatsApp chat (Settings > Chats > Export Chat > Without Media)
2. Save as `_chat.txt` in the project directory
3. Update participant mapping in the scripts:
   ```python
   PARTICIPANT_MAPPING = {
       "Contact Name 1": "Display Name 1",
       "Contact Name 2": "Display Name 2"
   }
   ```
4. Run the analyzers:
   ```bash
   cd execution
   python whatsapp_analyzer.py      # Main dashboard
   python traits_dashboard.py        # Traits analysis
   python video_call_analyzer.py     # Call analysis
   ```

## Output

All dashboards are saved to the `output/` directory as PNG files:
- `dashboard.png` - Main relationship dashboard
- `traits_dashboard.png` - Good/bad traits analysis
- `videocall_dashboard.png` - Video call analysis

## Project Structure

```
├── execution/
│   ├── chat_parser.py          # WhatsApp format parser
│   ├── metrics_calculator.py   # Statistics computation
│   ├── topic_classifier.py     # Message categorization
│   ├── sentiment_analyzer.py   # Relationship insights
│   ├── dashboard_generator.py  # Main dashboard visualization
│   ├── traits_analyzer.py      # Good/bad traits analysis
│   ├── traits_dashboard.py     # Traits visualization
│   ├── video_call_analyzer.py  # Call analysis & dashboard
│   └── whatsapp_analyzer.py    # Main orchestrator
├── output/                     # Generated dashboards
├── .tmp/                       # Intermediate analysis files
└── README.md
```

## Supported WhatsApp Export Format

The parser supports the standard WhatsApp export format:
```
[DD/MM/YY, H:MM:SS AM/PM] Sender: Message content
```

Special content types detected:
- Images, videos, audio, stickers, GIFs, documents
- Video calls and voice calls (with duration)
- Missed calls
- Deleted messages
- Edited messages

## Privacy Note

Your chat data stays local. The `_chat.txt` file is excluded from git via `.gitignore`.

## License

MIT License
