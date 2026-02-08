"""
Razorpay Payment Handler for WhatsApp Chat Analyzer
Handles order creation and payment verification.
"""

import os
import hmac
import hashlib
import requests
from typing import Tuple, Optional

# Razorpay API endpoints
RAZORPAY_ORDER_URL = "https://api.razorpay.com/v1/orders"
RAZORPAY_PAYMENT_URL = "https://api.razorpay.com/v1/payments"

# Default amount in paise (₹79 = 7900 paise)
DEFAULT_AMOUNT = 7900
CURRENCY = "INR"


def get_razorpay_keys() -> Tuple[str, str]:
    """Get Razorpay API keys from Streamlit secrets or environment variables."""
    key_id = ""
    key_secret = ""

    # Try Streamlit secrets first (for Streamlit Cloud deployment)
    try:
        import streamlit as st
        key_id = st.secrets.get("RAZORPAY_KEY_ID", "")
        key_secret = st.secrets.get("RAZORPAY_KEY_SECRET", "")
    except Exception:
        pass

    # Fall back to environment variables
    if not key_id:
        key_id = os.environ.get("RAZORPAY_KEY_ID", "")
    if not key_secret:
        key_secret = os.environ.get("RAZORPAY_KEY_SECRET", "")

    return key_id, key_secret


def create_order(amount: int = DEFAULT_AMOUNT) -> Optional[dict]:
    """
    Create a Razorpay order.

    Args:
        amount: Amount in paise (default ₹79 = 7900 paise)

    Returns:
        Order details dict or None if failed
    """
    key_id, key_secret = get_razorpay_keys()

    if not key_id or not key_secret:
        return None

    try:
        response = requests.post(
            RAZORPAY_ORDER_URL,
            auth=(key_id, key_secret),
            json={
                "amount": amount,
                "currency": CURRENCY,
                "receipt": f"chat_analyzer_{os.urandom(8).hex()}",
                "notes": {
                    "product": "WhatsApp Chat Analyzer",
                    "description": "One-time analysis access"
                }
            }
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Razorpay order creation failed: {response.text}")
            return None

    except Exception as e:
        print(f"Error creating Razorpay order: {e}")
        return None


def verify_payment_signature(
    order_id: str,
    payment_id: str,
    signature: str
) -> bool:
    """
    Verify Razorpay payment signature.

    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID
        signature: Razorpay signature to verify

    Returns:
        True if signature is valid, False otherwise
    """
    _, key_secret = get_razorpay_keys()

    if not key_secret:
        return False

    try:
        # Create the signature verification string
        message = f"{order_id}|{payment_id}"

        # Generate expected signature
        expected_signature = hmac.new(
            key_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    except Exception as e:
        print(f"Error verifying payment signature: {e}")
        return False


def verify_payment_by_id(payment_id: str) -> bool:
    """
    Verify a payment directly via Razorpay API.

    Args:
        payment_id: Razorpay payment ID (starts with pay_)

    Returns:
        True if payment is captured/authorized, False otherwise
    """
    key_id, key_secret = get_razorpay_keys()

    if not key_id or not key_secret:
        return False

    try:
        response = requests.get(
            f"{RAZORPAY_PAYMENT_URL}/{payment_id}",
            auth=(key_id, key_secret)
        )

        if response.status_code == 200:
            payment = response.json()
            # Check if payment is captured or authorized
            status = payment.get("status", "")
            return status in ["captured", "authorized"]

        return False

    except Exception as e:
        print(f"Error verifying payment: {e}")
        return False


def get_checkout_html(order_id: str, key_id: str, amount: int = DEFAULT_AMOUNT) -> str:
    """
    Generate Razorpay checkout HTML/JS.

    Args:
        order_id: Razorpay order ID
        key_id: Razorpay key ID
        amount: Amount in paise

    Returns:
        HTML string with Razorpay checkout script
    """
    return f'''
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
        var options = {{
            "key": "{key_id}",
            "amount": "{amount}",
            "currency": "INR",
            "name": "WhatsApp Chat Analyzer",
            "description": "One-time Analysis Access",
            "order_id": "{order_id}",
            "handler": function (response) {{
                // Send payment details back to Streamlit
                window.parent.postMessage({{
                    type: 'razorpay_success',
                    payment_id: response.razorpay_payment_id,
                    order_id: response.razorpay_order_id,
                    signature: response.razorpay_signature
                }}, '*');
            }},
            "prefill": {{}},
            "theme": {{
                "color": "#667eea"
            }},
            "modal": {{
                "ondismiss": function() {{
                    window.parent.postMessage({{
                        type: 'razorpay_dismissed'
                    }}, '*');
                }}
            }}
        }};

        var rzp = new Razorpay(options);
        rzp.on('payment.failed', function (response) {{
            window.parent.postMessage({{
                type: 'razorpay_failed',
                error: response.error.description
            }}, '*');
        }});

        // Auto-open checkout
        rzp.open();
    </script>
    <div style="text-align: center; padding: 20px; color: #666;">
        <p>Razorpay checkout is opening...</p>
        <p>If it doesn't open, please refresh and try again.</p>
    </div>
    '''
