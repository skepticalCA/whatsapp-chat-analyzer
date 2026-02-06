"""
Flashcard Generator Module
Creates 1080x1080 square shareable flashcard images with romantic styling.
Uses Pillow for pixel-perfect social media sized cards.
"""

import os
import math
import urllib.parse
from io import BytesIO
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont


WEBSITE_URL = "https://tinyurl.com/loveydoveyy"
BRAND_NAME = "Love Chat Analyzer"

# Romantic color palette (RGB tuples)
CARD_THEMES = [
    {  # Pink to purple gradient
        'top': (252, 231, 243),
        'bottom': (221, 214, 254),
        'accent': (219, 39, 119),
        'text': (92, 74, 82),
    },
    {  # Soft rose to peach
        'top': (255, 228, 236),
        'bottom': (255, 218, 200),
        'accent': (244, 63, 94),
        'text': (92, 74, 82),
    },
    {  # Lavender to sky
        'top': (237, 233, 254),
        'bottom': (224, 242, 254),
        'accent': (139, 92, 246),
        'text': (92, 74, 82),
    },
    {  # Blush to mint
        'top': (255, 241, 242),
        'bottom': (220, 252, 231),
        'accent': (236, 72, 153),
        'text': (92, 74, 82),
    },
    {  # Deep rose to warm
        'top': (254, 205, 211),
        'bottom': (254, 215, 170),
        'accent': (190, 18, 60),
        'text': (92, 74, 82),
    },
    {  # Cyan to lavender
        'top': (207, 250, 254),
        'bottom': (245, 208, 254),
        'accent': (6, 182, 212),
        'text': (92, 74, 82),
    },
]


class FlashcardGenerator:
    """Generate shareable 1080x1080 flashcard images."""

    def __init__(self, metrics, sentiment, calls, participant_mapping):
        self.metrics = metrics
        self.sentiment = sentiment
        self.calls = calls
        self.participant_mapping = participant_mapping
        self.names = list(participant_mapping.values())
        self._setup_fonts()

    def _setup_fonts(self):
        """Load fonts for flashcard rendering."""
        bold_candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        regular_candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]

        self.font_bold_path = None
        self.font_regular_path = None

        for path in bold_candidates:
            if os.path.exists(path):
                self.font_bold_path = path
                break

        for path in regular_candidates:
            if os.path.exists(path):
                self.font_regular_path = path
                break

        emoji_font_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'fonts', 'NotoEmoji-Regular.ttf'
        )
        self.emoji_font_path = emoji_font_path if os.path.exists(emoji_font_path) else None

    def _get_font(self, size, bold=False):
        """Get a PIL ImageFont at the given size."""
        path = self.font_bold_path if bold else self.font_regular_path
        if path:
            try:
                return ImageFont.truetype(path, size)
            except (IOError, OSError):
                pass
        return ImageFont.load_default().font_variant(size=size)

    def _get_emoji_font(self, size):
        """Get emoji font at given size."""
        if self.emoji_font_path:
            try:
                return ImageFont.truetype(self.emoji_font_path, size)
            except (IOError, OSError):
                pass
        return self._get_font(size)

    def _create_gradient_background(self, theme_idx=0):
        """Create a romantic gradient background image."""
        size = 1080
        theme = CARD_THEMES[theme_idx % len(CARD_THEMES)]
        img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        top = theme['top']
        bottom = theme['bottom']

        for y in range(size):
            ratio = y / size
            r = int(top[0] + (bottom[0] - top[0]) * ratio)
            g = int(top[1] + (bottom[1] - top[1]) * ratio)
            b = int(top[2] + (bottom[2] - top[2]) * ratio)
            draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

        return img

    def _draw_decorative_elements(self, draw, theme_idx=0):
        """Draw decorative circles and hearts on the card."""
        size = 1080
        theme = CARD_THEMES[theme_idx % len(CARD_THEMES)]
        accent = theme['accent']

        # Draw soft circles in corners (low opacity effect via blending)
        circle_color = accent + (30,)
        positions_sizes = [
            (-40, -40, 160), (size - 120, -40, 160),
            (-40, size - 120, 160), (size - 120, size - 120, 160),
            (size // 2 - 60, 40, 120),
        ]
        for x, y, s in positions_sizes:
            draw.ellipse([x, y, x + s, y + s], fill=circle_color)

        # Draw small hearts using the emoji font
        emoji_font = self._get_emoji_font(28)
        heart_positions = [
            (100, 90), (size - 140, 90),
            (60, size - 160), (size - 100, size - 160),
            (size // 2 + 200, 130), (size // 2 - 240, 130),
        ]
        heart_color = accent + (60,)
        for x, y in heart_positions:
            try:
                draw.text((x, y), "\u2665", fill=heart_color, font=emoji_font)
            except Exception:
                pass

    def _draw_branding(self, draw, theme_idx=0):
        """Draw branding at bottom of card."""
        size = 1080
        theme = CARD_THEMES[theme_idx % len(CARD_THEMES)]

        brand_font = self._get_font(30, bold=True)
        url_font = self._get_font(26)

        draw.text((size // 2, size - 110), BRAND_NAME,
                  fill=theme['accent'], font=brand_font, anchor="mm")
        draw.text((size // 2, size - 70), WEBSITE_URL,
                  fill=theme['text'], font=url_font, anchor="mm")

    def _wrap_text(self, text, font, max_width, draw):
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def _create_card(self, emoji_icon, stat_value, stat_label, subtitle="",
                     theme_idx=0):
        """Create a single 1080x1080 flashcard image."""
        size = 1080
        theme = CARD_THEMES[theme_idx % len(CARD_THEMES)]
        img = self._create_gradient_background(theme_idx)
        draw = ImageDraw.Draw(img, 'RGBA')

        self._draw_decorative_elements(draw, theme_idx)

        # Central white card area
        card_margin = 80
        card_top = 200
        card_bottom = size - 200
        card_rect = [card_margin, card_top, size - card_margin, card_bottom]
        draw.rounded_rectangle(card_rect, radius=30,
                               fill=(255, 255, 255, 200))

        # Top emoji icon
        emoji_font = self._get_emoji_font(72)
        try:
            draw.text((size // 2, card_top + 60), emoji_icon,
                      font=emoji_font, anchor="mm", fill=theme['accent'])
        except Exception:
            pass

        # Names line
        names_font = self._get_font(34, bold=True)
        if len(self.names) >= 2:
            names_text = f"{self.names[0]} & {self.names[1]}"
        else:
            names_text = "Your Love Story"
        draw.text((size // 2, card_top + 120), names_text,
                  fill=theme['accent'], font=names_font, anchor="mm")

        # Decorative line
        line_y = card_top + 155
        draw.line([(size // 2 - 100, line_y), (size // 2 + 100, line_y)],
                  fill=theme['accent'] + (100,), width=2)

        # Big stat value
        if stat_value:
            stat_font = self._get_font(110, bold=True)
            draw.text((size // 2, card_top + 270), str(stat_value),
                      fill=theme['accent'], font=stat_font, anchor="mm")

        # Stat label (with wrapping)
        label_font = self._get_font(38, bold=True)
        label_y = card_top + 370 if stat_value else card_top + 250
        label_lines = self._wrap_text(stat_label, label_font, size - 200, draw)
        for i, line in enumerate(label_lines):
            draw.text((size // 2, label_y + i * 50), line,
                      fill=theme['text'], font=label_font, anchor="mm")

        # Subtitle
        if subtitle:
            sub_font = self._get_font(28)
            sub_y = label_y + len(label_lines) * 50 + 30
            sub_lines = self._wrap_text(subtitle, sub_font, size - 200, draw)
            for i, line in enumerate(sub_lines):
                draw.text((size // 2, sub_y + i * 38), line,
                          fill=theme['text'] + (180,), font=sub_font,
                          anchor="mm")

        self._draw_branding(draw, theme_idx)

        return img.convert('RGB')

    def _create_insight_card(self, insight_text, theme_idx=4):
        """Create a special card for key insights with larger text."""
        size = 1080
        theme = CARD_THEMES[theme_idx % len(CARD_THEMES)]
        img = self._create_gradient_background(theme_idx)
        draw = ImageDraw.Draw(img, 'RGBA')

        self._draw_decorative_elements(draw, theme_idx)

        # Central white card
        card_margin = 80
        card_top = 200
        card_bottom = size - 200
        draw.rounded_rectangle(
            [card_margin, card_top, size - card_margin, card_bottom],
            radius=30, fill=(255, 255, 255, 200)
        )

        # Emoji icon
        emoji_font = self._get_emoji_font(72)
        try:
            draw.text((size // 2, card_top + 60), "\u2728",
                      font=emoji_font, anchor="mm", fill=theme['accent'])
        except Exception:
            pass

        # Names
        names_font = self._get_font(34, bold=True)
        if len(self.names) >= 2:
            names_text = f"{self.names[0]} & {self.names[1]}"
        else:
            names_text = "Your Love Story"
        draw.text((size // 2, card_top + 120), names_text,
                  fill=theme['accent'], font=names_font, anchor="mm")

        # Decorative line
        line_y = card_top + 155
        draw.line([(size // 2 - 100, line_y), (size // 2 + 100, line_y)],
                  fill=theme['accent'] + (100,), width=2)

        # Large quote marks
        quote_font = self._get_font(80, bold=True)
        draw.text((size // 2, card_top + 210), "\u201C",
                  fill=theme['accent'] + (80,), font=quote_font, anchor="mm")

        # Insight text - larger, centered, wrapped
        insight_font = self._get_font(36, bold=True)
        lines = self._wrap_text(insight_text, insight_font, size - 240, draw)
        start_y = card_top + 280
        for i, line in enumerate(lines):
            draw.text((size // 2, start_y + i * 52), line,
                      fill=theme['text'], font=insight_font, anchor="mm")

        # Subtitle
        sub_font = self._get_font(26)
        sub_y = start_y + len(lines) * 52 + 30
        draw.text((size // 2, sub_y), "A beautiful insight about your love",
                  fill=theme['text'] + (150,), font=sub_font, anchor="mm")

        self._draw_branding(draw, theme_idx)

        return img.convert('RGB')

    def generate_all_cards(self) -> List[Dict]:
        """Generate all flashcard images. Returns list of dicts with image, title, share_text."""
        cards = []
        name1 = self.names[0] if len(self.names) >= 1 else "Me"
        name2 = self.names[1] if len(self.names) >= 2 else "Babe"

        # Card 1: Total Messages - "proof of love" hook
        msg_counts = self.metrics.get_message_counts()
        total_msgs = sum(msg_counts.values())
        total_days = self.metrics.get_total_days()
        msgs_per_day = total_msgs / max(total_days, 1)

        cards.append({
            'image': self._create_card(
                emoji_icon="\u2764",
                stat_value=f"{total_msgs:,}",
                stat_label="reasons I know you love me",
                subtitle=f"That's {msgs_per_day:.0f} messages every single day",
                theme_idx=0,
            ),
            'title': 'Proof of Love',
            'share_text': (
                f"\u2764\ufe0f {total_msgs:,} messages. "
                f"That's {msgs_per_day:.0f} messages every single day "
                f"for {total_days} days straight.\n\n"
                f"If that's not love, what is? \U0001f495\n\n"
                f"Find out your number \U0001f449 {WEBSITE_URL}"
            ),
        })

        # Card 2: Love Score - competitive/flex hook
        rating_label, rating_desc, rating_score = (
            self.sentiment.calculate_relationship_rating()
        )

        cards.append({
            'image': self._create_card(
                emoji_icon="\U0001f496",
                stat_value=f"{rating_score:.0f}/100",
                stat_label="Love Compatibility Score",
                subtitle=f"Verdict: {rating_label}",
                theme_idx=1,
            ),
            'title': 'Love Score',
            'share_text': (
                f"\U0001f496 We just got our love score analyzed...\n\n"
                f"*{rating_score:.0f} out of 100* - {rating_label}!\n\n"
                f"Think you can beat us? \U0001f60f\n"
                f"Test your chat \U0001f449 {WEBSITE_URL}"
            ),
        })

        # Card 3: Call Hours - emotional intimacy hook
        call_summary = self.calls.get_call_summary()
        total_hours = call_summary['total_call_time_hours']
        total_calls = call_summary['total_calls']

        if total_calls > 0:
            total_days_calling = total_hours / 24
            cards.append({
                'image': self._create_card(
                    emoji_icon="\U0001f4de",
                    stat_value=f"{total_hours:.0f}h",
                    stat_label="spent hearing your voice",
                    subtitle=f"That's {total_days_calling:.1f} full days of just us",
                    theme_idx=2,
                ),
                'title': 'Hours Together',
                'share_text': (
                    f"\U0001f4de {total_hours:.0f} hours on calls.\n"
                    f"That's {total_days_calling:.1f} full days of "
                    f"just hearing each other's voice.\n\n"
                    f"Some people don't talk that much in a year \U0001f602\n\n"
                    f"Check your hours \U0001f449 {WEBSITE_URL}"
                ),
            })

        # Card 4: Double Text - playful teasing hook
        double_msgs = self.metrics.get_double_messages()
        if double_msgs:
            top_double = max(double_msgs.items(), key=lambda x: x[1])
            top_name = self.participant_mapping.get(top_double[0], top_double[0])
            double_count = top_double[1]
            other_name = name2 if top_name == name1 else name1

            cards.append({
                'image': self._create_card(
                    emoji_icon="\U0001f451",
                    stat_value=f"{double_count:,}",
                    stat_label=f"times {top_name} couldn't wait",
                    subtitle=f"The official 'can't stop thinking about {other_name}' award",
                    theme_idx=3,
                ),
                'title': "Can't Stop Texting",
                'share_text': (
                    f"\U0001f451 {top_name} double-texted {double_count:,} times.\n\n"
                    f"That's {double_count:,} times they just couldn't wait "
                    f"for {other_name} to reply \U0001f602\U0001f495\n\n"
                    f"Who's the clingy one in your relationship?\n"
                    f"Find out \U0001f449 {WEBSITE_URL}"
                ),
            })

        # Card 5: Key Insight - deep connection hook
        insights = self.sentiment.generate_key_insights()
        if insights:
            best_insight = insights[0]
            cards.append({
                'image': self._create_insight_card(best_insight, theme_idx=4),
                'title': 'What Your Chat Reveals',
                'share_text': (
                    f"\u2728 We analyzed our entire WhatsApp chat "
                    f"and this is what it revealed:\n\n"
                    f"\"{best_insight}\"\n\n"
                    f"What does your chat say about you?\n"
                    f"Try it \U0001f449 {WEBSITE_URL}"
                ),
            })

        # Card 6: Response Time - who cares more hook
        avg_response = self.metrics.get_average_response_time()
        if avg_response and len(avg_response) >= 2:
            sorted_resp = sorted(avg_response.items(), key=lambda x: x[1])
            fastest_name = self.participant_mapping.get(
                sorted_resp[0][0], sorted_resp[0][0]
            )
            fastest_time = sorted_resp[0][1]
            slowest_name = self.participant_mapping.get(
                sorted_resp[1][0], sorted_resp[1][0]
            )
            slowest_time = sorted_resp[1][1]

            cards.append({
                'image': self._create_card(
                    emoji_icon="\u26a1",
                    stat_value=f"{fastest_time:.0f} min",
                    stat_label=f"{fastest_name} can't wait to reply",
                    subtitle=f"Meanwhile {slowest_name} takes {slowest_time:.0f} min...",
                    theme_idx=5,
                ),
                'title': 'Who Replies Faster',
                'share_text': (
                    f"\u26a1 The data doesn't lie...\n\n"
                    f"{fastest_name} replies in {fastest_time:.0f} min\n"
                    f"{slowest_name} takes {slowest_time:.0f} min \U0001f440\n\n"
                    f"We know who's more whipped \U0001f602\U0001f495\n\n"
                    f"Expose your partner \U0001f449 {WEBSITE_URL}"
                ),
            })

        return cards

    @staticmethod
    def get_whatsapp_share_url(text: str) -> str:
        """Generate a WhatsApp share URL for the given text."""
        encoded_text = urllib.parse.quote(text)
        return f"https://api.whatsapp.com/send?text={encoded_text}"

    @staticmethod
    def image_to_bytes(image: Image.Image) -> bytes:
        """Convert PIL Image to PNG bytes."""
        buf = BytesIO()
        image.save(buf, format='PNG', quality=95)
        buf.seek(0)
        return buf.getvalue()
