"""
Traits Analyzer Module
Analyzes communication patterns to identify good and bad traits for each person.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import numpy as np
from chat_parser import Message, MessageType
from metrics_calculator import MetricsCalculator


class TraitsAnalyzer:
    """Analyze communication patterns to identify personality traits."""

    def __init__(self, messages: List[Message], metrics: MetricsCalculator,
                 participant_mapping: Dict[str, str]):
        self.messages = messages
        self.metrics = metrics
        self.participant_mapping = participant_mapping
        self.participants = list(participant_mapping.keys())
        self.text_messages = [m for m in messages if m.message_type == MessageType.TEXT]

    def get_display_name(self, raw_name: str) -> str:
        return self.participant_mapping.get(raw_name, raw_name)

    # ============== GOOD TRAITS ANALYSIS ==============

    def analyze_supportiveness(self) -> Dict[str, Dict]:
        """Analyze how supportive each person is during tough times."""
        support_words = [
            'don\'t worry', 'it\'s okay', 'its okay', 'i\'m here', 'im here',
            'you can do it', 'i believe', 'proud of you', 'you got this',
            'i understand', 'take care', 'feel better', 'here for you',
            'everything will be', 'it will be okay', 'cheer up', 'stay strong',
            'you\'re amazing', 'you are amazing', 'you\'re the best', 'dont worry',
            'koi baat nhi', 'koi baat nahi', 'tension mat le', 'sab theek',
            'sab thik', 'main hun', 'mei hun', 'relax', 'chill'
        ]

        support_counts = defaultdict(int)
        examples = defaultdict(list)

        for msg in self.text_messages:
            content_lower = msg.content.lower()
            for phrase in support_words:
                if phrase in content_lower:
                    support_counts[msg.sender] += 1
                    if len(examples[msg.sender]) < 3:
                        examples[msg.sender].append(msg.content[:80])
                    break

        # Normalize by message count
        msg_counts = self.metrics.get_message_counts()
        scores = {}
        for sender in self.participants:
            count = support_counts.get(sender, 0)
            total = msg_counts.get(sender, 1)
            scores[sender] = {
                'count': count,
                'rate': (count / total) * 100,
                'examples': examples.get(sender, [])
            }

        return scores

    def analyze_affection_expression(self) -> Dict[str, Dict]:
        """Analyze how each person expresses affection."""
        affection_patterns = {
            'love_declarations': [r'\bi\s*love\s*(you|u)\b', r'\blive\s*you\b', r'\bpyaar\b'],
            'miss_you': [r'\bi?\s*miss\s*(you|u)\b', r'\bmissing\s*(you|u)\b', r'\byaad\b'],
            'pet_names': [r'\bbaby\b', r'\bbabe\b', r'\bcutie\b', r'\bcutu\b', r'\bjaan\b',
                         r'\bjaanu\b', r'\bhoney\b', r'\bsweetheart\b', r'\bprincess\b',
                         r'\bbb\b', r'\bbub\b', r'\bbubba\b'],
            'compliments': [r'\bbeautiful\b', r'\bgorgeous\b', r'\bhandsome\b', r'\bcute\b',
                           r'\bamazing\b', r'\bperfect\b', r'\bspecial\b', r'\bbest\b'],
            'care_expressions': [r'\btake care\b', r'\bstay safe\b', r'\beat\s*(properly|well)\b',
                                r'\bsleep well\b', r'\bdid you eat\b', r'\bkhana kha\b']
        }

        scores = {sender: {cat: 0 for cat in affection_patterns} for sender in self.participants}

        for msg in self.text_messages:
            content_lower = msg.content.lower()
            for category, patterns in affection_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content_lower):
                        scores[msg.sender][category] += 1
                        break

        # Calculate totals and rates
        msg_counts = self.metrics.get_message_counts()
        result = {}
        for sender in self.participants:
            total_affection = sum(scores[sender].values())
            result[sender] = {
                'breakdown': scores[sender],
                'total': total_affection,
                'rate': (total_affection / msg_counts.get(sender, 1)) * 100
            }

        return result

    def analyze_effort_and_initiative(self) -> Dict[str, Dict]:
        """Analyze effort put into the relationship."""
        # Plan-making words
        plan_words = ['let\'s meet', 'lets meet', 'shall we', 'want to go',
                     'wanna go', 'plan', 'date', 'surprise', 'gift', 'milte hai',
                     'chalte hai', 'chalo', 'movie dekhte', 'dinner', 'lunch']

        # Question asking (shows interest)
        question_count = defaultdict(int)
        plan_count = defaultdict(int)
        long_messages = defaultdict(int)  # Messages > 50 chars show effort

        for msg in self.text_messages:
            content = msg.content
            content_lower = content.lower()

            # Count questions
            question_count[msg.sender] += content.count('?')

            # Count planning
            for word in plan_words:
                if word in content_lower:
                    plan_count[msg.sender] += 1
                    break

            # Count long thoughtful messages
            if len(content) > 50:
                long_messages[msg.sender] += 1

        # Conversation initiations
        initiations = self.metrics.get_conversation_initiations()

        msg_counts = self.metrics.get_message_counts()
        result = {}
        for sender in self.participants:
            total_msgs = msg_counts.get(sender, 1)
            result[sender] = {
                'questions_asked': question_count.get(sender, 0),
                'questions_rate': (question_count.get(sender, 0) / total_msgs) * 100,
                'plans_made': plan_count.get(sender, 0),
                'long_messages': long_messages.get(sender, 0),
                'long_message_rate': (long_messages.get(sender, 0) / total_msgs) * 100,
                'conversation_starts': initiations.get(sender, 0)
            }

        return result

    def analyze_responsiveness(self) -> Dict[str, Dict]:
        """Analyze how responsive and attentive each person is."""
        response_times = self.metrics.get_response_times()
        immediate = self.metrics.get_immediate_replies_percentage()

        # Analyze late night responses (shows dedication)
        late_night_responses = defaultdict(int)
        early_morning_responses = defaultdict(int)

        for i in range(1, len(self.messages)):
            msg = self.messages[i]
            prev = self.messages[i-1]
            if msg.sender != prev.sender:
                hour = msg.timestamp.hour
                if 0 <= hour < 6:
                    late_night_responses[msg.sender] += 1
                elif 6 <= hour < 8:
                    early_morning_responses[msg.sender] += 1

        result = {}
        for sender in self.participants:
            times = response_times.get(sender, [])
            result[sender] = {
                'avg_response_min': np.mean(times) if times else 0,
                'median_response_min': np.median(times) if times else 0,
                'immediate_reply_pct': immediate.get(sender, 0),
                'late_night_responses': late_night_responses.get(sender, 0),
                'early_morning_responses': early_morning_responses.get(sender, 0)
            }

        return result

    def analyze_humor(self) -> Dict[str, Dict]:
        """Analyze sense of humor and playfulness."""
        humor_indicators = [
            r'\bhaha+\b', r'\blol+\b', r'\blmao+\b', r'\brofl\b', r'\bxd+\b',
            r'😂', r'🤣', r'😆', r'😹', r'💀', r'☠️'
        ]

        teasing_words = ['pagal', 'stupid', 'idiot', 'dumbo', 'silly', 'weirdo',
                        'drama', 'nautanki', 'paagal', 'bewakoof']

        humor_count = defaultdict(int)
        teasing_count = defaultdict(int)

        for msg in self.text_messages:
            content_lower = msg.content.lower()

            for pattern in humor_indicators:
                if re.search(pattern, content_lower):
                    humor_count[msg.sender] += 1
                    break

            for word in teasing_words:
                if word in content_lower:
                    teasing_count[msg.sender] += 1
                    break

        msg_counts = self.metrics.get_message_counts()
        result = {}
        for sender in self.participants:
            total = msg_counts.get(sender, 1)
            result[sender] = {
                'humor_expressions': humor_count.get(sender, 0),
                'humor_rate': (humor_count.get(sender, 0) / total) * 100,
                'playful_teasing': teasing_count.get(sender, 0)
            }

        return result

    # ============== BAD TRAITS ANALYSIS ==============

    def analyze_ghosting_patterns(self) -> Dict[str, Dict]:
        """Analyze ghosting and long silence patterns."""
        # Find gaps where one person left the other hanging
        ghosting_instances = defaultdict(list)  # Times someone didn't reply for 6+ hours during active hours
        ignored_messages = defaultdict(int)  # Double/triple texts that got no response

        for i in range(1, len(self.messages)):
            msg = self.messages[i]
            prev = self.messages[i-1]

            if msg.sender != prev.sender:
                gap_hours = (msg.timestamp - prev.timestamp).total_seconds() / 3600

                # Check if it's a significant gap during reasonable hours
                prev_hour = prev.timestamp.hour
                if gap_hours >= 6 and 8 <= prev_hour <= 23:  # Daytime message left hanging
                    ghosting_instances[msg.sender].append({
                        'date': prev.timestamp,
                        'gap_hours': gap_hours
                    })

        # Count ignored streak messages
        streak_sender = None
        streak_count = 0
        streak_start_time = None

        for i, msg in enumerate(self.messages):
            if msg.sender == streak_sender:
                streak_count += 1
            else:
                # End of streak - check if the responder took long
                if streak_count >= 3 and streak_start_time and i > 0:
                    gap = (msg.timestamp - self.messages[i-1].timestamp).total_seconds() / 3600
                    if gap > 3:  # More than 3 hours to respond to multiple messages
                        ignored_messages[msg.sender] += 1

                streak_sender = msg.sender
                streak_count = 1
                streak_start_time = msg.timestamp

        result = {}
        for sender in self.participants:
            ghost_list = ghosting_instances.get(sender, [])
            result[sender] = {
                'long_response_gaps': len(ghost_list),
                'avg_gap_hours': np.mean([g['gap_hours'] for g in ghost_list]) if ghost_list else 0,
                'times_ignored_multiple_msgs': ignored_messages.get(sender, 0)
            }

        return result

    def analyze_negativity(self) -> Dict[str, Dict]:
        """Analyze negative communication patterns."""
        negative_words = [
            'hate', 'angry', 'annoyed', 'irritated', 'frustrated', 'upset',
            'mad at', 'pissed', 'whatever', 'fine', 'leave me', 'go away',
            'don\'t talk', 'shut up', 'i don\'t care', 'idc', 'gussa',
            'chup', 'bekaar', 'boring', 'katti'
        ]

        passive_aggressive = [
            'k', 'ok.', 'fine.', 'whatever.', 'sure.', 'if you say so',
            'do what you want', 'i guess', 'nevermind', 'forget it',
            'nothing', 'nm', 'nth'
        ]

        negative_count = defaultdict(int)
        passive_count = defaultdict(int)
        negative_examples = defaultdict(list)

        for msg in self.text_messages:
            content_lower = msg.content.lower().strip()

            for word in negative_words:
                if word in content_lower:
                    negative_count[msg.sender] += 1
                    if len(negative_examples[msg.sender]) < 3:
                        negative_examples[msg.sender].append(msg.content[:60])
                    break

            # Check for passive aggressive short responses
            if content_lower in passive_aggressive or (len(content_lower) <= 2 and content_lower in ['k', 'ok', 'hm', 'mm']):
                passive_count[msg.sender] += 1

        msg_counts = self.metrics.get_message_counts()
        result = {}
        for sender in self.participants:
            total = msg_counts.get(sender, 1)
            result[sender] = {
                'negative_expressions': negative_count.get(sender, 0),
                'negativity_rate': (negative_count.get(sender, 0) / total) * 100,
                'passive_aggressive_responses': passive_count.get(sender, 0),
                'passive_rate': (passive_count.get(sender, 0) / total) * 100
            }

        return result

    def analyze_self_centeredness(self) -> Dict[str, Dict]:
        """Analyze if conversations are balanced or one-sided."""
        # Count "I" vs "you" usage
        i_count = defaultdict(int)
        you_count = defaultdict(int)

        # Count questions asked vs statements made
        questions = defaultdict(int)
        statements = defaultdict(int)

        for msg in self.text_messages:
            content_lower = msg.content.lower()
            words = content_lower.split()

            # Count I/me references
            i_refs = sum(1 for w in words if w in ['i', 'i\'m', 'im', 'me', 'my', 'mine', 'myself', 'mai', 'mera', 'meri', 'mujhe'])
            you_refs = sum(1 for w in words if w in ['you', 'you\'re', 'your', 'yours', 'yourself', 'tu', 'tum', 'tera', 'teri', 'tumhara', 'aap', 'apka'])

            i_count[msg.sender] += i_refs
            you_count[msg.sender] += you_refs

            if '?' in msg.content:
                questions[msg.sender] += 1
            else:
                statements[msg.sender] += 1

        result = {}
        for sender in self.participants:
            i_total = i_count.get(sender, 0)
            you_total = you_count.get(sender, 0)
            q_total = questions.get(sender, 0)
            s_total = statements.get(sender, 1)

            result[sender] = {
                'i_references': i_total,
                'you_references': you_total,
                'i_to_you_ratio': i_total / max(you_total, 1),
                'questions_asked': q_total,
                'question_ratio': (q_total / (q_total + s_total)) * 100
            }

        return result

    def analyze_emotional_availability(self) -> Dict[str, Dict]:
        """Analyze emotional availability and presence."""
        # Analyze response to emotional messages
        emotional_triggers = ['sad', 'upset', 'crying', 'cry', 'hurt', 'stressed',
                             'anxious', 'worried', 'scared', 'lonely', 'miss',
                             'bad day', 'rough day', 'tough', 'struggling']

        emotional_support_given = defaultdict(int)
        emotional_dismissals = defaultdict(int)

        dismissive_responses = ['ok', 'k', 'hmm', 'hm', 'oh', 'acha', 'achha', 'thik', 'theek']

        for i in range(1, len(self.text_messages)):
            prev_msg = self.text_messages[i-1]
            curr_msg = self.text_messages[i]

            if prev_msg.sender == curr_msg.sender:
                continue

            prev_lower = prev_msg.content.lower()

            # Check if previous message was emotional
            is_emotional = any(trigger in prev_lower for trigger in emotional_triggers)

            if is_emotional:
                curr_lower = curr_msg.content.lower().strip()
                # Check if response was supportive or dismissive
                if len(curr_lower) <= 5 and curr_lower in dismissive_responses:
                    emotional_dismissals[curr_msg.sender] += 1
                elif len(curr_msg.content) > 20:  # Longer response = more effort
                    emotional_support_given[curr_msg.sender] += 1

        result = {}
        for sender in self.participants:
            support = emotional_support_given.get(sender, 0)
            dismiss = emotional_dismissals.get(sender, 0)
            total = support + dismiss

            result[sender] = {
                'supportive_responses': support,
                'dismissive_responses': dismiss,
                'emotional_support_rate': (support / max(total, 1)) * 100
            }

        return result

    def analyze_consistency(self) -> Dict[str, Dict]:
        """Analyze consistency in communication patterns."""
        # Analyze message volume by month to see consistency
        monthly_counts = defaultdict(lambda: defaultdict(int))

        for msg in self.messages:
            month_key = msg.timestamp.strftime('%Y-%m')
            monthly_counts[month_key][msg.sender] += 1

        # Calculate standard deviation of monthly messages
        result = {}
        for sender in self.participants:
            monthly_values = [monthly_counts[m].get(sender, 0) for m in monthly_counts.keys()]
            if monthly_values:
                result[sender] = {
                    'avg_monthly_messages': np.mean(monthly_values),
                    'std_dev': np.std(monthly_values),
                    'consistency_score': 100 - min(100, (np.std(monthly_values) / max(np.mean(monthly_values), 1)) * 100),
                    'min_month': min(monthly_values),
                    'max_month': max(monthly_values)
                }
            else:
                result[sender] = {
                    'avg_monthly_messages': 0,
                    'std_dev': 0,
                    'consistency_score': 0,
                    'min_month': 0,
                    'max_month': 0
                }

        return result

    # ============== SUMMARY METHODS ==============

    def get_good_traits(self) -> Dict[str, List[Dict]]:
        """Get top good traits for each person."""
        supportiveness = self.analyze_supportiveness()
        affection = self.analyze_affection_expression()
        effort = self.analyze_effort_and_initiative()
        responsiveness = self.analyze_responsiveness()
        humor = self.analyze_humor()

        good_traits = {sender: [] for sender in self.participants}

        for sender in self.participants:
            name = self.get_display_name(sender)
            traits = []

            # Supportiveness
            if supportiveness[sender]['rate'] > 0.5:
                traits.append({
                    'trait': 'Supportive Partner',
                    'description': f"Uses supportive language {supportiveness[sender]['count']} times",
                    'score': min(100, supportiveness[sender]['rate'] * 50),
                    'icon': '🤗'
                })

            # Affection
            if affection[sender]['rate'] > 5:
                traits.append({
                    'trait': 'Expressive with Love',
                    'description': f"Expresses affection frequently ({affection[sender]['total']} times)",
                    'score': min(100, affection[sender]['rate'] * 5),
                    'icon': '❤️'
                })

            # Effort
            if effort[sender]['questions_rate'] > 5:
                traits.append({
                    'trait': 'Shows Genuine Interest',
                    'description': f"Asks lots of questions ({effort[sender]['questions_asked']})",
                    'score': min(100, effort[sender]['questions_rate'] * 5),
                    'icon': '🤔'
                })

            if effort[sender]['long_message_rate'] > 10:
                traits.append({
                    'trait': 'Puts Effort in Communication',
                    'description': f"Sends thoughtful long messages ({effort[sender]['long_messages']})",
                    'score': min(100, effort[sender]['long_message_rate'] * 3),
                    'icon': '✍️'
                })

            if effort[sender]['plans_made'] > 50:
                traits.append({
                    'trait': 'Takes Initiative',
                    'description': f"Often plans activities ({effort[sender]['plans_made']} times)",
                    'score': min(100, effort[sender]['plans_made'] / 5),
                    'icon': '📅'
                })

            # Responsiveness
            if responsiveness[sender]['immediate_reply_pct'] > 40:
                traits.append({
                    'trait': 'Quick to Respond',
                    'description': f"{responsiveness[sender]['immediate_reply_pct']:.0f}% immediate replies",
                    'score': responsiveness[sender]['immediate_reply_pct'],
                    'icon': '⚡'
                })

            if responsiveness[sender]['late_night_responses'] > 100:
                traits.append({
                    'trait': 'Always Available',
                    'description': f"Even responds late at night ({responsiveness[sender]['late_night_responses']} times)",
                    'score': min(100, responsiveness[sender]['late_night_responses'] / 10),
                    'icon': '🌙'
                })

            # Humor
            if humor[sender]['humor_rate'] > 5:
                traits.append({
                    'trait': 'Great Sense of Humor',
                    'description': f"Keeps things fun ({humor[sender]['humor_expressions']} laughs)",
                    'score': min(100, humor[sender]['humor_rate'] * 5),
                    'icon': '😄'
                })

            if humor[sender]['playful_teasing'] > 50:
                traits.append({
                    'trait': 'Playful & Fun',
                    'description': f"Enjoys playful teasing ({humor[sender]['playful_teasing']} times)",
                    'score': min(100, humor[sender]['playful_teasing'] / 2),
                    'icon': '😜'
                })

            # Sort by score and take top 5
            traits.sort(key=lambda x: -x['score'])
            good_traits[sender] = traits[:5]

        return good_traits

    def get_bad_traits(self) -> Dict[str, List[Dict]]:
        """Get areas for improvement for each person."""
        ghosting = self.analyze_ghosting_patterns()
        negativity = self.analyze_negativity()
        self_centered = self.analyze_self_centeredness()
        emotional = self.analyze_emotional_availability()
        consistency = self.analyze_consistency()
        effort = self.analyze_effort_and_initiative()

        bad_traits = {sender: [] for sender in self.participants}

        for sender in self.participants:
            name = self.get_display_name(sender)
            traits = []

            # Ghosting
            if ghosting[sender]['long_response_gaps'] > 50:
                traits.append({
                    'trait': 'Sometimes Slow to Respond',
                    'description': f"Had {ghosting[sender]['long_response_gaps']} long response delays",
                    'severity': min(100, ghosting[sender]['long_response_gaps'] / 5),
                    'suggestion': 'Try to respond more promptly, even if just to acknowledge',
                    'icon': '⏰'
                })

            # Passive aggressive
            if negativity[sender]['passive_rate'] > 2:
                traits.append({
                    'trait': 'Can Be Short in Responses',
                    'description': f"Uses brief responses like 'k', 'ok' ({negativity[sender]['passive_aggressive_responses']} times)",
                    'severity': min(100, negativity[sender]['passive_rate'] * 20),
                    'suggestion': 'Elaborate more to show engagement',
                    'icon': '💬'
                })

            # Self-centeredness
            if self_centered[sender]['i_to_you_ratio'] > 1.5:
                traits.append({
                    'trait': 'Talks More About Self',
                    'description': f"Uses 'I/me' {self_centered[sender]['i_to_you_ratio']:.1f}x more than 'you'",
                    'severity': min(100, (self_centered[sender]['i_to_you_ratio'] - 1) * 50),
                    'suggestion': 'Ask more about your partner\'s day and feelings',
                    'icon': '🪞'
                })

            if self_centered[sender]['question_ratio'] < 15:
                traits.append({
                    'trait': 'Could Ask More Questions',
                    'description': f"Only {self_centered[sender]['question_ratio']:.0f}% of messages are questions",
                    'severity': min(100, (25 - self_centered[sender]['question_ratio']) * 3),
                    'suggestion': 'Show more curiosity about your partner',
                    'icon': '❓'
                })

            # Emotional availability
            if emotional[sender]['dismissive_responses'] > 20:
                traits.append({
                    'trait': 'Sometimes Dismissive',
                    'description': f"Short responses to emotional messages ({emotional[sender]['dismissive_responses']} times)",
                    'severity': min(100, emotional[sender]['dismissive_responses'] * 2),
                    'suggestion': 'Offer more comfort when partner is emotional',
                    'icon': '😐'
                })

            # Consistency
            if consistency[sender]['consistency_score'] < 60:
                traits.append({
                    'trait': 'Inconsistent Communication',
                    'description': f"Message volume varies a lot (consistency: {consistency[sender]['consistency_score']:.0f}%)",
                    'severity': 100 - consistency[sender]['consistency_score'],
                    'suggestion': 'Try to maintain steady communication',
                    'icon': '📊'
                })

            # Initiative (for the one who starts less)
            other_sender = [s for s in self.participants if s != sender][0] if len(self.participants) > 1 else sender
            if effort[sender]['conversation_starts'] < effort[other_sender]['conversation_starts'] * 0.6:
                ratio = effort[sender]['conversation_starts'] / max(effort[other_sender]['conversation_starts'], 1)
                traits.append({
                    'trait': 'Could Initiate More',
                    'description': f"Starts only {ratio*100:.0f}% as many conversations",
                    'severity': min(100, (1 - ratio) * 80),
                    'suggestion': 'Reach out first more often',
                    'icon': '👋'
                })

            # Sort by severity and take top 5
            traits.sort(key=lambda x: -x['severity'])
            bad_traits[sender] = traits[:5]

        return bad_traits

    def get_all_analysis(self) -> Dict:
        """Get complete trait analysis."""
        return {
            'good_traits': self.get_good_traits(),
            'bad_traits': self.get_bad_traits(),
            'detailed': {
                'supportiveness': self.analyze_supportiveness(),
                'affection': self.analyze_affection_expression(),
                'effort': self.analyze_effort_and_initiative(),
                'responsiveness': self.analyze_responsiveness(),
                'humor': self.analyze_humor(),
                'ghosting': self.analyze_ghosting_patterns(),
                'negativity': self.analyze_negativity(),
                'self_centeredness': self.analyze_self_centeredness(),
                'emotional_availability': self.analyze_emotional_availability(),
                'consistency': self.analyze_consistency()
            }
        }


if __name__ == '__main__':
    from chat_parser import parse_whatsapp_chat
    import json

    file_path = '/Users/arvind/PythonProjects/Chatanaylsi/_chat.txt'
    print(f"Parsing {file_path}...")
    messages = parse_whatsapp_chat(file_path)

    participant_mapping = {
        "~~": "Arvind",
        "bae 🫶": "Palak"
    }

    print("Calculating metrics...")
    metrics = MetricsCalculator(messages, participant_mapping)

    print("Analyzing traits...")
    analyzer = TraitsAnalyzer(messages, metrics, participant_mapping)

    print("\n=== GOOD TRAITS ===")
    good = analyzer.get_good_traits()
    for sender, traits in good.items():
        name = participant_mapping.get(sender, sender)
        print(f"\n{name}:")
        for t in traits:
            print(f"  {t['icon']} {t['trait']}: {t['description']} (Score: {t['score']:.0f})")

    print("\n=== AREAS FOR IMPROVEMENT ===")
    bad = analyzer.get_bad_traits()
    for sender, traits in bad.items():
        name = participant_mapping.get(sender, sender)
        print(f"\n{name}:")
        for t in traits:
            print(f"  {t['icon']} {t['trait']}: {t['description']}")
            print(f"     Tip: {t['suggestion']}")

    # Save results
    output_path = '/Users/arvind/PythonProjects/Chatanaylsi/.tmp/traits_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(analyzer.get_all_analysis(), f, indent=2, default=str)
    print(f"\nSaved to {output_path}")
