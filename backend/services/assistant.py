from __future__ import annotations

import re
from collections import Counter
from typing import Any

from backend.services.nlp_engine import analyze_text


LANGUAGE_COPY = {
    "English": {
        "opener": "You do not have to handle this alone.",
        "escalate": "If this feels unsafe, or if you think you may harm yourself, contact a trusted person, counselor, helpline, or emergency support right now.",
        "contact_script_intro": "If reaching out feels hard, send this message:",
        "regarding": "Regarding",
    },
    "Hindi": {
        "opener": "Aapko yeh sab akela handle nahi karna hai.",
        "escalate": "Agar yeh unsafe lag raha hai, ya aapko lag raha hai ki aap khud ko hurt kar sakte hain, to turant kisi trusted person, counselor, helpline, ya emergency support se contact kijiye.",
        "contact_script_intro": "Agar message bhejna mushkil lag raha hai, yeh bhej sakte hain:",
        "regarding": "Aapke sawaal",
    },
    "Tamil": {
        "opener": "Neenga idhai thaniya handle panna vendiyadillai.",
        "escalate": "Idhu unsafe-a irundha, illaina neenga ungalai hurt pannuveenga-nu bayam irundha, udane oru trusted person, counselor, helpline, illa emergency support-ai contact pannunga.",
        "contact_script_intro": "Message anuppa kashtama irundha, idhai anuppalam:",
        "regarding": "Ungaludaiya kelvi",
    },
    "Telugu": {
        "opener": "Meeru deeni okkare handle cheyanavasaram ledhu.",
        "escalate": "Idhi unsafe ga anipisthe, leda meeku aathma-pramaadam anipisthe, ventane mee trusted person, counselor, helpline, leda emergency support ni contact cheyandi.",
        "contact_script_intro": "Message pampadam kashtamga unte, idhi pampandi:",
        "regarding": "Mee prashna",
    },
    "Kannada": {
        "opener": "Neevu idhannu obbare handle madabeku antha illa.",
        "escalate": "Idhu unsafe anisidare, athava nimage swatha hurt madikolluva bhaya iddare, udane obba trusted person, counselor, helpline, athava emergency support ge contact madi.",
        "contact_script_intro": "Message kaluhisuvudhu kashta anisidare, idhannu kaluhisi:",
        "regarding": "Nimma prashne",
    },
}
LANGUAGE_COPY["Kanada"] = LANGUAGE_COPY["Kannada"]


def _extract_question_keywords(message: str) -> str:
    cleaned = message.strip()
    words = re.findall(r"\b[A-Za-z0-9'-]+\b", cleaned)
    stop_words = {
        "i", "me", "my", "myself", "we", "our", "ours", "you", "your", "yours",
        "he", "him", "his", "she", "her", "it", "its", "they", "them", "their",
        "what", "which", "who", "whom", "this", "that", "these", "those", "am",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or",
        "because", "as", "until", "while", "of", "at", "by", "for", "with", "about",
        "against", "between", "into", "through", "during", "before", "after", "above",
        "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
        "again", "further", "then", "once", "here", "there", "when", "where", "why",
        "how", "all", "any", "both", "each", "few", "more", "most", "other", "some",
        "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
        "can", "will", "just", "dont", "should", "now", "feel", "feeling"
    }
    meaningful_words = [w for w in words if w.lower() not in stop_words]
    if meaningful_words:
        return " ".join(meaningful_words[:5])
    return cleaned[:45]


CRISIS_PHRASES = {
    "kill myself",
    "end my life",
    "want to die",
    "dont want to live",
    "don't want to live",
    "hurt myself",
    "self harm",
    "suicide",
    "suicidal",
    "not safe",
    "unsafe",
    "cant go on",
    "can't go on",
}

INTENT_KEYWORDS = {
    "exam_stress": {
        "exam", "exams", "test", "tests", "internal", "viva", "assignment", "assignments",
        "deadline", "deadlines", "marks", "result", "results", "study", "studying",
        "syllabus", "failing", "cgpa", "grade", "grades", "quiz", "submission",
    },
    "burnout": {
        "burnout", "drained", "exhausted", "tired", "done", "overloaded",
        "overwhelmed", "mentally drained", "collapsing", "no energy", "worn out",
        "can't take it", "cant take it", "fried",
    },
    "motivation": {
        "motivation", "lazy", "procrastinating", "procrastination", "stuck",
        "cant start", "can't start", "not productive", "distracted", "unmotivated",
        "wasting time", "sluggish", "no drive",
    },
    "sleep": {
        "sleep", "insomnia", "awake", "tired", "rest", "didnt sleep", "didn't sleep",
        "sleepless", "nightmare", "waking up", "cant sleep", "can't sleep", "groggy",
    },
    "anxiety": {
        "anxious", "anxiety", "panic", "panic attack", "worried", "overthinking",
        "fear", "nervous", "shaking", "heart racing", "chest tight", "hyperventilating",
        "dread", "catastrophizing",
    },
    "loneliness": {
        "alone", "lonely", "isolated", "nobody", "no one", "ignored", "left out",
        "homesick", "no friends", "outsider", "disconnected", "alienated",
    },
    "sadness": {
        "sad", "empty", "hopeless", "cry", "crying", "down", "heavy", "worthless",
        "miserable", "depressed", "heartbroken", "gloomy", "unhappy",
    },
    "imposter": {
        "imposter", "not smart enough", "not good enough", "everyone is smarter",
        "fake", "dont belong", "don't belong", "behind everyone", "fraud",
    },
    "relationships": {
        "roommate", "roommates", "friend", "friends", "fight", "arguing", "parents",
        "family pressure", "breakup", "relationship", "peer pressure", "conflict",
    },
    "positive": {
        "better", "good", "okay", "improving", "calm", "hopeful", "relieved",
        "productive today", "happy", "accomplished", "proud", "great", "peaceful",
    },
}

# Diverse, rich guidance architectures for each psychological & academic state
INTENT_CATALOG: dict[str, dict[str, Any]] = {
    "exam_stress": {
        "title": "Exam Stress",
        "validations": [
            "Academic pressure can feel like a heavy weight pressing directly against your ability to think clearly.",
            "Exam anxiety is very real—when your brain perceives a high-stakes threat, it tries to process everything at once and ends up freezing.",
            "It makes total sense that upcoming exams are creating this mental friction right now.",
        ],
        "insights": [
            "When anxiety tells you that you need to master everything in the syllabus right this instant, it destroys concentration. What works is narrowing your field of vision.",
            "Memory retention drops by over 40% when you study in high-panic mode. Calming your physiological state is actually the most efficient study strategy.",
        ],
        "stabilize": "Try the 20-Minute Triage Sprint: Pick the single highest-value concept or chapter, set a timer for 20 minutes, close all extra tabs, and review only that concept.",
        "grounding": "Somatic Exhale: Breathe in for 4 seconds, then exhale slowly for 7 seconds. Do this 4 times to disengage fight-or-flight mode.",
        "next_step": "Write down a 3-bullet checklist of topics you already understand, followed by the ONE topic you will tackle next.",
        "reach_out": "Send a 1-line text to a batchmate or study partner: 'I'm focusing on Chapter 3 for 30 minutes—want to do a quiet study sprint together?'",
        "follow_up": "Which specific subject or question feels like the biggest roadblock right now?",
    },
    "burnout": {
        "title": "Burnout",
        "validations": [
            "This isn't a failure of willpower or discipline—this is your nervous system signaling that you have been operating at maximum capacity for too long.",
            "Mental exhaustion is a biological signal, not a character flaw. Your mind is asking for recovery before performance.",
            "Feeling completely drained usually happens after weeks of carrying continuous micro-stress without real rest.",
        ],
        "insights": [
            "You cannot pour from an empty cup. Pushing through severe burnout produces diminishing returns and prolongs exhaustion.",
            "True recovery means taking time off without secretly guilt-tripping yourself about unfinished work.",
        ],
        "stabilize": "Declare a 30-minute Low-Stimulation Window: Step away from screens, drink a glass of cool water, wash your face, and rest your eyes.",
        "grounding": "Physical Body Scan: Unclench your jaw, drop your shoulders away from your ears, and release the tension in your stomach.",
        "next_step": "Apply the 'Drop, Delegate, Defer' rule: Look at today's to-do list and pick two items you will deliberately push to tomorrow.",
        "reach_out": "Tell someone you trust: 'I'm running on empty today and need to take things slowly. Just letting you know.'",
        "follow_up": "What is one responsibility on your plate today that can safely wait until tomorrow?",
    },
    "motivation": {
        "title": "Motivation",
        "validations": [
            "Waiting for motivation before starting is a trap—motivation usually arrives after action begins, not before.",
            "Feeling stuck or procrastinating is often your brain's unconscious way of avoiding anticipated difficulty or perfectionism.",
            "It's completely normal to have days where your study drive feels at zero.",
        ],
        "insights": [
            "The barrier to entry is what paralyzes you. When you lower the expectation from 'do 4 hours of studying' to 'open the notebook', resistance drops.",
            "Action precedes emotion. Taking a micro-step creates momentum that generates dopamine and clears the mental fog.",
        ],
        "stabilize": "Use the 2-Minute Micro-Start: Open the textbook, document, or code file, and commit to reading or writing just 2 sentences. If you want to stop after 2 minutes, you can.",
        "grounding": "Physical Environment Reset: Clear just the 12 inches of desk space in front of your keyboard to remove visual clutter.",
        "next_step": "Choose the easiest possible starting task—something almost ridiculously simple that takes less than 3 minutes.",
        "reach_out": "Ask a friend or study buddy: 'Can you hold me accountable to finish this one section by 4:00 PM?'",
        "follow_up": "What is the absolute smallest piece of work you could do in the next five minutes?",
    },
    "sleep": {
        "title": "Sleep",
        "validations": [
            "Sleep deprivation magnifies every minor problem, making stress feel twice as sharp and emotions harder to regulate.",
            "When sleep is fractured, your brain's emotional amygdala becomes hyperactive while the rational prefrontal cortex tires out.",
            "Lying awake with a racing mind is deeply frustrating, but fighting with your thoughts makes sleep even harder.",
        ],
        "insights": [
            "If you can't sleep, lying in bed tossing and turning trains your brain to associate your bed with worry rather than rest.",
            "Even quiet physical rest with your eyes closed provides up to 70% of the cognitive restoration of light sleep.",
        ],
        "stabilize": "Cognitive Brain Dump: Take a physical piece of paper and write down every unfinished thought, tomorrow's tasks, or worries so your brain stops rehearsing them.",
        "grounding": "4-7-8 Breathing Cycle: Inhale through the nose for 4 counts, hold for 7 counts, and exhale slowly through mouth for 8 counts.",
        "next_step": "If awake for more than 20 minutes, get out of bed, sit in a dimly lit chair, and read something low-intensity until drowsy.",
        "reach_out": "If insomnia has persisted for several days, schedule a brief check-in with your campus wellness clinic or mentor.",
        "follow_up": "What is keeping your mind busiest at night: specific deadline worries, racing thoughts, or phone usage?",
    },
    "anxiety": {
        "title": "Anxiety",
        "validations": [
            "Your body is experiencing a false alarm right now—intense physical sensations like a tight chest or racing thoughts are adrenaline, not actual danger.",
            "Anxiety thrives on uncertainty and catastrophizing. Recognizing that you are safe in this exact room right now is your first anchor.",
            "You don't have to debate every anxious thought. Thoughts are mental events, not objective predictions of the future.",
        ],
        "insights": [
            "When anxiety spikes, logic rarely works immediately because your sympathetic nervous system is engaged. We must regulate the body first.",
            "Notice the difference between a thought ('I might fail') and reality (you are sitting safely at your desk).",
        ],
        "stabilize": "The 5-4-3-2-1 Sensory Anchor: Look around and name 5 things you can see, 4 things you can physically feel, 3 sounds you hear, 2 scents, and take 1 deep sip of water.",
        "grounding": "Temperature Shock: Splash cool water directly on your forehead and cheeks to trigger the mammalian dive reflex and slow your heart rate.",
        "next_step": "Divide a page into two columns: 'Things Under My Control' vs. 'Things Outside My Control'. Put your worry in the right column.",
        "reach_out": "Text someone steady: 'I'm feeling a bit anxious right now—can you tell me something random from your day?'",
        "follow_up": "On a scale from 1 to 10, how intense does the physical tension feel right now?",
    },
    "loneliness": {
        "title": "Connection & Social Anchoring",
        "validations": [
            "Feeling lonely or disconnected while surrounded by hundreds of college students is surprisingly common and painful.",
            "Loneliness often tricks us into thinking that everyone else has their life, friendships, and study groups figured out.",
            "Carrying heavy academic pressure without social connection makes the days feel longer and heavier.",
        ],
        "insights": [
            "Connection does not require a deep 2-hour conversation; even small micro-interactions (greeting a librarian, studying in a café) reduce isolation.",
            "Vulnerability is magnetic—when you honestly share that you're finding things challenging, other students usually feel relieved to hear it.",
        ],
        "stabilize": "Change Your Physical Geography: Move your study spot to a shared communal space—the university library, a quiet campus corner, or a coffee shop.",
        "grounding": "Sensory Presence: Feel the weight of your feet firmly grounded on the floor and the air moving around you.",
        "next_step": "Check our **Peer Support Wall** to read encouragement notes from other students or post an anonymous thought.",
        "reach_out": "Send a low-stakes check-in to an old friend or family member: 'Hey, was just thinking of you! Hope your week is going well.'",
        "follow_up": "Is there someone you haven't spoken to in a while who usually brings calm energy?",
    },
    "sadness": {
        "title": "Gentle Compassion & Comfort",
        "validations": [
            "It is okay to not be okay today. You don't have to put on a brave face or pretend that everything is smooth.",
            "Sadness slows us down for a reason. Sometimes giving yourself permission to feel sad is the gentlest path forward.",
            "Heavy days happen. What matters is treating yourself with the same compassion you would offer a struggling close friend.",
        ],
        "insights": [
            "When your mood is low, high expectations lead to guilt. Today is a day for minimum viable progress and self-care.",
            "Emotional weather changes. This heavy mood feels permanent while you are in it, but it will shift.",
        ],
        "stabilize": "Engage in Pure Baseline Care: Wrap up in a comfortable hoodie or blanket, drink something warm, and ensure you have eaten something nutritious.",
        "grounding": "Self-Compassion Touch: Place a warm hand gently over your chest or upper arm and take three slow, steady breaths.",
        "next_step": "Pick one tiny task that brings a slight sense of comfort—listening to a favorite calm track or taking a brief stroll outside.",
        "reach_out": "Reach out to someone safe: 'I'm having a quiet, difficult day. Just wanted to connect briefly.'",
        "follow_up": "What is one kind, gentle thing you can do for yourself in the next hour?",
    },
    "imposter": {
        "title": "Imposter Syndrome & Self-Worth",
        "validations": [
            "Feeling like you don't belong or aren't smart enough is the hallmark of imposter syndrome—especially in ambitious college programs.",
            "You were admitted to your course and your university because of real ability and merit, not luck or coincidence.",
            "Comparing your internal doubts to everyone else's polished external performance is a guaranteed trap.",
        ],
        "insights": [
            "Everyone struggles; very few students talk openly about their confusion or fears of being exposed.",
            "Doubt is often evidence that you are learning at the edge of your comfort zone, where genuine growth happens.",
        ],
        "stabilize": "The Competence Audit: Write down three challenging concepts, projects, or exams you managed to navigate in the past.",
        "grounding": "Ground in Current Facts: Remind yourself: 'My anxiety is a feeling; it is not a grade or a transcript.'",
        "next_step": "Ask a classmate or professor one clarification question on a difficult topic—asking questions is what skilled students do.",
        "reach_out": "Mention to a peer: 'Did you find that last assignment tricky too?' (You'll almost certainly hear a resounding 'yes').",
        "follow_up": "What specific comparison or recent task triggered this feeling of self-doubt?",
    },
    "relationships": {
        "title": "Interpersonal & Peer Harmony",
        "validations": [
            "Roommate friction, family expectations, or peer drama can drain more energy than four hours of difficult exams.",
            "When relationships feel tense, your brain stays in defensive mode, making study and rest very difficult.",
            "It is completely reasonable to set clear, quiet boundaries to protect your mental peace during busy semesters.",
        ],
        "insights": [
            "You cannot control how another person behaves or reacts; you can only control your own boundaries and response.",
            "Most interpersonal conflict in college stems from unspoken assumptions or stress-induced irritability rather than malice.",
        ],
        "stabilize": "The 30-Minute Pause: Do not send emotionally reactive messages right now. Write your honest draft in private notes first, then wait 30 minutes.",
        "grounding": "Boundaries Visualizer: Envision a clear boundary around your study desk that protects your energy for today.",
        "next_step": "Plan a calm, direct 2-sentence conversation: 'Hey, I've been feeling stressed lately and need quiet hours after 10 PM. Can we work together on that?'",
        "reach_out": "Talk to a neutral mentor, senior, or counselor if roommate or family tension feels chronic.",
        "follow_up": "What is the core boundary or clarity you need most in this situation right now?",
    },
    "positive": {
        "title": "Momentum & Celebration",
        "validations": [
            "It is wonderful to hear that you are noticing relief, energy, or positive momentum today!",
            "Recognizing good days and progress is a crucial wellness skill—celebrating small wins trains your brain to notice resilience.",
            "Protecting your positive momentum allows you to build a buffer for future demanding periods.",
        ],
        "insights": [
            "Take note of what went right today: Did you sleep well? Did you take breaks? Keep repeating that helpful habit.",
            "You don't have to sustain 100% perfection tomorrow; simply enjoy and savor the clarity you have right now.",
        ],
        "stabilize": "Anchor the Win: Write down in 1 sentence what habit or shift helped create this good mood today.",
        "grounding": "Savoring Breath: Inhale deeply, acknowledging the calm and lightness you feel right now.",
        "next_step": "Lock in one helpful routine for tomorrow morning before demands pile up.",
        "reach_out": "Share a word of encouragement on our **Peer Support Wall** to pass on some positive energy to a peer who might need it.",
        "follow_up": "What was the best part of your day that you want to remember?",
    },
}


def _normalize_text(message: str) -> str:
    cleaned = message.lower().strip()
    cleaned = cleaned.replace("i'm", "im").replace("can't", "cant").replace("don't", "dont")
    return re.sub(r"\s+", " ", cleaned)


def _detect_crisis(message: str) -> bool:
    lowered = _normalize_text(message)
    return any(phrase in lowered for phrase in CRISIS_PHRASES)


def _detect_intent(
    message: str,
    analysis: dict[str, Any],
    latest_snapshot: dict[str, Any] | None,
) -> tuple[str, list[str]]:
    lowered = _normalize_text(message)
    scores: Counter[str] = Counter()

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lowered:
                scores[intent] += 3

    emotion = analysis.get("emotion", "balanced")
    if emotion == "anxiety":
        scores["anxiety"] += 3
    elif emotion == "burnout":
        scores["burnout"] += 3
    elif emotion == "sadness":
        scores["sadness"] += 3
    elif emotion == "joy":
        scores["positive"] += 3

    if analysis.get("sentiment_label") == "negative":
        scores["anxiety"] += 1
        scores["sadness"] += 1
    elif analysis.get("sentiment_label") == "positive":
        scores["positive"] += 1

    if latest_snapshot:
        if float(latest_snapshot.get("exam_pressure", 0)) >= 8:
            scores["exam_stress"] += 2
        if float(latest_snapshot.get("sleep_hours", 7)) < 6:
            scores["sleep"] += 2
        if float(latest_snapshot.get("stress_score", 0)) >= 8:
            scores["anxiety"] += 2
        if float(latest_snapshot.get("social_connectedness", 3)) <= 2:
            scores["loneliness"] += 2
        if float(latest_snapshot.get("mood_score", 3)) <= 2:
            scores["sadness"] += 2
        if float(latest_snapshot.get("energy_score", 6)) <= 4:
            scores["burnout"] += 1

    if not scores:
        primary = "anxiety" if analysis.get("sentiment_label") == "negative" else "exam_stress"
        return primary, [primary]

    ranked = [intent for intent, _ in scores.most_common(3)]
    return ranked[0], ranked


def _build_context_line(latest_snapshot: dict[str, Any] | None) -> str:
    if not latest_snapshot:
        return ""

    signals: list[str] = []
    sleep_hours = latest_snapshot.get("sleep_hours")
    stress_score = latest_snapshot.get("stress_score")
    exam_pressure = latest_snapshot.get("exam_pressure")
    attendance_rate = latest_snapshot.get("attendance_rate")

    if sleep_hours is not None and float(sleep_hours) < 6:
        signals.append(f"sleep has been low ({sleep_hours} hrs)")
    if stress_score is not None and float(stress_score) >= 7:
        signals.append(f"recent stress index is elevated ({stress_score}/10)")
    if exam_pressure is not None and float(exam_pressure) >= 8:
        signals.append(f"exam pressure is high ({exam_pressure}/10)")
    if attendance_rate is not None and float(attendance_rate) < 80:
        signals.append(f"class attendance has dipped ({attendance_rate}%)")

    if not signals:
        return ""

    if len(signals) == 1:
        summary = signals[0]
    else:
        summary = ", ".join(signals[:-1]) + f", and {signals[-1]}"
    return f"*(Looking at your recent wellness signals, {summary}. Let's take that into account.)*"


def _contact_script(intent: str) -> str:
    scripts = {
        "loneliness": "Hey, I've been feeling a bit isolated and overwhelmed today. Are you free to chat or grab a quick tea later?",
        "sadness": "I'm having a rough day emotionally and don't want to carry it all by myself. Could you check in on me when you get a moment?",
        "burnout": "Hey mentor/friend, I'm running on empty and struggling with overload. Could you help me look over my priorities for this week?",
        "exam_stress": "Hey, I'm feeling stressed about this upcoming syllabus. Do you want to do a 30-minute quiet study sprint together?",
        "motivation": "I'm having trouble starting on my assignments today. Could you check on me in an hour to see if I finished my first task?",
        "anxiety": "Hey, my anxiety is flaring up a bit right now. Would you mind sitting with me or talking about something random for 5 minutes?",
        "sleep": "Hey, my sleep schedule has been completely disrupted recently. I might need to take things a bit slower today.",
    }
    return scripts.get(intent, "I'm feeling a bit overwhelmed with college workload right now and wanted to reach out.")


def _crisis_response(language_pack: dict[str, str], message: str = "") -> dict[str, Any]:
    question_keywords = _extract_question_keywords(message) if message else ""
    user_topic_str = f"'{question_keywords}'" if question_keywords else ""

    reply_parts = [
        f"🚨 **Safety & Immediate Support**",
        language_pack["opener"],
        "I hear how much pain you are experiencing right now, and I want to take your words seriously.",
        "Your safety and wellbeing matter infinitely more than any academic deadline, grade, or college requirement.",
        "Please step away from isolation and reach out to someone who can physically support you right now.",
        language_pack["escalate"],
    ]

    return {
        "reply": "\n\n".join(reply_parts),
        "follow_up_prompt": "Who is one trusted person, friend, counselor, or family member you can call right now?",
        "analysis": {
            "emotion": "crisis",
            "sentiment_label": "negative",
            "keywords_detected": [],
        },
        "coping_cards": [
            "Call a campus counselor, family member, or trusted friend immediately.",
            "Move to a shared space with other people nearby.",
            "Contact National Crisis Helplines (e.g., Tele-MANAS: 14416 / 1800-891-4416).",
        ],
        "support_plan": [
            {"title": "1. Prioritize Safety", "step": "Put physical distance between yourself and any dangerous environment."},
            {"title": "2. Direct Contact", "step": "Call or message someone trusted without trying to hide how you feel."},
            {"title": "3. Immediate Escalation", "step": "Contact your university emergency desk or helpline right now."},
        ],
        "focus_area": "Immediate Safety & Crisis Care",
        "reflection": "This requires compassionate human care right now. You do not have to carry this alone.",
        "contact_script": "I do not feel safe right now and I need you to stay with me or help me get support.",
        "escalation_note": language_pack["escalate"],
        "detected_intents": ["crisis"],
        "contact_script_intro": language_pack["contact_script_intro"],
    }


def build_support_reply(
    message: str,
    latest_snapshot: dict[str, Any] | None,
    language: str = "English",
) -> dict[str, Any]:
    language_pack = LANGUAGE_COPY.get(language) or LANGUAGE_COPY.get(language.title()) or LANGUAGE_COPY["English"]
    analysis = analyze_text(message)
    risk_level = (latest_snapshot or {}).get("risk_level", "Normal")

    if _detect_crisis(message):
        return _crisis_response(language_pack, message)

    primary_intent, ranked_intents = _detect_intent(message, analysis, latest_snapshot)
    blueprint = INTENT_CATALOG.get(primary_intent, INTENT_CATALOG["anxiety"])
    context_line = _build_context_line(latest_snapshot)

    # Dynamic selection of validation and insight to keep answers varied and fresh
    msg_hash = abs(hash(message)) % len(blueprint["validations"])
    selected_validation = blueprint["validations"][msg_hash]
    insight_idx = abs(hash(message + "insight")) % len(blueprint["insights"])
    selected_insight = blueprint["insights"][insight_idx]

    question_keywords = _extract_question_keywords(message)
    topic_mention = f"Regarding **{question_keywords}**:" if question_keywords else ""

    reply_parts = []
    if topic_mention:
        reply_parts.append(topic_mention)

    reply_parts.append(selected_validation)
    reply_parts.append(selected_insight)

    if context_line:
        reply_parts.append(context_line)

    reply_parts.append(f"👉 **Immediate Recommendation:**\n{blueprint['stabilize']}")

    if risk_level == "High Risk":
        reply_parts.append(f"⚠️ {language_pack['escalate']}")

    coping_cards = [
        f"🎯 Action: {blueprint['stabilize']}",
        f"🧘 Grounding: {blueprint['grounding']}",
        f"🤝 Connection: {blueprint['reach_out']}",
    ]

    support_plan = [
        {"title": "1. Stabilize", "step": blueprint["stabilize"]},
        {"title": "2. Micro-Step", "step": blueprint["next_step"]},
        {"title": "3. Reach Out", "step": blueprint["reach_out"]},
    ]

    return {
        "reply": "\n\n".join(reply_parts),
        "follow_up_prompt": blueprint["follow_up"],
        "analysis": analysis,
        "coping_cards": coping_cards,
        "support_plan": support_plan,
        "focus_area": blueprint["title"],
        "reflection": selected_insight,
        "contact_script": _contact_script(primary_intent),
        "escalation_note": language_pack["escalate"] if risk_level == "High Risk" else "",
        "detected_intents": ranked_intents,
        "contact_script_intro": language_pack["contact_script_intro"],
    }
