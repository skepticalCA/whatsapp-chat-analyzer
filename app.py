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
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .stDownloadButton {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">💬 WhatsApp Chat Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload your WhatsApp chat export and get comprehensive relationship insights</p>', unsafe_allow_html=True)

# Initialize session state for payment
if 'payment_completed' not in st.session_state:
    st.session_state.payment_completed = False
if 'payment_id' not in st.session_state:
    st.session_state.payment_id = None
if 'order_id' not in st.session_state:
    st.session_state.order_id = None
if 'show_checkout' not in st.session_state:
    st.session_state.show_checkout = False

# Sidebar instructions
with st.sidebar:
    st.header("📱 How to Export Your Chat")
    st.markdown("""
    **From WhatsApp:**
    1. Open the chat you want to analyze
    2. Tap ⋮ (menu) → **More** → **Export chat**
    3. Select **Without media**
    4. Save the `.txt` file

    **Privacy Note:**
    - Your chat is processed securely
    - We don't store any data
    - Analysis happens in real-time
    """)

    st.divider()
    st.header("📊 What You'll Get")
    st.markdown("""
    - **Relationship Rating** & Key Insights
    - **Message Statistics** & Balance
    - **Response Time** Analysis
    - **Topic Distribution**
    - **Communication Traits**
    - **Video Call** Statistics
    - **Activity Heatmaps**
    - **Relationship Timeline**
    """)

# Main content
# Check if Razorpay is configured
key_id, key_secret = get_razorpay_keys()
razorpay_configured = bool(key_id and key_secret)

# Payment flow
if PAYMENT_ENABLED and razorpay_configured and not st.session_state.payment_completed:
    st.markdown("### 💳 One-Time Payment")
    st.markdown("""
    Get comprehensive analysis of your WhatsApp chat including:
    - **Relationship Dashboard** with score and insights
    - **Traits Analysis** for both partners
    - **Video Call Statistics** and patterns

    **Price: ₹99** (one-time payment)
    """)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💳 Pay ₹99 to Unlock Analysis", type="primary", use_container_width=True):
            # Create Razorpay order
            order = create_order(PAYMENT_AMOUNT)
            if order:
                st.session_state.order_id = order['id']
                st.session_state.show_checkout = True
            else:
                st.error("Failed to create payment order. Please try again.")

    # Show Razorpay checkout if order created
    if st.session_state.show_checkout and st.session_state.order_id:
        st.markdown("---")
        st.info("🔐 Complete your payment in the popup window below")

        # Embed Razorpay checkout
        checkout_html = f'''
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        <div id="razorpay-container" style="text-align: center; padding: 20px;">
            <button id="pay-btn" style="
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 40px;
                font-size: 18px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            ">Click to Open Payment</button>
            <p style="margin-top: 15px; color: #666;">Click the button above to open the payment window</p>
        </div>
        <script>
            var options = {{
                "key": "{key_id}",
                "amount": "{PAYMENT_AMOUNT}",
                "currency": "INR",
                "name": "WhatsApp Chat Analyzer",
                "description": "One-time Analysis Access",
                "order_id": "{st.session_state.order_id}",
                "handler": function (response) {{
                    document.getElementById('razorpay-container').innerHTML = `
                        <div style="background: #d4edda; padding: 20px; border-radius: 10px; color: #155724;">
                            <h3>✅ Payment Successful!</h3>
                            <p><strong>Payment ID:</strong> ${{response.razorpay_payment_id}}</p>
                            <p>Please copy the Payment ID above and enter it below to verify.</p>
                        </div>
                    `;
                }},
                "theme": {{
                    "color": "#667eea"
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

        # Manual payment verification
        st.markdown("---")
        st.markdown("**After completing payment, enter your Payment ID below:**")
        payment_id_input = st.text_input(
            "Payment ID (starts with pay_)",
            placeholder="pay_xxxxxxxxxxxxx",
            key="payment_verification"
        )

        if st.button("✅ Verify Payment", type="primary"):
            if payment_id_input and payment_id_input.startswith("pay_"):
                # Verify payment via API
                if verify_payment_by_id(payment_id_input):
                    st.session_state.payment_completed = True
                    st.session_state.payment_id = payment_id_input
                    st.session_state.show_checkout = False
                    st.success("✅ Payment verified! You can now upload your chat.")
                    st.rerun()
                else:
                    st.error("❌ Could not verify payment. Please check the Payment ID and try again.")
            else:
                st.warning("Please enter a valid Payment ID (starts with 'pay_')")

    st.markdown("---")
    st.markdown("""
    <p style="text-align: center; color: #888; font-size: 12px;">
    🔒 Secure payment via Razorpay | 💳 All major cards & UPI accepted
    </p>
    """, unsafe_allow_html=True)

elif not PAYMENT_ENABLED or not razorpay_configured:
    # Payment disabled or not configured - show free access
    if PAYMENT_ENABLED and not razorpay_configured:
        st.info("💡 Payment gateway not configured. Enjoying free access!")

# Show file uploader only if payment completed or payment disabled
if st.session_state.payment_completed or not PAYMENT_ENABLED or not razorpay_configured:
    if st.session_state.payment_completed:
        st.success(f"✅ Payment verified! (ID: {st.session_state.payment_id})")

    uploaded_file = st.file_uploader(
        "Upload your WhatsApp chat export (.txt file)",
        type=['txt'],
        help="Export from WhatsApp: Settings > Chats > Export Chat > Without Media"
    )
else:
    uploaded_file = None

if uploaded_file is not None:
    # Read the file
    content = uploaded_file.read().decode('utf-8')

    # Save to temp file for parsing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name

    try:
        with st.spinner("🔍 Parsing your chat..."):
            messages = parse_whatsapp_chat(temp_path)

        if len(messages) < 10:
            st.error("❌ Could not parse enough messages. Please make sure you uploaded a valid WhatsApp chat export.")
            st.stop()

        # Get participants
        participants = get_participants(messages)

        st.success(f"✅ Successfully parsed **{len(messages):,}** messages!")

        # Participant name mapping
        st.subheader("👤 Set Display Names")
        st.markdown("Enter the display names for the participants in your chat:")

        col1, col2 = st.columns(2)
        participant_mapping = {}

        for i, participant in enumerate(participants[:2]):  # Max 2 participants
            with col1 if i == 0 else col2:
                display_name = st.text_input(
                    f"Name for '{participant}'",
                    value=participant.split()[0] if ' ' in participant else participant,
                    key=f"name_{i}"
                )
                participant_mapping[participant] = display_name

        # Analysis button
        if st.button("🚀 Generate Analysis", type="primary", use_container_width=True):

            # Progress bar
            progress = st.progress(0)
            status = st.empty()

            # Step 1: Calculate metrics
            status.text("📊 Calculating metrics...")
            progress.progress(10)
            metrics = MetricsCalculator(messages, participant_mapping)

            # Step 2: Classify topics
            status.text("🏷️ Classifying conversation topics...")
            progress.progress(25)
            topics = TopicClassifier(messages)

            # Step 3: Analyze sentiment
            status.text("💕 Analyzing relationship sentiment...")
            progress.progress(40)
            sentiment = SentimentAnalyzer(messages, metrics, participant_mapping)

            # Step 4: Analyze traits
            status.text("🎭 Analyzing communication traits...")
            progress.progress(55)
            traits = TraitsAnalyzer(messages, metrics, participant_mapping)

            # Step 5: Analyze calls
            status.text("📞 Analyzing video calls...")
            progress.progress(70)
            calls = VideoCallAnalyzer(messages, participant_mapping)

            # Create temp directory for outputs
            output_dir = tempfile.mkdtemp()

            # Step 6: Generate main dashboard
            status.text("🎨 Generating main dashboard...")
            progress.progress(80)
            main_dashboard = DashboardGenerator(messages, metrics, sentiment, topics, participant_mapping)
            main_path = os.path.join(output_dir, 'dashboard.png')
            main_dashboard.create_dashboard(main_path)

            # Step 7: Generate traits dashboard
            status.text("🎨 Generating traits dashboard...")
            progress.progress(90)
            traits_dashboard = TraitsDashboardGenerator(traits, participant_mapping)
            traits_path = os.path.join(output_dir, 'traits_dashboard.png')
            traits_dashboard.create_dashboard(traits_path)

            # Step 8: Generate call dashboard
            status.text("🎨 Generating video call dashboard...")
            progress.progress(95)
            call_dashboard = VideoCallDashboard(calls, participant_mapping)
            call_path = os.path.join(output_dir, 'videocall_dashboard.png')
            call_dashboard.create_dashboard(call_path)

            progress.progress(100)
            status.text("✅ Analysis complete!")

            # Display results
            st.divider()

            # Quick stats
            st.subheader("📈 Quick Stats")

            msg_counts = metrics.get_message_counts()
            call_summary = calls.get_call_summary()
            rating_label, rating_desc, rating_score = sentiment.calculate_relationship_rating()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Messages", f"{len(messages):,}")
            with col2:
                st.metric("Relationship Score", f"{rating_score:.0f}/100")
            with col3:
                st.metric("Total Calls", f"{call_summary['total_calls']:,}")
            with col4:
                st.metric("Call Hours", f"{call_summary['total_call_time_hours']:.1f}")

            # Date range
            start, end = metrics.get_date_range()
            st.info(f"📅 Chat period: **{start.strftime('%b %d, %Y')}** to **{end.strftime('%b %d, %Y')}** ({metrics.get_total_days()} days)")

            # Key insights
            st.subheader("💡 Key Insights")
            insights = sentiment.generate_key_insights()
            for insight in insights:
                st.markdown(f"• {insight}")

            st.divider()

            # Dashboard tabs
            st.subheader("📊 Your Dashboards")

            tab1, tab2, tab3 = st.tabs(["🏠 Main Dashboard", "🎭 Traits Analysis", "📞 Video Calls"])

            with tab1:
                st.image(main_path, use_container_width=True)
                with open(main_path, 'rb') as f:
                    st.download_button(
                        "⬇️ Download Main Dashboard",
                        f.read(),
                        file_name="whatsapp_dashboard.png",
                        mime="image/png",
                        use_container_width=True
                    )

            with tab2:
                st.image(traits_path, use_container_width=True)
                with open(traits_path, 'rb') as f:
                    st.download_button(
                        "⬇️ Download Traits Dashboard",
                        f.read(),
                        file_name="traits_dashboard.png",
                        mime="image/png",
                        use_container_width=True
                    )

            with tab3:
                st.image(call_path, use_container_width=True)
                with open(call_path, 'rb') as f:
                    st.download_button(
                        "⬇️ Download Video Call Dashboard",
                        f.read(),
                        file_name="videocall_dashboard.png",
                        mime="image/png",
                        use_container_width=True
                    )

            # Detailed stats expander
            with st.expander("📋 Detailed Statistics"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Message Counts:**")
                    for sender, count in msg_counts.items():
                        name = participant_mapping.get(sender, sender)
                        st.markdown(f"• {name}: {count:,} messages")

                    st.markdown("**Response Times:**")
                    avg_response = metrics.get_average_response_time()
                    for sender, time in avg_response.items():
                        name = participant_mapping.get(sender, sender)
                        st.markdown(f"• {name}: {time:.1f} min average")

                with col2:
                    st.markdown("**Call Statistics:**")
                    st.markdown(f"• Video calls: {call_summary['total_video_calls']:,}")
                    st.markdown(f"• Voice calls: {call_summary['total_voice_calls']:,}")
                    st.markdown(f"• Total time: {call_summary['total_call_time_hours']:.1f} hours")
                    st.markdown(f"• Longest call: {call_summary['longest_video_call_min']:.0f} min")

            # Cleanup temp files
            os.unlink(temp_path)

    except Exception as e:
        st.error(f"❌ Error analyzing chat: {str(e)}")
        st.exception(e)

else:
    # Show sample/demo section
    st.markdown("---")
    st.markdown("### 👆 Upload your chat file to get started!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **📊 Relationship Dashboard**
        - Overall relationship score
        - Message balance & patterns
        - Response time analysis
        - Monthly activity trends
        """)

    with col2:
        st.markdown("""
        **🎭 Traits Analysis**
        - Good communication traits
        - Areas for improvement
        - Personality insights
        - Communication style
        """)

    with col3:
        st.markdown("""
        **📞 Call Analysis**
        - Video vs voice calls
        - Call duration stats
        - Who calls more
        - Longest calls ever
        """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>Made with ❤️ | "
    "<a href='https://github.com/skepticalCA/whatsapp-chat-analyzer'>GitHub</a></p>",
    unsafe_allow_html=True
)
