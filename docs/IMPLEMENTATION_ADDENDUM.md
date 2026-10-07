# Implementation Addendum

This addendum supersedes older report wording that listed login and live alert delivery under future scope.

## Newly Implemented Features

- Email/password login and registration with hashed passwords
- Role-aware access with a counselor-only analytics page
- Consent-based trusted contact storage in the profile
- Real email alert integration through Resend
- Real SMS alert integration through Twilio
- Provider configuration status visibility inside the app sidebar

## Demo Credentials

- Student demo: `demo@studentwellness.local` / `Demo@12345`
- Counselor demo: `counselor@studentwellness.local` / `Counselor@123`

## Environment Variables

Use `.env.example` as the source of truth for provider setup.

- `ALERT_REAL_DELIVERY_ENABLED`
- `ALERT_EMAIL_PROVIDER`
- `ALERT_EMAIL_FROM`
- `RESEND_API_KEY`
- `ALERT_SMS_PROVIDER`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`
- `TWILIO_MESSAGING_SERVICE_SID`

## Safety Note

Real provider delivery remains disabled by default until `ALERT_REAL_DELIVERY_ENABLED=true` is explicitly set.
