from __future__ import annotations

from typing import Any

import requests

from shared.config import get_settings


def get_provider_status() -> dict[str, Any]:
    settings = get_settings()
    email_missing: list[str] = []
    sms_missing: list[str] = []

    if settings.alert_email_provider == "resend":
        if not settings.resend_api_key:
            email_missing.append("RESEND_API_KEY")
        if not settings.alert_email_from:
            email_missing.append("ALERT_EMAIL_FROM")
    else:
        email_missing.append("Unsupported email provider")

    if settings.alert_sms_provider == "twilio":
        if not settings.twilio_account_sid:
            sms_missing.append("TWILIO_ACCOUNT_SID")
        if not settings.twilio_auth_token:
            sms_missing.append("TWILIO_AUTH_TOKEN")
        if not settings.twilio_from_number and not settings.twilio_messaging_service_sid:
            sms_missing.append("TWILIO_FROM_NUMBER or TWILIO_MESSAGING_SERVICE_SID")
    else:
        sms_missing.append("Unsupported SMS provider")

    return {
        "real_delivery_enabled": settings.real_alert_delivery_enabled,
        "email": {
            "provider": settings.alert_email_provider,
            "configured": not email_missing,
            "missing": email_missing,
        },
        "sms": {
            "provider": settings.alert_sms_provider,
            "configured": not sms_missing,
            "missing": sms_missing,
        },
    }


def _base_result(channel: str) -> dict[str, Any]:
    return {
        "channel": channel,
        "status": "not_requested",
        "provider": "",
        "provider_id": "",
        "error": "",
        "recipient": "",
    }


def _send_resend_email(to_email: str, subject: str, html: str, text: str) -> dict[str, Any]:
    settings = get_settings()
    payload: dict[str, Any] = {
        "from": settings.alert_email_from,
        "to": [to_email],
        "subject": subject,
        "html": html,
        "text": text,
    }
    if settings.alert_email_reply_to:
        payload["reply_to"] = [settings.alert_email_reply_to]

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "channel": "email",
        "status": "sent",
        "provider": "resend",
        "provider_id": data.get("id", ""),
        "error": "",
        "recipient": to_email,
    }


def _send_twilio_sms(to_phone: str, body: str) -> dict[str, Any]:
    settings = get_settings()
    payload = {
        "To": to_phone,
        "Body": body,
    }
    if settings.twilio_messaging_service_sid:
        payload["MessagingServiceSid"] = settings.twilio_messaging_service_sid
    else:
        payload["From"] = settings.twilio_from_number

    response = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json",
        data=payload,
        auth=(settings.twilio_account_sid, settings.twilio_auth_token),
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "channel": "sms",
        "status": data.get("status", "queued"),
        "provider": "twilio",
        "provider_id": data.get("sid", ""),
        "error": "",
        "recipient": to_phone,
    }


def dispatch_high_risk_alert(profile: dict[str, Any], alert_message: str) -> dict[str, Any]:
    settings = get_settings()
    provider_status = get_provider_status()
    email_result = _base_result("email")
    sms_result = _base_result("sms")

    contact_name = profile.get("alert_contact") or "Trusted contact"
    subject = f"Wellness alert for {profile.get('name') or 'student'}"
    student_name = profile.get("name") or "The student"
    text_body = (
        f"{student_name} triggered a high-risk wellness alert in MindPulse AI. "
        f"{alert_message} Please reach out to them as soon as possible."
    )
    html_body = (
        "<p><strong>MindPulse AI alert</strong></p>"
        f"<p>{student_name} triggered a high-risk wellness alert.</p>"
        f"<p>{alert_message}</p>"
        "<p>Please check in with them as soon as possible.</p>"
    )

    if profile.get("trusted_contact_email"):
        email_result["recipient"] = profile["trusted_contact_email"]
        if not settings.real_alert_delivery_enabled:
            email_result["status"] = "disabled"
            email_result["provider"] = provider_status["email"]["provider"]
            email_result["error"] = "Real delivery is disabled. Set ALERT_REAL_DELIVERY_ENABLED=true."
        elif not provider_status["email"]["configured"]:
            email_result["status"] = "misconfigured"
            email_result["provider"] = provider_status["email"]["provider"]
            email_result["error"] = ", ".join(provider_status["email"]["missing"])
        else:
            try:
                email_result = _send_resend_email(
                    profile["trusted_contact_email"],
                    subject,
                    html_body,
                    text_body,
                )
            except Exception as exc:
                email_result["status"] = "failed"
                email_result["provider"] = provider_status["email"]["provider"]
                email_result["error"] = str(exc)
    else:
        email_result["status"] = "skipped"
        email_result["error"] = "No trusted contact email provided."

    if profile.get("trusted_contact_phone"):
        sms_result["recipient"] = profile["trusted_contact_phone"]
        if not settings.real_alert_delivery_enabled:
            sms_result["status"] = "disabled"
            sms_result["provider"] = provider_status["sms"]["provider"]
            sms_result["error"] = "Real delivery is disabled. Set ALERT_REAL_DELIVERY_ENABLED=true."
        elif not provider_status["sms"]["configured"]:
            sms_result["status"] = "misconfigured"
            sms_result["provider"] = provider_status["sms"]["provider"]
            sms_result["error"] = ", ".join(provider_status["sms"]["missing"])
        else:
            try:
                sms_result = _send_twilio_sms(profile["trusted_contact_phone"], text_body)
            except Exception as exc:
                sms_result["status"] = "failed"
                sms_result["provider"] = provider_status["sms"]["provider"]
                sms_result["error"] = str(exc)
    else:
        sms_result["status"] = "skipped"
        sms_result["error"] = "No trusted contact phone provided."

    return {
        "contact_name": contact_name,
        "email": email_result,
        "sms": sms_result,
        "provider_status": provider_status,
        "message": alert_message,
    }
