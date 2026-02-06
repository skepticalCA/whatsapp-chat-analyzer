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
    page_title="Love Chat Analyzer 💕",
    page_icon="💕",
    layout="wide"
)

# Romantic Custom CSS
st.markdown("""
<style>
    /* Main romantic theme */
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #ff6b9d 0%, #c44569 50%, #ff6b9d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s ease-in-out infinite;
    }

    @keyframes shimmer {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }

    .sub-header {
        text-align: center;
        color: #c44569;
        margin-bottom: 2rem;
        font-size: 1.2rem;
    }

    .love-card {
        background: linear-gradient(135deg, #fff5f7 0%, #ffe4ec 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid #ffb6c1;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 107, 157, 0.2);
    }

    .feature-card {
        background: linear-gradient(135deg, #fff0f3 0%, #ffe8ed 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #ff6b9d;
        margin: 0.5rem 0;
    }

    .price-tag {
        font-size: 3rem;
        font-weight: bold;
        color: #c44569;
        text-align: center;
    }

    .price-subtitle {
        color: #888;
        text-align: center;
        font-size: 0.9rem;
    }

    .heart-divider {
        text-align: center;
        font-size: 1.5rem;
        margin: 2rem 0;
        color: #ff6b9d;
    }

    .testimonial {
        background: #fff;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ffccd5;
        font-style: italic;
        color: #666;
    }

    .stat-highlight {
        background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: bold;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(255, 107, 157, 0.4);
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #fff5f7 0%, #ffe4ec 100%);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid #ffb6c1;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #fff5f7;
        border-radius: 10px;
    }

    /* Footer */
    .footer-love {
        text-align: center;
        color: #c44569;
        padding: 2rem;
        font-size: 0.9rem;
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
    - 🔥 **Activity Heatmaps**
    """)

# Main content
key_id, key_secret = get_razorpay_keys()
razorpay_configured = bool(key_id and key_secret)

# Payment flow with romantic landing page
if PAYMENT_ENABLED and razorpay_configured and not st.session_state.payment_completed:

    # Hero section
    st.markdown("""
    <div class="love-card">
        <h2 style="color: #c44569; margin-bottom: 0.5rem;">✨ Unlock Your Love Story ✨</h2>
        <p style="color: #666; font-size: 1.1rem;">Transform your WhatsApp chats into beautiful insights about your relationship</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)

    # Features in 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>💯 Relationship Score</h3>
            <p>Get a comprehensive score based on your communication patterns, response times, and emotional connection.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🎭 Personality Insights</h3>
            <p>Discover your communication styles, good traits, and areas where you can grow together.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📞 Call Analysis</h3>
            <p>See your video call patterns, longest calls, and how your connection has grown over time.</p>
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
        - Activity heatmaps
        """)

    with col2:
        st.markdown("""
        **💡 Personalized Insights:**
        - Relationship strengths
        - Growth opportunities
        - Communication style comparison
        - Key relationship milestones

        **📥 Downloadable:**
        - High-quality PNG dashboards
        - Share with your partner!
        """)

    st.markdown('<div class="heart-divider">💕 💕 💕</div>', unsafe_allow_html=True)

    # Pricing section
    st.markdown("""
    <div class="love-card">
        <p style="color: #888; margin-bottom: 0;">One-time payment</p>
        <div class="price-tag">₹99</div>
        <p class="price-subtitle">Less than a cup of coffee ☕</p>
        <p style="color: #666; margin-top: 1rem;">💳 UPI • Cards • Net Banking • Wallets</p>
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

    # Checkout flow
    if st.session_state.show_checkout and st.session_state.order_id:
        st.markdown("---")
        st.markdown("### 💳 Complete Your Payment")
        st.info("Click the button below to open secure payment window")

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
                    document.getElementById('razorpay-container').innerHTML = `
                        <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); padding: 25px; border-radius: 15px; color: #155724;">
                            <h3>💕 Payment Successful!</h3>
                            <p><strong>Payment ID:</strong> ${{response.razorpay_payment_id}}</p>
                            <p style="margin-top: 10px;">Copy the Payment ID and paste it below to unlock your analysis!</p>
                        </div>
                    `;
                }},
                "theme": {{
                    "color": "#c44569"
                }}
            }};
            var rzp = new Razorpay(options);
            document.getElementById('pay-btn').onclick = function(e) {{
                rzp.open();
                e.preventDefault();
            }};
        </script>
        '''
        components.html(checkout_html, height=180)

        st.markdown("---")
        st.markdown("**After payment, paste your Payment ID here:**")
        payment_id_input = st.text_input(
            "Payment ID",
            placeholder="pay_xxxxxxxxxxxxx",
            key="payment_verification",
            label_visibility="collapsed"
        )

        if st.button("✅ Verify & Unlock", type="primary"):
            if payment_id_input and payment_id_input.startswith("pay_"):
                if verify_payment_by_id(payment_id_input):
                    st.session_state.payment_completed = True
                    st.session_state.payment_id = payment_id_input
                    st.session_state.show_checkout = False
                    st.balloons()
                    st.success("💕 Payment verified! You can now upload your chat!")
                    st.rerun()
                else:
                    st.error("Could not verify payment. Please check the ID and try again.")
            else:
                st.warning("Please enter a valid Payment ID (starts with 'pay_')")

    # Trust badges
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🔒 **Secure Payment**")
    with col2:
        st.markdown("⚡ **Instant Access**")
    with col3:
        st.markdown("💝 **Made with Love**")

elif not PAYMENT_ENABLED or not razorpay_configured:
    pass  # Free access - go directly to uploader

# File uploader section
if st.session_state.payment_completed or not PAYMENT_ENABLED or not razorpay_configured:

    if st.session_state.payment_completed:
        st.markdown("""
        <div class="love-card">
            <h3 style="color: #155724;">💕 Payment Successful!</h3>
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
    <a href="https://github.com/skepticalCA/whatsapp-chat-analyzer" style="color: #c44569;">GitHub</a>
</p>
""", unsafe_allow_html=True)
