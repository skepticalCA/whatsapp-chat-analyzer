# WhatsApp Chat Analyzer

A comprehensive WhatsApp chat analysis tool that generates beautiful visual dashboards with relationship insights, communication patterns, and call statistics.

## 🌐 Try It Online

**[Launch Web App](https://whatsapp-chat-analyzer.streamlit.app)** - Upload your chat and get instant analysis!

## Features

### 1. Main Dashboard
- **Relationship Rating** - Overall score based on communication patterns
- **Key Insights** - Personalized observations about the relationship
- **Message Statistics** - Total messages, balance, double-texting patterns
- **Response Metrics** - Average response time, immediate reply percentage
- **Topic Analysis** - Pie chart of conversation topics
- **Messaging Heatmap** - Activity by day of week and hour
- **Relationship Growth Timeline** - How communication evolved over time
- **Key Milestones** - First message, first call, first "I love you", etc.

### 2. Traits Analysis
- **Good Traits** - Supportiveness, affection, humor, responsiveness
- **Growth Areas** - Areas for improvement with actionable suggestions
- **Communication Style Comparison** - Side-by-side comparison of both partners
- **Detailed Metrics** - Support rate, affection rate, question ratio, etc.

### 3. Video Call Analysis
- **Call Summary** - Total calls, video vs voice, missed calls
- **Time Statistics** - Total hours, average duration, longest calls
- **Who Initiates** - Call initiation patterns by person
- **Monthly Trends** - Call frequency over time
- **Call Heatmap** - When calls happen (day x hour)
- **Longest Calls** - Top 10 longest calls ever
- **Call Streaks** - Consecutive days with calls

## 🚀 Quick Start (Web App)

1. Export your WhatsApp chat:
   - Open chat → ⋮ Menu → **More** → **Export chat** → **Without media**
2. Go to the [web app](https://whatsapp-chat-analyzer.streamlit.app)
3. Upload your `.txt` file
4. Get your dashboards!

## 💻 Local Installation

```bash
# Clone the repository
git clone https://github.com/skepticalCA/whatsapp-chat-analyzer.git
cd whatsapp-chat-analyzer

# Install dependencies
pip install -r requirements.txt

# Run the web app locally
streamlit run app.py
```

### Command Line Usage

```bash
cd execution
python whatsapp_analyzer.py      # Main dashboard
python traits_dashboard.py        # Traits analysis
python video_call_analyzer.py     # Call analysis
```

## Project Structure

```
├── app.py                      # Streamlit web app
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
├── requirements.txt
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

## 🔒 Privacy

- **Web App**: Your chat is processed in-memory and never stored
- **Local**: All data stays on your machine
- Chat files are excluded from git via `.gitignore`

## 💳 Payment Integration (Optional)

The app supports Razorpay payment integration. Users can be required to pay ₹99 before accessing the analysis.

### Setting up Razorpay

1. Create a [Razorpay account](https://razorpay.com/)
2. Get your API keys from Dashboard → Settings → API Keys
3. Add secrets to Streamlit Cloud:
   - Go to your app settings on [share.streamlit.io](https://share.streamlit.io)
   - Click "Secrets" in the left sidebar
   - Add your keys:
   ```toml
   RAZORPAY_KEY_ID = "rzp_live_xxxxxxxxxxxx"
   RAZORPAY_KEY_SECRET = "xxxxxxxxxxxxxxxxxxxx"
   ```

### Disabling Payment

To run the app without payment requirement:
- Don't set the Razorpay environment variables, OR
- Set `PAYMENT_ENABLED = False` in `app.py`

## License

MIT License
