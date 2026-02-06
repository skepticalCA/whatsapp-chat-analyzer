"""
WhatsApp Chat Analyzer - Streamlit Web App
Upload your WhatsApp chat export and get comprehensive analysis dashboards.
"""

import streamlit as st
import tempfile
import os
import sys
from datetime import datetime
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
from razorpay_handler import create_order, verify_payment_signature, get_razorpay_keys, verify_payment_by_id

# Payment configuration
PAYMENT_AMOUNT = 9900  # ₹99 in paise
PAYMENT_ENABLED = True  # Set to False to disable payment requirement

# Page config
st.set_page_config(
    page_title="Love Chat Analyzer",
    page_icon="💕",
    layout="wide"
)

# Fixed CSS - works in both light and dark mode
st.markdown("""
<style>
    /* Force light background for main content area */
    .stApp {
        background-color: #fff5f7 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffe4ec !important;
    }

    section[data-testid="stSidebar"] * {
        color: #333 !important;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: #333 !important;
    }

    /* Main header */
    .main-header {
        font-size: 2.2rem !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 1rem !important;
        color: #c44569 !important;
        background: none !important;
        -webkit-text-fill-color: #c44569 !important;
    }

    @media (min-width: 768px) {
        .main-header {
            font-size: 3rem !important;
        }
    }

    .sub-header {
        text-align: center !important;
        color: #e75480 !important;
        margin-bottom: 2rem !important;
        font-size: 1rem !important;
        -webkit-text-fill-color: #e75480 !important;
    }

    /* Love card - solid background */
    .love-card {
        background: #fff !important;
        padding: 1.5rem !important;
        border-radius: 20px !important;
        border: 2px solid #ffb6c1 !important;
        text-align: center !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3) !important;
    }

    .love-card h2 {
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
        font-size: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    .love-card h3 {
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
        margin-bottom: 0.5rem !important;
    }

    .love-card p {
        color: #444 !important;
        -webkit-text-fill-color: #444 !important;
    }

    /* Feature cards container */
    .feature-container {
        display: flex !important;
        gap: 1rem !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        margin: 1rem 0 !important;
    }

    .feature-card {
        background: #fff !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        border-left: 4px solid #ff6b9d !important;
        border-top: 1px solid #ffccd5 !important;
        border-right: 1px solid #ffccd5 !important;
        border-bottom: 1px solid #ffccd5 !important;
        flex: 1 1 280px !important;
        max-width: 350px !important;
        min-height: 160px !important;
        display: flex !important;
        flex-direction: column !important;
        box-shadow: 0 2px 10px rgba(255, 107, 157, 0.15) !important;
    }

    .feature-card h3 {
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.75rem !important;
    }

    .feature-card p {
        color: #555 !important;
        -webkit-text-fill-color: #555 !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
        flex-grow: 1 !important;
    }

    .price-tag {
        font-size: 3rem !important;
        font-weight: bold !important;
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
        text-align: center !important;
    }

    .price-subtitle {
        color: #666 !important;
        -webkit-text-fill-color: #666 !important;
        text-align: center !important;
        font-size: 0.9rem !important;
    }

    .heart-divider {
        text-align: center !important;
        font-size: 1.5rem !important;
        margin: 1.5rem 0 !important;
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

    /* All markdown text in main area */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #333 !important;
        -webkit-text-fill-color: #333 !important;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #fff !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        border: 1px solid #ffb6c1 !important;
    }

    div[data-testid="metric-container"] label {
        color: #c44569 !important;
        -webkit-text-fill-color: #c44569 !important;
    }

    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #333 !important;
        -webkit-text-fill-color: #333 !important;
    }

    /* File uploader */
    div[data-testid="stFileUploader"] {
        background: #fff !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }

    div[data-testid="stFileUploader"] * {
        color: #333 !important;
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

    /* Trust badges */
    .trust-badge {
        text-align: center !important;
        color: #555 !important;
        -webkit-text-fill-color: #555 !important;
        font-size: 0.9rem !important;
    }

    /* Success message */
    .stSuccess {
        background: #d4edda !important;
    }

    .stSuccess * {
        color: #155724 !important;
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Header with romantic theme
st.markdown('<h1 class="main-header">💕 Love Chat Analyzer 💕</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Discover the beautiful story hidden in your conversations</p>', unsafe_allow_html=True)

# Initialize session state for payment
if 'payment_completed' not in st.session_state:
    st.session_state.payment_completed = False
if 'payment_id' not in st.session_state:
    st.session_state.payment_id = None
if 'order_id' not in st.session_state:
    st.session_state.order_id = None
if 'show_checkout' not in st.session_state:
    st.session_state.show_checkout = False

# Sidebar with romantic theme
with st.sidebar:
    st.markdown("### 💌 How to Export Your Chat")
    st.markdown("""
**From WhatsApp:**
1. Open your special chat 💕
2. Tap ⋮ → **More** → **Export chat**
3. Select **Without media**
4. Save the `.txt` file

---

**🔒 Your Privacy Matters**
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

# Main content
key_id, key_secret = get_razorpay_keys()
razorpay_configured = bool(key_id and key_secret)

# Payment flow with romantic landing page
if PAYMENT_ENABLED and razorpay_configured and not st.session_state.payment_completed:

    # Hero section
    st.markdown("""
    <div class="love-card">
        <h2>✨ Unlock Your Love Story ✨</h2>
        <p>Transform your WhatsApp chats into beautiful insights about your relationship</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)

    # Features - using HTML for proper alignment
    st.markdown("""
    <div class="feature-container">
        <div class="feature-card">
            <h3>💯 Relationship Score</h3>
            <p>Get a comprehensive score based on your communication patterns, response times, and emotional connection.</p>
        </div>
        <div class="feature-card">
            <h3>🎭 Personality Insights</h3>
            <p>Discover your communication styles, good traits, and areas where you can grow together.</p>
        </div>
        <div class="feature-card">
            <h3>📞 Call Analysis</h3>
            <p>See your video call patterns, longest calls, and how your connection has grown over time.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)

    # What you get section
    st.markdown("### 🎁 What's Included")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
**📊 3 Beautiful Dashboards:**
- Main Relationship Dashboard
- Traits & Personality Analysis
- Video Call Statistics

**📈 Key Metrics:**
- Message balance & patterns
- Response time analysis
- Topic distribution
        """)

    with col2:
        st.markdown("""
**💡 Personalized Insights:**
- Relationship strengths
- Growth opportunities
- Communication comparison

**📥 Downloadable:**
- High-quality PNG dashboards
- Share with your partner!
        """)

    st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)

    # Pricing section
    st.markdown("""
    <div class="love-card">
        <p style="color: #888 !important; margin-bottom: 0;">One-time payment</p>
        <div class="price-tag">₹99</div>
        <p class="price-subtitle">Less than a cup of coffee ☕</p>
        <p style="color: #666 !important; margin-top: 1rem;">💳 UPI • Cards • Net Banking • Wallets</p>
    </div>
    """, unsafe_allow_html=True)

    # CTA Button
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💕 Unlock Your Love Story - ₹99", type="primary", use_container_width=True):
            order = create_order(PAYMENT_AMOUNT)
            if order:
                st.session_state.order_id = order['id']
                st.session_state.show_checkout = True
                st.rerun()
            else:
                st.error("Failed to create order. Please try again.")

    # Checkout flow - simplified without manual payment ID
    if st.session_state.show_checkout and st.session_state.order_id:
        st.markdown("---")
        st.markdown("### 💳 Complete Your Payment")

        # Razorpay checkout with auto-callback
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
            ">💕 Pay ₹99 Now</button>
            <p style="color: #666; margin-top: 15px;">Click to open secure payment window</p>
        </div>
        <script>
            var options = {{
                "key": "{key_id}",
                "amount": "{PAYMENT_AMOUNT}",
                "currency": "INR",
                "name": "Love Chat Analyzer",
                "description": "Unlock Your Love Story",
                "order_id": "{st.session_state.order_id}",
                "handler": function (response) {{
                    // Store payment ID in localStorage for verification
                    localStorage.setItem('razorpay_payment_id', response.razorpay_payment_id);
                    document.getElementById('razorpay-container').innerHTML = `
                        <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 25px; border-radius: 15px;">
                            <h3 style="color: #155724 !important;">💕 Payment Successful!</h3>
                            <p style="color: #155724 !important;">Click the button below to continue</p>
                            <p style="color: #666 !important; font-size: 12px; margin-top: 10px;">Payment ID: ${{response.razorpay_payment_id}}</p>
                        </div>
                    `;
                }},
                "theme": {{
                    "color": "#c44569"
                }},
                "modal": {{
                    "ondismiss": function() {{
                        document.getElementById('razorpay-container').innerHTML += `
                            <p style="color: #dc3545; margin-top: 10px;">Payment cancelled. Click the button to try again.</p>
                        `;
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
        components.html(checkout_html, height=200)

        st.markdown("---")
        st.markdown("**After completing payment, click below:**")

        # Simplified verification - just verify the order status
        if st.button("✅ I've Completed Payment - Continue", type="primary", use_container_width=True):
            # Try to verify the order's payment status via Razorpay API
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
                        st.balloons()
                        st.success("💕 Payment verified! Redirecting...")
                        st.rerun()
                    else:
                        st.warning("Payment not yet received. Please complete the payment first, then click this button.")
                else:
                    st.error("Could not verify payment. Please try again.")
            except Exception as e:
                st.error(f"Verification error. Please try again.")

    # Trust badges
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<p class="trust-badge">🔒 Secure Payment</p>', unsafe_allow_html=True)
    with col2:
        st.markdown('<p class="trust-badge">⚡ Instant Access</p>', unsafe_allow_html=True)
    with col3:
        st.markdown('<p class="trust-badge">💝 Made with Love</p>', unsafe_allow_html=True)

elif not PAYMENT_ENABLED or not razorpay_configured:
    pass  # Free access - go directly to uploader

# File uploader section
if st.session_state.payment_completed or not PAYMENT_ENABLED or not razorpay_configured:

    if st.session_state.payment_completed:
        st.markdown("""
        <div class="love-card">
            <h3 style="color: #155724 !important;">💕 Payment Successful!</h3>
            <p>Upload your chat below to discover your love story</p>
        </div>
        """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "💌 Upload your WhatsApp chat export (.txt)",
        type=['txt'],
        help="Export from WhatsApp: Settings > Chats > Export Chat > Without Media"
    )
else:
    uploaded_file = None

if uploaded_file is not None:
    content = uploaded_file.read().decode('utf-8')

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name

    try:
        with st.spinner("💕 Reading your love story..."):
            messages = parse_whatsapp_chat(temp_path)

        if len(messages) < 10:
            st.error("Could not parse enough messages. Please upload a valid WhatsApp chat export.")
            st.stop()

        participants = get_participants(messages)

        st.success(f"💕 Found **{len(messages):,}** messages of love!")

        st.markdown("### 👩‍❤️‍👨 Who's in this love story?")
        col1, col2 = st.columns(2)
        participant_mapping = {}

        for i, participant in enumerate(participants[:2]):
            with col1 if i == 0 else col2:
                display_name = st.text_input(
                    f"💕 Name for '{participant}'",
                    value=participant.split()[0] if ' ' in participant else participant,
                    key=f"name_{i}"
                )
                participant_mapping[participant] = display_name

        if st.button("💕 Generate Love Analysis", type="primary", use_container_width=True):
            progress = st.progress(0)
            status = st.empty()

            status.text("💕 Calculating your connection...")
            progress.progress(10)
            metrics = MetricsCalculator(messages, participant_mapping)

            status.text("🏷️ Understanding your conversations...")
            progress.progress(25)
            topics = TopicClassifier(messages)

            status.text("💖 Analyzing your bond...")
            progress.progress(40)
            sentiment = SentimentAnalyzer(messages, metrics, participant_mapping)

            status.text("🎭 Discovering your traits...")
            progress.progress(55)
            traits = TraitsAnalyzer(messages, metrics, participant_mapping)

            status.text("📞 Reviewing your calls...")
            progress.progress(70)
            calls = VideoCallAnalyzer(messages, participant_mapping)

            output_dir = tempfile.mkdtemp()

            status.text("🎨 Creating your love dashboard...")
            progress.progress(80)
            main_dashboard = DashboardGenerator(messages, metrics, sentiment, topics, participant_mapping)
            main_path = os.path.join(output_dir, 'dashboard.png')
            main_dashboard.create_dashboard(main_path)

            status.text("🎨 Crafting traits analysis...")
            progress.progress(90)
            traits_dashboard = TraitsDashboardGenerator(traits, participant_mapping)
            traits_path = os.path.join(output_dir, 'traits_dashboard.png')
            traits_dashboard.create_dashboard(traits_path)

            status.text("🎨 Building call insights...")
            progress.progress(95)
            call_dashboard = VideoCallDashboard(calls, participant_mapping)
            call_path = os.path.join(output_dir, 'videocall_dashboard.png')
            call_dashboard.create_dashboard(call_path)

            progress.progress(100)
            status.text("💕 Your love story is ready!")
            st.balloons()

            st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)

            # Quick stats with romantic styling
            st.markdown("### 💕 Your Love at a Glance")

            msg_counts = metrics.get_message_counts()
            call_summary = calls.get_call_summary()
            rating_label, rating_desc, rating_score = sentiment.calculate_relationship_rating()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("💬 Messages", f"{len(messages):,}")
            with col2:
                st.metric("💯 Love Score", f"{rating_score:.0f}/100")
            with col3:
                st.metric("📞 Calls", f"{call_summary['total_calls']:,}")
            with col4:
                st.metric("⏰ Hours Talking", f"{call_summary['total_call_time_hours']:.1f}")

            start, end = metrics.get_date_range()
            st.info(f"💕 Your journey: **{start.strftime('%b %d, %Y')}** to **{end.strftime('%b %d, %Y')}** ({metrics.get_total_days()} days of love)")

            st.markdown("### 💡 Key Insights About Your Love")
            insights = sentiment.generate_key_insights()
            for insight in insights:
                st.markdown(f"💕 {insight}")

            st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)

            st.markdown("### 📊 Your Love Dashboards")

            tab1, tab2, tab3 = st.tabs(["💕 Main Dashboard", "🎭 Traits Analysis", "📞 Call Statistics"])

            with tab1:
                st.image(main_path, use_container_width=True)
                with open(main_path, 'rb') as f:
                    st.download_button(
                        "💕 Download Main Dashboard",
                        f.read(),
                        file_name="love_dashboard.png",
                        mime="image/png",
                        use_container_width=True
                    )

            with tab2:
                st.image(traits_path, use_container_width=True)
                with open(traits_path, 'rb') as f:
                    st.download_button(
                        "💕 Download Traits Dashboard",
                        f.read(),
                        file_name="traits_dashboard.png",
                        mime="image/png",
                        use_container_width=True
                    )

            with tab3:
                st.image(call_path, use_container_width=True)
                with open(call_path, 'rb') as f:
                    st.download_button(
                        "💕 Download Call Dashboard",
                        f.read(),
                        file_name="call_dashboard.png",
                        mime="image/png",
                        use_container_width=True
                    )

            with st.expander("📋 Detailed Statistics"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**💬 Message Counts:**")
                    for sender, count in msg_counts.items():
                        name = participant_mapping.get(sender, sender)
                        st.markdown(f"• {name}: {count:,} messages")

                    st.markdown("**⏰ Response Times:**")
                    avg_response = metrics.get_average_response_time()
                    for sender, time in avg_response.items():
                        name = participant_mapping.get(sender, sender)
                        st.markdown(f"• {name}: {time:.1f} min average")

                with col2:
                    st.markdown("**📞 Call Statistics:**")
                    st.markdown(f"• Video calls: {call_summary['total_video_calls']:,}")
                    st.markdown(f"• Voice calls: {call_summary['total_voice_calls']:,}")
                    st.markdown(f"• Total time: {call_summary['total_call_time_hours']:.1f} hours")
                    st.markdown(f"• Longest call: {call_summary['longest_video_call_min']:.0f} min")

            os.unlink(temp_path)

    except Exception as e:
        st.error(f"Error analyzing chat: {str(e)}")
        st.exception(e)

elif not st.session_state.payment_completed and PAYMENT_ENABLED and razorpay_configured:
    pass  # Payment section is shown above

else:
    # Landing info for free mode
    st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)
    st.markdown("### 👆 Upload your chat to discover your love story!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
**💕 Relationship Dashboard**
- Overall love score
- Message balance
- Response patterns
- Monthly trends
        """)

    with col2:
        st.markdown("""
**🎭 Traits Analysis**
- Good qualities
- Growth areas
- Personality insights
- Communication style
        """)

    with col3:
        st.markdown("""
**📞 Call Analysis**
- Video vs voice
- Duration stats
- Who calls more
- Longest calls
        """)

# Footer
st.markdown("---")
st.markdown("""
<p class="footer-love">
    Made with 💕 for lovers everywhere<br>
    <a href="https://github.com/skepticalCA/whatsapp-chat-analyzer">GitHub</a>
</p>
""", unsafe_allow_html=True)
