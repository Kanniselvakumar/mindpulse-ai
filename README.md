# MindPulse AI

MindPulse AI is a college-project-ready mental health support platform built with `Streamlit`, `Flask`, `SQLite`, `Pandas`, `NLTK`, `TextBlob`, and `scikit-learn`.

It is designed as a support tool, not a medical diagnosis system. The app helps students log daily mood signals, connect stress patterns with attendance and academic pressure, and surface early support actions with privacy-aware analytics.

## Features

- Daily emoji-based mood check-in with sleep, attendance, assignment load, and social connection signals
- Login and registration with hashed passwords and role-aware access
- NLP sentiment and emotion analysis using TextBlob and VADER-style sentiment scoring
- ML-backed risk classification into `Normal`, `Stressed`, and `High Risk`
- Supervised model comparison using `LogisticRegression` and `RandomForestClassifier`
- Forecasting for potential low days based on recent mood and stress history
- AI support companion with multilingual prompts in English, Hindi, and Tamil
- Resource hub with campus support details, helplines, and coping tools
- Anonymous peer wall and study-buddy matching suggestions
- Aggregate counselor dashboard with anonymized analytics only
- Encrypted journal note storage and consent-based alert flow
- Real provider integrations for email alerts via Resend and SMS alerts via Twilio

## Project Structure

```text
student-wellness-system/
+-- backend/
|   +-- api/
|   +-- data/
|   +-- models/
|   +-- services/
|   +-- database.py
|   +-- app_platform.py
|   `-- wsgi.py
+-- docs/
|   +-- FINAL_YEAR_PROJECT_REPORT.md
|   +-- PRESENTATION_OUTLINE.md
|   `-- VIVA_QUESTIONS.md
+-- frontend/
|   +-- pages/
|   +-- Home.py
|   `-- ui.py
+-- scripts/
+-- shared/
+-- tests/
+-- render.yaml
+-- requirements.txt
`-- runtime.txt
```


## ML and Dataset Credibility

To make the project stronger for judges and viva review, MindPulse AI now includes:

- a supervised `LogisticRegression` baseline model
- a supervised `RandomForestClassifier` model
- automatic model comparison using accuracy and macro-F1
- a transparent simulated student wellness dataset with `1800` labeled records
- clear preprocessing notes covering feature generation, label creation, and train-test splitting

Current dataset approach:

- The deployed classifier is trained on a simulated student wellness dataset generated inside the project.
- Labels are `Normal`, `Stressed`, and `High Risk`.
- Features include mood, stress, energy, sleep, attendance, assignments, social connection, exam pressure, and NLP compound sentiment.
- This keeps the data source easy to explain and safe for a college demonstration.

## Local Run

1. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

2. Bootstrap the local database:

   From the project root:

   ```bash
   python -m scripts.bootstrap_data
   ```

   Alternative from the project root:

   ```bash
   python bootstrap_data.py
   ```

   This seeds demo accounts as well as sample wellness data.

   Another root-level option:

   ```bash
   python scripts/bootstrap_data.py
   ```

   If your terminal is currently inside `backend/`:

   ```bash
   python bootstrap_data.py
   ```

3. Run the Streamlit app:

   From the project root:

   ```bash
   python run_app.py
   ```

   Direct module form from the project root:

   ```bash
   python -m streamlit run frontend/Home.py
   ```

   If your terminal is inside `backend/`, first move back to the project root:

   ```bash
   cd ..
   python run_app.py
   ```

4. Optional: run the Flask API separately:

   ```bash
   gunicorn backend.wsgi:app
   ```

## Demo Credentials

- Student demo: `demo@studentwellness.local` / `Demo@12345`
- Counselor demo: `counselor@studentwellness.local` / `Counselor@123`

## Alert Provider Setup

Copy `.env.example` to `.env` and fill in the provider values if you want real alert delivery.

Required variables for email with Resend:

- `ALERT_REAL_DELIVERY_ENABLED=true`
- `ALERT_EMAIL_PROVIDER=resend`
- `ALERT_EMAIL_FROM=MindPulse AI <alerts@yourdomain.com>`
- `RESEND_API_KEY=...`

Required variables for SMS with Twilio:

- `ALERT_SMS_PROVIDER=twilio`
- `TWILIO_ACCOUNT_SID=...`
- `TWILIO_AUTH_TOKEN=...`
- `TWILIO_FROM_NUMBER=...`

Alternative Twilio sender option:

- `TWILIO_MESSAGING_SERVICE_SID=...`

Notes:

- Keep `ALERT_REAL_DELIVERY_ENABLED=false` until you finish provider setup.
- High-risk alerts are sent only when the logged-in user enables consent-based alerts and saves a trusted contact email or phone number.
- The counselor dashboard is restricted to counselor or admin roles.

## Render Deployment

This repo includes a `render.yaml` blueprint for one-click deployment on Render.

- Public app service: Streamlit UI
- Included codebase: Flask API, shared backend services, and local SQLite demo mode
- Default Render mode: `STREAMLIT_FORCE_LOCAL_BACKEND=true` so the Streamlit app works without a second service

Deploy steps:

1. Push this project to GitHub.
2. In Render, create a new Blueprint from the repository.
3. Render will detect `render.yaml` and create the web service automatically.
4. Open the deployed URL after the build finishes.

If you want a separate API service later, deploy `backend.wsgi:app` as another Python web service.

## API Endpoints

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/account/<user_id>`
- `GET /api/profile/<user_id>`
- `POST /api/profile`
- `POST /api/checkins`
- `GET /api/dashboard/<user_id>?days=30`
- `GET /api/alerts/provider-status`
- `GET /api/ml/overview`
- `POST /api/assistant`
- `GET /api/resources`
- `GET /api/peer-posts`
- `POST /api/peer-posts`
- `GET /api/buddy-matches/<user_id>`
- `GET /api/admin/overview`

## Testing

```bash
pytest
```

## Judge Pitch

This project stands out because it combines:

- ethical AI support instead of unsafe diagnosis claims
- practical student-centered features instead of generic sentiment analysis alone
- actual supervised ML with Logistic Regression and Random Forest instead of only rule-based NLP
- privacy-aware design with anonymized counselor insights
- deployment-ready architecture that is simple enough for a college demo
