"""
WhatsApp Chat Parser Module
Parses WhatsApp chat export files into structured Message objects.
"""

import re
from datetime import datetime
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple
import json


class MessageType(Enum):
    TEXT = auto()
    IMAGE = auto()
    VIDEO = auto()
    AUDIO = auto()
    STICKER = auto()
    GIF = auto()
    DOCUMENT = auto()
    VIDEO_CALL = auto()
    VOICE_CALL = auto()
    MISSED_VIDEO_CALL = auto()
    MISSED_VOICE_CALL = auto()
    DELETED = auto()
    SYSTEM = auto()
    LOCATION = auto()
    CONTACT = auto()


@dataclass
class Message:
    timestamp: datetime
    sender: str
    content: str
    message_type: MessageType
    raw_line: str
    call_duration_seconds: Optional[int] = None
    is_edited: bool = False


# Regex pattern for WhatsApp timestamp format: [DD/MM/YY, HH:MM:SS AM/PM]
# Note: WhatsApp uses narrow no-break space (U+202F) before AM/PM
TIMESTAMP_PATTERN = re.compile(
    r'^\[(\d{2}/\d{2}/\d{2}), (\d{1,2}:\d{2}:\d{2}[\s\u202f]*[AP]M)\] (.+?): (.*)$'
)

# System message patterns (no sender)
SYSTEM_PATTERN = re.compile(
    r'^\[(\d{2}/\d{2}/\d{2}), (\d{1,2}:\d{2}:\d{2}[\s\u202f]*[AP]M)\] (.+)$'
)

# Messages to skip entirely
SKIP_PATTERNS = [
    "Messages and calls are end-to-end encrypted",
    "security code changed",
    "created group",
    "added you",
    "left the group",
    "changed the group",
    "You're now an admin",
]


def classify_message_type(content: str) -> Tuple[MessageType, Optional[int], bool]:
    """
    Classify message type based on content patterns.
    Returns (MessageType, call_duration_seconds, is_edited)
    """
    content_lower = content.lower().strip()
    content_clean = content.replace('\u200e', '').strip()

    # Check for edited message
    is_edited = '<This message was edited>' in content or '‎<This message was edited>' in content
    content_check = content_clean.replace('<This message was edited>', '').strip()

    # Media patterns
    if 'image omitted' in content_lower:
        return MessageType.IMAGE, None, is_edited
    if 'video omitted' in content_lower:
        return MessageType.VIDEO, None, is_edited
    if 'audio omitted' in content_lower:
        return MessageType.AUDIO, None, is_edited
    if 'sticker omitted' in content_lower:
        return MessageType.STICKER, None, is_edited
    if 'gif omitted' in content_lower:
        return MessageType.GIF, None, is_edited
    if 'document omitted' in content_lower:
        return MessageType.DOCUMENT, None, is_edited
    if 'location:' in content_lower or 'live location shared' in content_lower:
        return MessageType.LOCATION, None, is_edited
    if 'contact card omitted' in content_lower:
        return MessageType.CONTACT, None, is_edited

    # Call patterns
    if 'video call' in content_lower:
        duration = parse_call_duration(content)
        if 'missed' in content_lower or 'no answer' in content_lower:
            return MessageType.MISSED_VIDEO_CALL, None, is_edited
        return MessageType.VIDEO_CALL, duration, is_edited

    if 'voice call' in content_lower or ('call' in content_lower and 'video' not in content_lower):
        duration = parse_call_duration(content)
        if 'missed' in content_lower or 'no answer' in content_lower:
            return MessageType.MISSED_VOICE_CALL, None, is_edited
        return MessageType.VOICE_CALL, duration, is_edited

    # Deleted message
    if 'this message was deleted' in content_lower or 'you deleted this message' in content_lower:
        return MessageType.DELETED, None, is_edited

    return MessageType.TEXT, None, is_edited


def parse_call_duration(content: str) -> Optional[int]:
    """
    Extract call duration in seconds from call message.
    Returns None for missed/no answer calls.
    """
    if 'no answer' in content.lower() or 'missed' in content.lower():
        return None

    # Pattern for duration: X hr Y min Z sec, or combinations
    total_seconds = 0

    hr_match = re.search(r'(\d+)\s*hr', content, re.IGNORECASE)
    min_match = re.search(r'(\d+)\s*min', content, re.IGNORECASE)
    sec_match = re.search(r'(\d+)\s*sec', content, re.IGNORECASE)

    if hr_match:
        total_seconds += int(hr_match.group(1)) * 3600
    if min_match:
        total_seconds += int(min_match.group(1)) * 60
    if sec_match:
        total_seconds += int(sec_match.group(1))

    return total_seconds if total_seconds > 0 else None


def should_skip_message(content: str) -> bool:
    """Check if message should be skipped (system notifications)."""
    for pattern in SKIP_PATTERNS:
        if pattern.lower() in content.lower():
            return True
    return False


def parse_timestamp(date_str: str, time_str: str) -> datetime:
    """Parse WhatsApp timestamp into datetime object."""
    # Format: DD/MM/YY, H:MM:SS AM/PM
    # Replace narrow no-break space (U+202F) with regular space
    time_str = time_str.replace('\u202f', ' ').replace('\xa0', ' ')
    combined = f"{date_str} {time_str}"
    return datetime.strptime(combined, "%d/%m/%y %I:%M:%S %p")


def parse_whatsapp_chat(file_path: str) -> List[Message]:
    """
    Parse WhatsApp chat export file into structured Message objects.
    Handles multi-line messages by detecting timestamp pattern.
    """
    messages = []
    current_message = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Remove BOM and strip
            line = line.lstrip('\ufeff').rstrip('\n\r')

            if not line.strip():
                continue

            # Try to match timestamp pattern
            match = TIMESTAMP_PATTERN.match(line)

            if match:
                # Save previous message if exists
                if current_message is not None:
                    messages.append(current_message)

                date_str, time_str, sender, content = match.groups()

                # Clean up content
                content = content.replace('\u200e', '').strip()
                sender = sender.strip()

                # Skip system messages
                if should_skip_message(content):
                    current_message = None
                    continue

                # Parse timestamp
                try:
                    timestamp = parse_timestamp(date_str, time_str)
                except ValueError:
                    current_message = None
                    continue

                # Classify message type
                msg_type, call_duration, is_edited = classify_message_type(content)

                # Clean edited tag from content
                content = content.replace('<This message was edited>', '').replace('‎<This message was edited>', '').strip()

                current_message = Message(
                    timestamp=timestamp,
                    sender=sender,
                    content=content,
                    message_type=msg_type,
                    raw_line=line,
                    call_duration_seconds=call_duration,
                    is_edited=is_edited
                )
            else:
                # Check if it's a system message without sender
                sys_match = SYSTEM_PATTERN.match(line)
                if sys_match and current_message is None:
                    # System message, skip
                    continue

                # This is a continuation of the previous message
                if current_message is not None:
                    current_message.content += '\n' + line.strip()
                    current_message.raw_line += '\n' + line

    # Don't forget the last message
    if current_message is not None:
        messages.append(current_message)

    return messages


def get_participants(messages: List[Message]) -> List[str]:
    """Extract unique participant names from messages."""
    participants = set()
    for msg in messages:
        participants.add(msg.sender)
    return sorted(list(participants))


def messages_to_dict(messages: List[Message]) -> List[dict]:
    """Convert messages to dictionary format for JSON serialization."""
    return [
        {
            'timestamp': msg.timestamp.isoformat(),
            'sender': msg.sender,
            'content': msg.content,
            'message_type': msg.message_type.name,
            'call_duration_seconds': msg.call_duration_seconds,
            'is_edited': msg.is_edited
        }
        for msg in messages
    ]


def save_parsed_messages(messages: List[Message], output_path: str):
    """Save parsed messages to JSON file."""
    data = messages_to_dict(messages)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    # Test parsing
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = '/Users/arvind/PythonProjects/Chatanaylsi/_chat.txt'

    print(f"Parsing {file_path}...")
    messages = parse_whatsapp_chat(file_path)

    print(f"\nTotal messages parsed: {len(messages)}")
    print(f"Participants: {get_participants(messages)}")

    # Count by type
    type_counts = {}
    for msg in messages:
        type_name = msg.message_type.name
        type_counts[type_name] = type_counts.get(type_name, 0) + 1

    print("\nMessage types:")
    for msg_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {msg_type}: {count}")

    # Date range
    if messages:
        print(f"\nDate range: {messages[0].timestamp.date()} to {messages[-1].timestamp.date()}")

    # Save to JSON
    output_path = '/Users/arvind/PythonProjects/Chatanaylsi/.tmp/parsed_messages.json'
    save_parsed_messages(messages, output_path)
    print(f"\nSaved to {output_path}")
