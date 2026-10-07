from __future__ import annotations

from typing import Any


CAMPUS_RESOURCES = {
    "Main Campus": [
        {
            "name": "Campus Counseling Cell",
            "contact": "+91 98765 43210",
            "hours": "Mon-Fri, 9:00 AM - 5:00 PM",
            "type": "Counselor",
        },
        {
            "name": "Faculty Mentor Desk",
            "contact": "mentor@college.edu",
            "hours": "Mon-Sat, 10:00 AM - 4:00 PM",
            "type": "Mentor",
        },
    ],
    "Chennai": [
        {
            "name": "Student Support Centre - Chennai",
            "contact": "+91 98888 22001",
            "hours": "Mon-Fri, 8:30 AM - 6:00 PM",
            "type": "Counselor",
        }
    ],
    "Coimbatore": [
        {
            "name": "Wellness Hub - Coimbatore",
            "contact": "+91 97777 44002",
            "hours": "Mon-Fri, 9:00 AM - 5:30 PM",
            "type": "Counselor",
        }
    ],
}

HELPLINES = [
    {
        "name": "Tele-MANAS India",
        "contact": "14416",
        "note": "24x7 national mental health helpline",
    },
    {
        "name": "Kiran Mental Health Helpline",
        "contact": "1800-599-0019",
        "note": "Government-supported support line",
    },
]


def get_resource_pack(campus: str, risk_level: str = "Normal") -> dict[str, Any]:
    campus_matches = CAMPUS_RESOURCES.get(campus) or CAMPUS_RESOURCES["Main Campus"]
    emergency_note = None
    if risk_level == "High Risk":
        emergency_note = (
            "You may need immediate human support. Please contact a trusted adult, mentor, "
            "or helpline now."
        )

    return {
        "campus": campus,
        "campus_resources": campus_matches,
        "helplines": HELPLINES,
        "emergency_note": emergency_note,
        "coping_tools": [
            "5-minute breathing reset",
            "Walk outside for 10 minutes",
            "Text one trusted person",
            "Break one task into the next 10-minute step",
        ],
        "playlist_hint": "Calm-focus playlist, instrumental study beats, or nature ambience",
        "journal_prompts": [
            "What made today harder than expected?",
            "What is one thing your future self would thank you for tonight?",
            "Who helped you recently, even in a small way?",
        ],
    }
