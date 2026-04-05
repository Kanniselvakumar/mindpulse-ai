from __future__ import annotations

import re
from collections import Counter
from typing import Any

from backend.services.nlp_engine import analyze_text


LANGUAGE_COPY = {
    "English": {
        "opener": "You do not have to handle this alone.",
        "reset": "We are not trying to fix your whole life in one reply. We are trying to make the next 10 to 20 minutes safer and clearer.",
        "escalate": "If this feels unsafe, or if you think you may harm yourself, contact a trusted person, counselor, helpline, or emergency support right now.",
        "contact_script_intro": "If reaching out feels hard, send this message:",
    },
    "Hindi": {
        "opener": "Aapko yeh sab akela handle nahi karna hai.",
        "reset": "Humein abhi sab kuch solve nahi karna. Sirf agle 10 se 20 minutes ko thoda safer aur clearer banana hai.",
        "escalate": "Agar yeh unsafe lag raha hai, ya aapko lag raha hai ki aap khud ko hurt kar sakte hain, to turant kisi trusted person, counselor, helpline, ya emergency support se contact kijiye.",
        "contact_script_intro": "Agar message bhejna mushkil lag raha hai, yeh bhej sakte hain:",
    },
    "Tamil": {
        "opener": "Neenga idhai thaniya handle panna vendiyadillai.",
        "reset": "Ippo namma ellathayum ore reply-la sari panna poradhillai. Adutha 10 to 20 nimishatha konjam safer-aum clearer-aum panna porom.",
        "escalate": "Idhu unsafe-a irundha, illaina neenga ungalai hurt pannuveenga-nu bayam irundha, udane oru trusted person, counselor, helpline, illa emergency support-ai contact pannunga.",
        "contact_script_intro": "Message anuppa kashtama irundha, idhai anuppalam:",
    },
}

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
        "exam",
        "test",
        "internal",
        "viva",
        "assignment",
        "deadline",
        "marks",
        "result",
        "study",
        "syllabus",
    },
    "burnout": {
        "burnout",
        "drained",
        "exhausted",
        "tired",
        "done",
        "overloaded",
        "overwhelmed",
        "mentally drained",
    },
    "motivation": {
        "motivation",
        "lazy",
        "procrastinating",
        "procrastination",
        "stuck",
        "cant start",
        "can't start",
        "not productive",
    },
    "loneliness": {
        "alone",
        "lonely",
        "isolated",
        "nobody",
        "no one",
        "ignored",
        "left out",
    },
    "sleep": {
        "sleep",
        "insomnia",
        "awake",
        "tired",
        "rest",
        "didnt sleep",
        "didn't sleep",
    },
    "anxiety": {
        "anxious",
        "anxiety",
        "panic",
        "panic attack",
        "worried",
        "overthinking",
        "fear",
        "nervous",
    },
    "sadness": {
        "sad",
        "empty",
        "hopeless",
        "cry",
        "crying",
        "down",
        "heavy",
        "worthless",
    },
    "positive": {
        "better",
        "good",
        "okay",
        "improving",
        "calm",
        "hopeful",
        "relieved",
    },
}

INTENT_BLUEPRINT = {
    "exam_stress": {
        "validation": "It makes sense that exam pressure is squeezing your focus right now.",
        "reflection": "When the brain treats everything as urgent, focus usually gets worse, not better.",
        "stabilize": "Close the mental loop: write the one subject or chapter that matters most today, then ignore the rest for 20 minutes.",
        "next_step": "Do one 20-minute study sprint on the highest-weight topic, then take a 5-minute reset.",
        "reach_out": "If the pressure still feels jammed, message a classmate or mentor and name the exact topic you are stuck on.",
        "follow_up": "Which subject or chapter feels heaviest right now?",
    },
    "burnout": {
        "validation": "This sounds more like overload than lack of effort.",
        "reflection": "When you have been pushing for too long, your brain starts asking for recovery before performance.",
        "stabilize": "Do recovery first: water, a few slow exhales, and a short movement break before asking yourself for more work.",
        "next_step": "Cut today's target in half and choose the single task that protects you most.",
        "reach_out": "Tell one trusted person: 'I am overloaded and need help prioritizing today.'",
        "follow_up": "What is the one task that would reduce the most pressure if it got done first?",
    },
    "motivation": {
        "validation": "Low motivation often appears after stress, pressure, or too many unfinished loops.",
        "reflection": "You do not need a big burst of motivation right now. You need a tiny start.",
        "stabilize": "Shrink the target until it feels almost too small to resist: open the material and work for just 2 minutes.",
        "next_step": "Pick one visible finish line such as one question, one paragraph, or one slide.",
        "reach_out": "If starting alone keeps failing, ask a friend to sit on call while you begin.",
        "follow_up": "What is the smallest version of studying that still counts today?",
    },
    "loneliness": {
        "validation": "Feeling isolated can make academic pressure feel twice as heavy.",
        "reflection": "This is not just about productivity. It sounds like you need connection as well as structure.",
        "stabilize": "Do not stay alone with this for the whole evening. Move toward one safer, more connected space if you can.",
        "next_step": "Choose one gentle task you can do while near people, even if you are not talking much yet.",
        "reach_out": "Message one person and ask for five minutes of company, not a perfect conversation.",
        "follow_up": "Who feels safest to message first, even with a very short text?",
    },
    "sleep": {
        "validation": "Low sleep can make stress, hopelessness, and overthinking feel much louder.",
        "reflection": "Your mind may be reading this as failure when some of it is exhaustion.",
        "stabilize": "Choose lighter work for now and protect tonight's shutdown routine instead of forcing deep focus.",
        "next_step": "Write tomorrow's first task before bed so your brain does not keep rehearsing it all night.",
        "reach_out": "If sleep disruption keeps repeating, tell a mentor, counselor, or doctor rather than carrying it quietly.",
        "follow_up": "What usually keeps you awake most: worry, deadlines, phone use, or something else?",
    },
    "anxiety": {
        "validation": "Your mind sounds stuck in threat mode right now, which can make focus feel impossible.",
        "reflection": "When anxiety rises, the goal is not to argue with every thought. It is to get your body and attention a little steadier.",
        "stabilize": "Write the worry in one sentence, then split the page into two columns: facts and fears.",
        "next_step": "Pick one action that would still help even if the worry turned out to be true.",
        "reach_out": "If your body still feels highly activated after that, call or sit with someone instead of white-knuckling it alone.",
        "follow_up": "What is the exact worry your mind keeps looping on?",
    },
    "sadness": {
        "validation": "This sounds emotionally heavy, not just academically frustrating.",
        "reflection": "When sadness gets deep, care usually has to come before performance.",
        "stabilize": "Start with basics: water, food if you have skipped it, daylight, and one gentle task.",
        "next_step": "Choose one task that keeps your day moving without asking too much from you.",
        "reach_out": "Please let one safe person know you are having a hard day instead of hiding it.",
        "follow_up": "What would make today feel 5% less heavy?",
    },
    "positive": {
        "validation": "It sounds like you are noticing some relief or momentum, which is worth protecting.",
        "reflection": "Good phases matter because they show you what helps, not because you have to be positive all the time.",
        "stabilize": "Capture the habit or event that helped this shift happen.",
        "next_step": "Repeat that one helpful action tomorrow before the day gets busy.",
        "reach_out": "If someone supported you recently, consider telling them it helped.",
        "follow_up": "What do you want to protect from today so it does not get lost tomorrow?",
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
                scores[intent] += 2

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
        primary = "anxiety" if analysis.get("sentiment_label") == "negative" else "positive"
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
        signals.append(f"stress has been high ({stress_score}/10)")
    if exam_pressure is not None and float(exam_pressure) >= 8:
        signals.append(f"exam pressure is elevated ({exam_pressure}/10)")
    if attendance_rate is not None and float(attendance_rate) < 80:
        signals.append(f"attendance has dipped ({attendance_rate}%)")

    if not signals:
        return ""

    if len(signals) == 1:
        summary = signals[0]
    else:
        summary = ", ".join(signals[:-1]) + f", and {signals[-1]}"
    return f"Your recent check-ins also suggest that {summary}."


def _contact_script(intent: str) -> str:
    if intent in {"loneliness", "sadness"}:
        return "I am having a rough time today and I do not want to stay alone with it. Can you check in on me?"
    if intent in {"burnout", "exam_stress", "motivation"}:
        return "I am overloaded and need help settling on the next priority. Can I talk to you for 5 minutes?"
    return "I am feeling overwhelmed right now and I would feel safer if someone checked in with me."


def _crisis_response(language_pack: dict[str, str]) -> dict[str, Any]:
    reply = "\n\n".join(
        [
            language_pack["opener"],
            "I want to take what you said seriously. Your safety matters more than productivity right now.",
            "Please move toward a safer space and contact a trusted person, counselor, helpline, or emergency service immediately.",
            language_pack["escalate"],
        ]
    )

    return {
        "reply": reply,
        "follow_up_prompt": "Who can you contact right now, and what is the fastest way to reach them?",
        "analysis": {
            "emotion": "crisis",
            "sentiment_label": "negative",
            "keywords_detected": [],
        },
        "coping_cards": [
            "Call or text one trusted person right now.",
            "Move to a shared or safer space instead of staying alone.",
            "Use emergency support or a helpline immediately if you might act on these thoughts.",
        ],
        "support_plan": [
            {"title": "Safety First", "step": "Put distance between yourself and anything you could use to hurt yourself."},
            {"title": "Reach Someone", "step": "Contact one trusted person, counselor, or emergency support now."},
            {"title": "Stay With People", "step": "Do not isolate yourself while this feels intense."},
        ],
        "focus_area": "Immediate Safety",
        "reflection": "This needs human support now, not more pressure to cope alone.",
        "contact_script": "I do not feel safe right now and I need you to stay with me or help me get support.",
        "escalation_note": language_pack["escalate"],
    }


def build_support_reply(
    message: str,
    latest_snapshot: dict[str, Any] | None,
    language: str = "English",
) -> dict[str, Any]:
    language_pack = LANGUAGE_COPY.get(language, LANGUAGE_COPY["English"])
    analysis = analyze_text(message)
    risk_level = (latest_snapshot or {}).get("risk_level", "Normal")

    if _detect_crisis(message):
        return _crisis_response(language_pack)

    primary_intent, ranked_intents = _detect_intent(message, analysis, latest_snapshot)
    blueprint = INTENT_BLUEPRINT.get(primary_intent, INTENT_BLUEPRINT["anxiety"])
    context_line = _build_context_line(latest_snapshot)

    reply_parts = [
        language_pack["opener"],
        blueprint["validation"],
        blueprint["reflection"],
        language_pack["reset"],
    ]

    if context_line:
        reply_parts.append(context_line)

    reply_parts.append(f"For the next step, try this: {blueprint['stabilize']}")

    if risk_level == "High Risk":
        reply_parts.append(language_pack["escalate"])
    elif primary_intent in {"loneliness", "sadness", "burnout"}:
        reply_parts.append("Please ask for support earlier than your mind is telling you to.")
    elif primary_intent == "positive":
        reply_parts.append("You do not need to do everything perfectly today; just protect the momentum you already created.")

    coping_cards = [
        blueprint["stabilize"],
        blueprint["next_step"],
        blueprint["reach_out"],
    ]

    support_plan = [
        {"title": "Stabilize", "step": blueprint["stabilize"]},
        {"title": "Next Step", "step": blueprint["next_step"]},
        {"title": "Reach Out", "step": blueprint["reach_out"]},
    ]

    response = {
        "reply": "\n\n".join(reply_parts),
        "follow_up_prompt": blueprint["follow_up"],
        "analysis": analysis,
        "coping_cards": coping_cards,
        "support_plan": support_plan,
        "focus_area": primary_intent.replace("_", " ").title(),
        "reflection": context_line or blueprint["reflection"],
        "contact_script": _contact_script(primary_intent),
        "escalation_note": language_pack["escalate"] if risk_level == "High Risk" else "",
        "detected_intents": ranked_intents,
        "contact_script_intro": language_pack["contact_script_intro"],
    }

    return response
