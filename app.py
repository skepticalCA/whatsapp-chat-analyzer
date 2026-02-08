"""
WhatsApp Chat Analyzer - Streamlit Web App
Upload your WhatsApp chat export and get comprehensive analysis dashboards.
"""

import streamlit as st
import tempfile
import os
import sys
import gc
import matplotlib.pyplot as plt
from io import BytesIO
import streamlit.components.v1 as components

# Add execution directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'execution'))

from chat_parser import parse_whatsapp_chat, get_participants
from metrics_calculator import MetricsCalculator
from topic_classifier import TopicClassifier
from sentiment_analyzer import SentimentAnalyzer
from dashboard_generator import DashboardGenerator
from traits_analyzer import TraitsAnalyzer
from traits_dashboard import TraitsDashboardGenerator
from video_call_analyzer import VideoCallAnalyzer, VideoCallDashboard
from razorpay_handler import create_order, get_razorpay_keys
from flashcard_generator import FlashcardGenerator

# Payment configuration
PAYMENT_AMOUNT = 7900  # ₹79 in paise
PAYMENT_ENABLED = True

# Page config
st.set_page_config(
    page_title="Love Chat Analyzer",
    page_icon="💕",
    layout="wide"
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
STATE_DEFAULTS = {
    'page': 'landing',
    'payment_completed': False,
    'payment_id': None,
    'order_id': None,
    'show_checkout': False,
    'analysis_results': None,
    'blurred_previews': None,
    'uploaded_file_content': None,
    'participant_mapping': None,
    'participant_names': None,
}

for _key, _default in STATE_DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    /* Force light background */
    .stApp {
        background-color: #fff5f7 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffe4ec !important;
    }

    section[data-testid="stSidebar"] * {
        color: #333 !important;
    }

    /* All markdown text */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #333 !important;
        -webkit-text-fill-color: #333 !important;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        font-weight: bold !important;
    }

    .stButton > button:hover {
        box-shadow: 0 5px 20px rgba(255, 107, 157, 0.4) !important;
    }

    .stButton > button span, .stButton > button p {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #fff !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        border: 1px solid #ffb6c1 !important;
        box-shadow: 0 2px 8px rgba(196, 69, 105, 0.1) !important;
    }

    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] label p,
    div[data-testid="metric-container"] label span {
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
        opacity: 1 !important;
    }

    div[data-testid="metric-container"] div[data-testid="stMetricValue"],
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] div,
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] span,
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] p {
        color: #333 !important;
        -webkit-text-fill-color: #333 !important;
        opacity: 1 !important;
    }

    /* File uploader */
    div[data-testid="stFileUploader"] {
        background: #fff !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }

    div[data-testid="stFileUploader"] * {
        color: #333 !important;
        -webkit-text-fill-color: #333 !important;
    }

    div[data-testid="stFileUploader"] section {
        background: #fff !important;
        border: 2px dashed #ffb6c1 !important;
        border-radius: 10px !important;
    }

    div[data-testid="stFileUploader"] section > div {
        background: #fff !important;
    }

    div[data-testid="stFileUploader"] button {
        background: #ffe4ec !important;
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
        border: 1px solid #ffb6c1 !important;
    }

    div[data-testid="stFileUploader"] small {
        color: #888 !important;
        -webkit-text-fill-color: #888 !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: #fff !important;
    }

    [data-testid="stFileUploaderDropzone"] * {
        color: #666 !important;
        -webkit-text-fill-color: #666 !important;
        background: transparent !important;
    }

    /* Text inputs */
    .stTextInput > div > div {
        background: #fff !important;
    }

    .stTextInput input {
        color: #333 !important;
        background: #fff !important;
    }

    /* Info/warning/error boxes */
    .stAlert {
        background: #fff !important;
    }

    .stAlert * {
        color: #333 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #fff !important;
        gap: 4px !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: #ffe4ec !important;
        color: #333 !important;
    }

    .stTabs [data-baseweb="tab"] * {
        color: #333 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #fff !important;
        color: #333 !important;
    }

    .streamlit-expanderContent {
        background: #fff !important;
    }

    /* Footer */
    .footer-love {
        text-align: center !important;
        padding: 2rem !important;
    }

    .footer-love, .footer-love * {
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%) !important;
    }

    /* WhatsApp share button */
    .whatsapp-btn {
        display: inline-block;
        width: 100%;
        text-align: center;
        background: linear-gradient(135deg, #25D366, #128C7E);
        color: white !important;
        padding: 12px 20px;
        border-radius: 25px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 8px;
        box-shadow: 0 2px 10px rgba(37, 211, 102, 0.3);
        transition: box-shadow 0.3s ease, transform 0.2s ease;
    }
    .whatsapp-btn:hover {
        box-shadow: 0 5px 20px rgba(37, 211, 102, 0.5);
        transform: translateY(-1px);
        color: white !important;
        text-decoration: none;
    }

    /* ===== NEW: Landing page styles ===== */

    .hero-section {
        text-align: center;
        padding: 3rem 1rem 1rem;
    }

    .hero-section h1 {
        font-size: 2.2rem !important;
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
        font-weight: 800 !important;
        line-height: 1.3;
        margin-bottom: 0.5rem;
    }

    @media (min-width: 768px) {
        .hero-section h1 { font-size: 2.8rem !important; }
    }

    .hero-section .hook {
        font-size: 1.1rem;
        color: #e75480 !important;
        -webkit-text-fill-color: #e75480 !important;
        margin-top: 0.5rem;
    }

    .hero-section .sub-hook {
        font-size: 0.95rem;
        color: #888 !important;
        -webkit-text-fill-color: #888 !important;
        margin-top: 0.3rem;
    }

    /* Feature pointer grid */
    .pointer-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        padding: 1rem;
        max-width: 750px;
        margin: 0 auto;
    }
    @media (max-width: 768px) {
        .pointer-grid { grid-template-columns: repeat(2, 1fr); }
    }
    .pointer-item {
        background: #fff;
        padding: 0.9rem 0.7rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #ffccd5;
        font-size: 0.9rem;
        color: #555;
        box-shadow: 0 2px 8px rgba(255, 107, 157, 0.1);
    }
    .pointer-item .emoji { font-size: 1.4rem; display: block; margin-bottom: 0.4rem; }

    /* Steps section */
    .steps-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        justify-content: center;
        padding: 0.5rem 0;
    }
    .step-item {
        background: #fff;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #ffe0e8;
        min-width: 140px;
        flex: 1;
        max-width: 180px;
    }
    .step-item .step-emoji { font-size: 1.8rem; display: block; margin-bottom: 0.3rem; }
    .step-item .step-text { font-size: 0.85rem; color: #666; }

    /* Upload section */
    .upload-section {
        max-width: 600px;
        margin: 1.5rem auto;
        padding: 2rem;
        background: #fff;
        border-radius: 20px;
        border: 2px solid #ffb6c1;
        box-shadow: 0 4px 20px rgba(255, 107, 157, 0.15);
        text-align: center;
    }

    .upload-section h3 {
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
    }

    /* Paywall styles */
    .paywall-card {
        background: linear-gradient(135deg, #fff5f7 0%, #ffe4ec 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        border: 2px solid #ffb6c1;
        margin: 2rem auto;
        max-width: 500px;
        box-shadow: 0 4px 25px rgba(255, 107, 157, 0.2);
    }

    .paywall-card h2 {
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
        font-size: 1.8rem !important;
        margin-bottom: 0.5rem;
    }

    .paywall-price {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
        margin: 0.5rem 0;
    }

    .paywall-sub {
        color: #888 !important;
        -webkit-text-fill-color: #888 !important;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    .paywall-coffee {
        color: #e75480 !important;
        -webkit-text-fill-color: #e75480 !important;
        font-size: 0.95rem;
        font-style: italic;
    }

    /* Score reveal */
    .score-container {
        text-align: center;
        padding: 2rem;
        background: #fff;
        border-radius: 20px;
        border: 2px solid #ffb6c1;
        margin: 1rem auto;
        max-width: 400px;
        box-shadow: 0 4px 20px rgba(255, 107, 157, 0.15);
    }

    .score-label { color: #888; font-size: 1rem; margin-bottom: 0.5rem; }

    .score-value {
        font-size: 4.5rem;
        font-weight: 800;
        color: #c44569;
        line-height: 1;
    }

    .score-hidden {
        filter: blur(8px);
        user-select: none;
        -webkit-user-select: none;
    }

    .score-unit { font-size: 1.8rem; color: #ccc; font-weight: 400; }

    .score-unlock { color: #e75480; font-size: 0.95rem; margin-top: 0.8rem; }

    /* Locked cards */
    .locked-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    @media (max-width: 768px) {
        .locked-grid { grid-template-columns: 1fr; }
    }
    .locked-card {
        background: #fff;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #ffccd5;
        text-align: center;
        position: relative;
    }
    .locked-card .lock-icon {
        position: absolute;
        top: 10px;
        right: 12px;
        font-size: 1.3rem;
    }
    .locked-card h4 {
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
        margin-bottom: 0.5rem;
    }
    .locked-card .blurred-text {
        filter: blur(5px);
        user-select: none;
        -webkit-user-select: none;
        color: #666;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Trust badges */
    .trust-row {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
        margin: 1.5rem 0;
    }
    .trust-item {
        color: #888;
        font-size: 0.9rem;
    }

    /* Section divider */
    .heart-divider {
        text-align: center !important;
        font-size: 1.5rem !important;
        margin: 1.5rem 0 !important;
    }

    /* Love card */
    .love-card {
        background: #fff !important;
        padding: 1.5rem !important;
        border-radius: 20px !important;
        border: 2px solid #ffb6c1 !important;
        text-align: center !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3) !important;
    }

    .love-card h2, .love-card h3 {
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
    }

    .love-card p {
        color: #444 !important;
        -webkit-text-fill-color: #444 !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_blurred_preview(png_bytes, blur_radius=25):
    """Generate a heavily blurred version of a dashboard PNG for the paywall teaser."""
    from PIL import Image, ImageFilter
    img = Image.open(BytesIO(png_bytes))
    blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    buf = BytesIO()
    blurred.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


def get_loading_animation_html():
    """Return self-contained HTML/CSS/JS for the heart-fill loading animation."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; min-height: 520px;
        background: linear-gradient(135deg, #fff5f7 0%, #fce7f3 50%, #ffd6e7 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        overflow: hidden;
      }
      .heart-container {
        position: relative; width: 160px; height: 160px;
        margin-bottom: 2rem;
        animation: pulse 2.5s ease-in-out infinite;
      }
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.06); }
      }
      .heart-svg { width: 160px; height: 160px; }
      .heart-fill-rect {
        transform: translateY(100%);
        animation: fillUp 30s ease-in-out forwards;
      }
      @keyframes fillUp {
        0% { transform: translateY(100%); }
        100% { transform: translateY(0%); }
      }
      .status-text {
        font-size: 1.2rem; color: #c44569; font-weight: 500;
        text-align: center; padding: 0 2rem;
        opacity: 1; transition: opacity 0.5s ease;
        min-height: 1.5em;
      }
      .sub-text {
        font-size: 0.85rem; color: #e75480; margin-top: 0.8rem;
        opacity: 0.7;
      }
    </style>
    </head>
    <body>
      <div class="heart-container">
        <svg class="heart-svg" viewBox="0 0 100 90">
          <defs>
            <linearGradient id="fillGrad" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0%" stop-color="#ff6b9d"/>
              <stop offset="50%" stop-color="#e74580"/>
              <stop offset="100%" stop-color="#c44569"/>
            </linearGradient>
            <clipPath id="heartClip">
              <path d="M50,85 C25,60 0,45 0,25 A25,25,0,0,1,50,15
                       A25,25,0,0,1,100,25 C100,45 75,60 50,85Z"/>
            </clipPath>
          </defs>
          <path d="M50,85 C25,60 0,45 0,25 A25,25,0,0,1,50,15
                   A25,25,0,0,1,100,25 C100,45 75,60 50,85Z"
                stroke="#ffb6c1" stroke-width="1.5" fill="rgba(255,240,245,0.5)"/>
          <g clip-path="url(#heartClip)">
            <rect x="0" y="0" width="100" height="90"
                  fill="url(#fillGrad)" class="heart-fill-rect"/>
          </g>
        </svg>
      </div>
      <div class="status-text" id="statusText">Going through all your texts 💬</div>
      <div class="sub-text">This usually takes 15-30 seconds</div>
      <script>
        var msgs = [
          "Going through all your texts 💬",
          "Analyzing your love language ❤️",
          "Calculating reply speed ⏱️",
          "Detecting fight patterns 😤",
          "Analyzing attachment styles 🧠",
          "Measuring emotional balance 💞",
          "Scanning conversation trends 📊",
          "Building your dashboards 🎨",
          "Preparing your love report 💕"
        ];
        var i = 0;
        setInterval(function() {
          var el = document.getElementById('statusText');
          el.style.opacity = '0';
          setTimeout(function() {
            i = (i + 1) % msgs.length;
            el.textContent = msgs[i];
            el.style.opacity = '1';
          }, 500);
        }, 3000);
      </script>
    </body>
    </html>
    '''


def run_analysis_pipeline():
    """Run the full analysis pipeline and store results + blurred previews in session state."""
    content = st.session_state.uploaded_file_content
    participant_mapping = st.session_state.participant_mapping

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name

    try:
        messages = parse_whatsapp_chat(temp_path)

        if len(messages) < 10:
            st.session_state.analysis_results = {'error': 'Not enough messages found. Please upload a valid WhatsApp chat export.'}
            return

        metrics = MetricsCalculator(messages, participant_mapping)
        topics = TopicClassifier(messages)
        sentiment = SentimentAnalyzer(messages, metrics, participant_mapping)
        traits = TraitsAnalyzer(messages, metrics, participant_mapping)
        calls = VideoCallAnalyzer(messages, participant_mapping)

        output_dir = tempfile.mkdtemp()

        dashboard_status = {'main': False, 'traits': False, 'calls': False}
        dashboard_errors = {}
        dashboard_bytes = {}

        # Main dashboard
        main_path = os.path.join(output_dir, 'dashboard.png')
        try:
            main_dashboard = DashboardGenerator(messages, metrics, sentiment, topics, participant_mapping)
            main_dashboard.create_dashboard(main_path)
            if os.path.exists(main_path):
                dashboard_status['main'] = True
                with open(main_path, 'rb') as f:
                    dashboard_bytes['main'] = f.read()
            else:
                dashboard_errors['main'] = "File was not created"
        except Exception as e:
            dashboard_errors['main'] = str(e)
        finally:
            plt.close('all')
            gc.collect()

        # Traits dashboard
        traits_path = os.path.join(output_dir, 'traits_dashboard.png')
        try:
            traits_dashboard = TraitsDashboardGenerator(traits, participant_mapping)
            traits_dashboard.create_dashboard(traits_path)
            if os.path.exists(traits_path):
                dashboard_status['traits'] = True
                with open(traits_path, 'rb') as f:
                    dashboard_bytes['traits'] = f.read()
            else:
                dashboard_errors['traits'] = "File was not created"
        except Exception as e:
            dashboard_errors['traits'] = str(e)
        finally:
            plt.close('all')
            gc.collect()

        # Call dashboard
        call_path = os.path.join(output_dir, 'videocall_dashboard.png')
        try:
            call_dashboard = VideoCallDashboard(calls, participant_mapping)
            call_dashboard.create_dashboard(call_path)
            if os.path.exists(call_path):
                dashboard_status['calls'] = True
                with open(call_path, 'rb') as f:
                    dashboard_bytes['calls'] = f.read()
            else:
                dashboard_errors['calls'] = "File was not created"
        except Exception as e:
            dashboard_errors['calls'] = str(e)
        finally:
            plt.close('all')
            gc.collect()

        # Generate flashcards
        flashcard_data = []
        try:
            flashcard_gen = FlashcardGenerator(metrics, sentiment, calls, participant_mapping)
            raw_cards = flashcard_gen.generate_all_cards()
            for card in raw_cards:
                flashcard_data.append({
                    'image_bytes': FlashcardGenerator.image_to_bytes(card['image']),
                    'title': card['title'],
                    'share_text': card['share_text'],
                })
        except Exception:
            pass

        # Gather stats
        msg_counts = metrics.get_message_counts()
        call_summary = calls.get_call_summary()
        rating_label, rating_desc, rating_score = sentiment.calculate_relationship_rating()
        start, end = metrics.get_date_range()
        total_days = metrics.get_total_days()
        insights = sentiment.generate_key_insights()
        avg_response = metrics.get_average_response_time()

        # Store in session state
        st.session_state.analysis_results = {
            'dashboard_status': dashboard_status,
            'dashboard_errors': dashboard_errors,
            'dashboard_bytes': dashboard_bytes,
            'flashcards': flashcard_data,
            'msg_count': len(messages),
            'msg_counts': msg_counts,
            'call_summary': call_summary,
            'rating_label': rating_label,
            'rating_score': rating_score,
            'date_start': start.strftime('%b %d, %Y'),
            'date_end': end.strftime('%b %d, %Y'),
            'total_days': total_days,
            'insights': insights,
            'avg_response': avg_response,
            'participant_mapping': participant_mapping,
        }

        # Generate blurred previews for paywall
        blurred = {}
        for key, img_bytes in dashboard_bytes.items():
            try:
                blurred[key] = generate_blurred_preview(img_bytes, blur_radius=25)
            except Exception:
                pass
        st.session_state.blurred_previews = blurred

    finally:
        try:
            os.unlink(temp_path)
        except Exception:
            pass


# ============================================================
# PAGE: LANDING
# ============================================================

def render_landing_page():
    # Hero section
    st.markdown('''
    <div class="hero-section">
        <h1>What your chats secretly say<br>about your relationship 👀</h1>
        <p class="hook">We analyzed our chats… the results shocked us 💀</p>
        <p class="sub-hook">Now you can also upload your chats and discover the truth.</p>
    </div>
    ''', unsafe_allow_html=True)

    # Feature pointers
    st.markdown('''
    <div style="text-align:center; margin: 1.5rem 0 0.5rem;">
        <h3 style="color: #c44569 !important; -webkit-text-fill-color: #c44569 !important;">
            Here's what our analysis will reveal 👀
        </h3>
    </div>
    <div class="pointer-grid">
        <div class="pointer-item"><span class="emoji">❤️</span> Who loves more</div>
        <div class="pointer-item"><span class="emoji">📊</span> Compatibility score</div>
        <div class="pointer-item"><span class="emoji">⏱️</span> Who replies faster</div>
        <div class="pointer-item"><span class="emoji">📉</span> Effort imbalance</div>
        <div class="pointer-item"><span class="emoji">😤</span> Who starts fights</div>
        <div class="pointer-item"><span class="emoji">💔</span> Hidden conflict patterns</div>
        <div class="pointer-item"><span class="emoji">📞</span> Who calls more</div>
        <div class="pointer-item"><span class="emoji">🔁</span> Conversation trends</div>
        <div class="pointer-item"><span class="emoji">🧠</span> Texting personality types</div>
    </div>
    ''', unsafe_allow_html=True)

    # Steps to follow (collapsible)
    with st.expander("📋 Steps to follow"):
        st.markdown('''
        <div class="steps-grid">
            <div class="step-item">
                <span class="step-emoji">1️⃣</span>
                <span class="step-text">Open WhatsApp chat 💬</span>
            </div>
            <div class="step-item">
                <span class="step-emoji">2️⃣</span>
                <span class="step-text">Export without media 📤</span>
            </div>
            <div class="step-item">
                <span class="step-emoji">3️⃣</span>
                <span class="step-text">Upload file below 📁</span>
            </div>
            <div class="step-item">
                <span class="step-emoji">4️⃣</span>
                <span class="step-text">We analyse 🤖</span>
            </div>
            <div class="step-item">
                <span class="step-emoji">5️⃣</span>
                <span class="step-text">Unlock report 💕</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # Upload section
    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload your WhatsApp chat export (.txt file)",
        type=['txt'],
        help="Export from WhatsApp: Open chat → Tap ⋮ → More → Export Chat → Without Media",
        key='chat_uploader'
    )

    if uploaded_file:
        content = uploaded_file.read().decode('utf-8')
        st.session_state.uploaded_file_content = content

        # Quick parse to get participant names
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            quick_temp = f.name

        try:
            messages = parse_whatsapp_chat(quick_temp)
            if len(messages) >= 10:
                participants = get_participants(messages)
                st.session_state.participant_names = participants

                st.success(f"Found **{len(messages):,}** messages!")

                st.markdown("### 👩‍❤️‍👨 Who's in this love story?")
                col1, col2 = st.columns(2)
                mapping = {}

                for i, participant in enumerate(participants[:2]):
                    with col1 if i == 0 else col2:
                        display_name = st.text_input(
                            f"Name for '{participant}'",
                            value=participant.split()[0] if ' ' in participant else participant,
                            key=f"name_{i}"
                        )
                        mapping[participant] = display_name

                st.session_state.participant_mapping = mapping

                # CTA button
                st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
                if st.button("Reveal Our Chat Insights 👀", type="primary", use_container_width=True):
                    st.session_state.page = 'loading'
                    st.rerun()
            else:
                st.error("Could not parse enough messages. Please upload a valid WhatsApp chat export (.txt file).")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
        finally:
            try:
                os.unlink(quick_temp)
            except Exception:
                pass

    elif st.session_state.uploaded_file_content and st.session_state.participant_names:
        # File was uploaded in a previous rerun but widget reset - show names + CTA
        participants = st.session_state.participant_names
        st.markdown("### 👩‍❤️‍👨 Who's in this love story?")
        col1, col2 = st.columns(2)
        mapping = st.session_state.participant_mapping or {}

        for i, participant in enumerate(participants[:2]):
            with col1 if i == 0 else col2:
                display_name = st.text_input(
                    f"Name for '{participant}'",
                    value=mapping.get(participant, participant.split()[0] if ' ' in participant else participant),
                    key=f"name_{i}"
                )
                mapping[participant] = display_name

        st.session_state.participant_mapping = mapping

        if st.button("Reveal Our Chat Insights 👀", type="primary", use_container_width=True):
            st.session_state.page = 'loading'
            st.rerun()


# ============================================================
# PAGE: LOADING
# ============================================================

def render_loading_screen():
    # Show animation
    components.html(get_loading_animation_html(), height=580, scrolling=False)

    # Run analysis (browser shows animation while server computes)
    try:
        run_analysis_pipeline()
    except Exception as e:
        st.session_state.analysis_results = {'error': str(e)}

    # Transition to preview
    st.session_state.page = 'preview'
    st.rerun()


# ============================================================
# PAGE: BLURRED PREVIEW + PAYWALL
# ============================================================

def render_blurred_preview():
    r = st.session_state.analysis_results
    if not r:
        st.session_state.page = 'landing'
        st.rerun()
        return

    if r.get('error'):
        st.error(f"Analysis failed: {r['error']}")
        if st.button("Try Again", type="primary"):
            st.session_state.page = 'landing'
            st.session_state.analysis_results = None
            st.rerun()
        return

    key_id, key_secret = get_razorpay_keys()
    razorpay_configured = bool(key_id and key_secret)

    # If payment not needed or already completed, go to results
    if not PAYMENT_ENABLED or not razorpay_configured or st.session_state.payment_completed:
        st.session_state.page = 'results'
        st.rerun()
        return

    # ---- Blurred preview ----

    st.markdown('''
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <h2 style="color: #c44569 !important; -webkit-text-fill-color: #c44569 !important;">
            Your analysis is complete! ✨
        </h2>
    </div>
    ''', unsafe_allow_html=True)

    # Relationship score with last digit blurred
    score = r.get('rating_score', 0)
    tens = int(score) // 10
    ones = int(score) % 10

    st.markdown(f'''
    <div class="score-container">
        <div class="score-label">Your Relationship Score</div>
        <div class="score-value">
            {tens}<span class="score-hidden">{ones}</span><span class="score-unit">/100</span>
        </div>
        <div class="score-label" style="margin-top: 0.5rem;">❤️ {r.get('rating_label', '')}</div>
        <div class="score-unlock">🔒 Unlock to see your full score</div>
    </div>
    ''', unsafe_allow_html=True)

    # Blurred dashboard preview
    blurred = st.session_state.blurred_previews or {}
    if 'main' in blurred:
        st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
        st.image(blurred['main'], use_container_width=True,
                 caption="🔒 Your relationship dashboard — unlock to view in full detail")

    # Locked insight cards
    st.markdown(f'''
    <div class="locked-grid">
        <div class="locked-card">
            <span class="lock-icon">🔒</span>
            <h4>💕 Compatibility</h4>
            <div class="blurred-text">
                Your communication patterns reveal a deep connection.
                Message balance shows healthy engagement from both sides.
            </div>
        </div>
        <div class="locked-card">
            <span class="lock-icon">🔒</span>
            <h4>🎭 Personality Traits</h4>
            <div class="blurred-text">
                5 strengths and growth areas identified for each partner.
                Detailed behavioral analysis from your texts.
            </div>
        </div>
        <div class="locked-card">
            <span class="lock-icon">🔒</span>
            <h4>📊 Communication</h4>
            <div class="blurred-text">
                Response patterns, conversation starters, and message
                timing analysis across {r.get('total_days', 0)} days.
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # ---- Paywall ----

    st.markdown(f'''
    <div class="paywall-card">
        <h2>Your love report is ready 💕</h2>
        <p class="paywall-sub">Unlock your full relationship insights</p>
        <div class="paywall-price">₹79</div>
        <p class="paywall-sub">One-time unlock</p>
        <p class="paywall-coffee">Less than a cup of coffee ☕</p>
    </div>
    ''', unsafe_allow_html=True)

    # Payment CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Unlock My Love Report 💕", type="primary", use_container_width=True):
            order = create_order(PAYMENT_AMOUNT)
            if order:
                st.session_state.order_id = order['id']
                st.session_state.show_checkout = True
                st.rerun()
            else:
                st.error("Failed to create order. Please try again.")

    # Razorpay checkout
    if st.session_state.show_checkout and st.session_state.order_id:
        st.markdown("---")
        checkout_html = f'''
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        <div id="razorpay-container" style="text-align: center; padding: 20px;">
            <button id="pay-btn" style="
                background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%);
                color: white;
                padding: 18px 50px;
                font-size: 18px;
                border: none;
                border-radius: 30px;
                cursor: pointer;
                font-weight: bold;
                box-shadow: 0 4px 15px rgba(255, 107, 157, 0.4);
            ">💕 Pay ₹79 Now</button>
            <p style="color: #666; margin-top: 15px;">Click to open secure payment window</p>
        </div>
        <script>
            var options = {{
                "key": "{key_id}",
                "amount": "{PAYMENT_AMOUNT}",
                "currency": "INR",
                "name": "Love Chat Analyzer",
                "description": "Unlock Your Love Report",
                "order_id": "{st.session_state.order_id}",
                "handler": function (response) {{
                    localStorage.setItem('razorpay_payment_id', response.razorpay_payment_id);
                    document.getElementById('razorpay-container').innerHTML =
                        '<div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 25px; border-radius: 15px;">' +
                        '<h3 style="color: #155724;">💕 Payment Successful!</h3>' +
                        '<p style="color: #155724;">Click the button below to unlock your report</p>' +
                        '<p style="color: #666; font-size: 12px; margin-top: 10px;">Payment ID: ' + response.razorpay_payment_id + '</p></div>';
                }},
                "theme": {{
                    "color": "#c44569"
                }},
                "modal": {{
                    "ondismiss": function() {{
                        document.getElementById('razorpay-container').innerHTML +=
                            '<p style="color: #dc3545; margin-top: 10px;">Payment cancelled. Click the button to try again.</p>';
                    }}
                }}
            }};
            var rzp = new Razorpay(options);
            document.getElementById('pay-btn').onclick = function(e) {{
                rzp.open();
                e.preventDefault();
            }};
        </script>
        '''
        components.html(checkout_html, height=250)

        st.markdown("---")
        st.markdown("**After completing payment, click below:**")

        if st.button("✅ I've Completed Payment — Unlock Results", type="primary", use_container_width=True):
            import requests
            try:
                response = requests.get(
                    f"https://api.razorpay.com/v1/orders/{st.session_state.order_id}",
                    auth=(key_id, key_secret)
                )
                if response.status_code == 200:
                    order_data = response.json()
                    if order_data.get('status') == 'paid':
                        st.session_state.payment_completed = True
                        st.session_state.show_checkout = False
                        st.session_state.page = 'results'
                        st.balloons()
                        st.rerun()
                    else:
                        st.warning("Payment not yet received. Please complete the payment first, then click this button.")
                else:
                    st.error("Could not verify payment. Please try again.")
            except Exception:
                st.error("Verification error. Please try again.")

    # Trust badges
    st.markdown('''
    <div class="trust-row">
        <span class="trust-item">🔒 Secure payment</span>
        <span class="trust-item">⚡ Instant unlock</span>
        <span class="trust-item">💬 Results ready immediately</span>
    </div>
    ''', unsafe_allow_html=True)

    # Analyze new chat option
    st.markdown("---")
    if st.button("← Upload a different chat", key="back_to_landing"):
        for key, default in STATE_DEFAULTS.items():
            st.session_state[key] = default
        st.rerun()


# ============================================================
# PAGE: FULL RESULTS
# ============================================================

def render_full_results():
    r = st.session_state.analysis_results
    if not r or r.get('error'):
        st.session_state.page = 'landing'
        st.rerun()
        return

    # Safety: if payment required but not completed, go to preview
    key_id, key_secret = get_razorpay_keys()
    razorpay_configured = bool(key_id and key_secret)
    if PAYMENT_ENABLED and razorpay_configured and not st.session_state.payment_completed:
        st.session_state.page = 'preview'
        st.rerun()
        return

    st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)

    # Quick stats
    st.markdown("### 💕 Your Love at a Glance")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💬 Messages", f"{r['msg_count']:,}")
    with col2:
        st.metric("💯 Love Score", f"{r['rating_score']:.0f}/100")
    with col3:
        st.metric("📞 Calls", f"{r['call_summary']['total_calls']:,}")
    with col4:
        st.metric("⏰ Hours Talking", f"{r['call_summary']['total_call_time_hours']:.1f}")

    st.info(f"💕 Your journey: **{r['date_start']}** to **{r['date_end']}** ({r['total_days']} days of love)")

    st.markdown("### 💡 Key Insights About Your Love")
    for insight in r['insights']:
        st.markdown(f"💕 {insight}")

    st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)
    st.markdown("### 📊 Your Love Dashboards")

    # PDF Export
    pdf_images = []
    for key in ['main', 'traits', 'calls']:
        if r['dashboard_status'].get(key) and key in r['dashboard_bytes']:
            pdf_images.append(r['dashboard_bytes'][key])

    if pdf_images:
        from PIL import Image as PILImage
        pil_pages = []
        for img_bytes in pdf_images:
            pil_pages.append(PILImage.open(BytesIO(img_bytes)).convert('RGB'))

        pdf_buffer = BytesIO()
        if len(pil_pages) == 1:
            pil_pages[0].save(pdf_buffer, format='PDF')
        else:
            pil_pages[0].save(pdf_buffer, format='PDF', save_all=True,
                              append_images=pil_pages[1:])
        pdf_buffer.seek(0)

        st.download_button(
            "📄 Export All Dashboards as PDF",
            pdf_buffer.getvalue(),
            file_name="love_analysis_complete.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="export_pdf"
        )

    tab1, tab2, tab3 = st.tabs(["💕 Main Dashboard", "🎭 Traits Analysis", "📞 Call Statistics"])

    with tab1:
        if r['dashboard_status']['main'] and 'main' in r['dashboard_bytes']:
            st.image(r['dashboard_bytes']['main'], use_container_width=True)
            st.download_button(
                "💕 Download Main Dashboard",
                r['dashboard_bytes']['main'],
                file_name="love_dashboard.png",
                mime="image/png",
                use_container_width=True,
                key="dl_main"
            )
        else:
            st.error(f"💔 Main dashboard could not be generated. Error: {r['dashboard_errors'].get('main', 'Unknown error')}")

    with tab2:
        if r['dashboard_status']['traits'] and 'traits' in r['dashboard_bytes']:
            st.image(r['dashboard_bytes']['traits'], use_container_width=True)
            st.download_button(
                "💕 Download Traits Dashboard",
                r['dashboard_bytes']['traits'],
                file_name="traits_dashboard.png",
                mime="image/png",
                use_container_width=True,
                key="dl_traits"
            )
        else:
            st.error(f"💔 Traits dashboard could not be generated. Error: {r['dashboard_errors'].get('traits', 'Unknown error')}")

    with tab3:
        if r['dashboard_status']['calls'] and 'calls' in r['dashboard_bytes']:
            st.image(r['dashboard_bytes']['calls'], use_container_width=True)
            st.download_button(
                "💕 Download Call Dashboard",
                r['dashboard_bytes']['calls'],
                file_name="call_dashboard.png",
                mime="image/png",
                use_container_width=True,
                key="dl_calls"
            )
        else:
            st.error(f"💔 Call dashboard could not be generated. Error: {r['dashboard_errors'].get('calls', 'Unknown error')}")

    # Flashcards
    if r.get('flashcards'):
        st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)
        st.markdown("### 💕 Share Your Love Story")
        st.markdown("Download your flashcard, then share it with your love on WhatsApp!")

        for i in range(0, len(r['flashcards']), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(r['flashcards']):
                    card = r['flashcards'][idx]
                    with col:
                        st.image(card['image_bytes'], caption=card['title'],
                                 use_container_width=True)

                        dl_col, share_col = st.columns(2)
                        with dl_col:
                            st.download_button(
                                "📥 Save Image",
                                card['image_bytes'],
                                file_name=f"love_flashcard_{idx + 1}.png",
                                mime="image/png",
                                use_container_width=True,
                                key=f"flashcard_dl_{idx}"
                            )
                        with share_col:
                            share_url = FlashcardGenerator.get_whatsapp_share_url(
                                card['share_text']
                            )
                            st.markdown(
                                f'<a href="{share_url}" target="_blank" '
                                f'class="whatsapp-btn">'
                                f'WhatsApp</a>',
                                unsafe_allow_html=True
                            )

    with st.expander("📋 Detailed Statistics"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**💬 Message Counts:**")
            for sender, count in r['msg_counts'].items():
                name = r['participant_mapping'].get(sender, sender)
                st.markdown(f"• {name}: {count:,} messages")

            st.markdown("**⏰ Response Times:**")
            for sender, time in r['avg_response'].items():
                name = r['participant_mapping'].get(sender, sender)
                st.markdown(f"• {name}: {time:.1f} min average")

        with col2:
            st.markdown("**📞 Call Statistics:**")
            st.markdown(f"• Video calls: {r['call_summary']['total_video_calls']:,}")
            st.markdown(f"• Voice calls: {r['call_summary']['total_voice_calls']:,}")
            st.markdown(f"• Total time: {r['call_summary']['total_call_time_hours']:.1f} hours")
            st.markdown(f"• Longest call: {r['call_summary']['longest_video_call_min']:.0f} min")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 💝 Love Chat Analyzer")

    if st.session_state.page in ('preview', 'results'):
        st.markdown("---")
        if st.button("🔄 Analyze New Chat"):
            for key, default in STATE_DEFAULTS.items():
                st.session_state[key] = default
            st.rerun()

    st.markdown("---")
    st.markdown("### 🔒 Your Privacy")
    st.markdown("""
- Chat processed securely
- Nothing is stored
- Analysis in real-time
    """)

    st.markdown("---")
    st.markdown("### 💝 What You'll Discover")
    st.markdown("""
- 💯 **Relationship Score**
- 💬 **Message Patterns**
- ⏰ **Response Times**
- 🎭 **Communication Traits**
- 📞 **Call Statistics**
- 📈 **Love Timeline**
    """)


# ============================================================
# PAGE ROUTER (main)
# ============================================================

page = st.session_state.page

# Safety guards
if page in ('preview', 'results') and not st.session_state.analysis_results:
    st.session_state.page = 'landing'
    page = 'landing'

if page == 'results' and not st.session_state.payment_completed:
    key_id, key_secret = get_razorpay_keys()
    if PAYMENT_ENABLED and bool(key_id and key_secret):
        st.session_state.page = 'preview'
        page = 'preview'

if page == 'landing':
    render_landing_page()
elif page == 'loading':
    render_loading_screen()
elif page == 'preview':
    render_blurred_preview()
elif page == 'results':
    render_full_results()

# Footer
st.markdown("---")
st.markdown("""
<p class="footer-love">
    Made with 💕 for lovers everywhere<br>
    <a href="https://github.com/skepticalCA/whatsapp-chat-analyzer">GitHub</a>
</p>
""", unsafe_allow_html=True)
