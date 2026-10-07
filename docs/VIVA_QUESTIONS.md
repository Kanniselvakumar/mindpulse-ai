# MindPulse AI
## Viva Questions and Answers

### 1. What is the main aim of this project?

The main aim is to build an AI-based student wellness support system that detects emotional and behavioral warning signs early and provides supportive suggestions without claiming medical diagnosis.

### 2. Why did you choose this topic?

I chose this topic because student stress and burnout are common, but early support systems are limited. This project combines social relevance with AI, NLP, machine learning, dashboarding, and deployment.

### 3. Why is this project important?

It is important because many students struggle silently. A simple digital assistant can improve self-awareness, encourage timely help-seeking, and help institutions understand aggregate wellness trends ethically.

### 4. Which technologies are used in the project?

The project uses Streamlit, Flask, Python, SQLite, Pandas, Plotly, TextBlob, NLTK, scikit-learn, and Render.

### 5. Why did you use Streamlit?

Streamlit is fast, beginner-friendly, and ideal for building interactive dashboards and demo-ready interfaces without complex frontend infrastructure.

### 6. Why did you use Flask if Streamlit is already present?

Flask helps structure backend APIs and business logic clearly. It makes the project more modular and closer to production architecture.

### 7. What data does the system collect?

The system collects mood score, stress, energy, sleep, attendance, assignment load, social connectedness, exam pressure, and optional journal notes.

### 8. How does NLP work in this project?

The journal text is analyzed using polarity, subjectivity, compound sentiment, and emotion keyword detection to identify emotional tone and likely mental state.

### 9. What machine learning is used?

The project uses two supervised classifiers for credibility: Logistic Regression as a baseline and Random Forest as the main nonlinear model. The final deployed classifier is selected after evaluation on a held-out test split. The project also uses LinearRegression for short-term low-day forecasting.

### 10. Where did your dataset come from?

The current deployed model is trained on a simulated student wellness dataset generated inside the project. It contains realistic student features such as mood, stress, energy, sleep, attendance, assignments, social connection, exam pressure, and NLP sentiment. This makes the data source transparent and safe for academic demonstration.

### 11. What are the output classes of the model?

The model classifies student state into Normal, Stressed, and High Risk.

### 12. Is this a medical diagnosis system?

No. It is only a support and early-detection system. It encourages students to seek human or professional help when risk appears high.

### 13. How is privacy handled?

Privacy is handled through encrypted notes, anonymous mode, consent-based alerts, and aggregate-only counselor analytics.

### 14. What is the role of the counselor dashboard?

The counselor dashboard shows only anonymized trends and group-level insights. It avoids revealing personal journal data.

### 15. What makes this project different from a normal mood tracker?

It combines mood check-ins with NLP, behavioral analytics, academic factors, risk detection, dashboard trends, and intervention guidance.

### 16. What are the limitations?

The system depends partly on self-reported data, is not medically validated, and currently uses demo-ready rather than enterprise-scale infrastructure.

### 17. What can be improved in the future?

Future work includes larger real-world institution datasets, voice analysis, translation support, stronger forecasting, and full mobile deployment.

### 18. Why is this a good final-year project?

It solves a real social problem, demonstrates multiple AI and software engineering skills, includes ethics and privacy considerations, and is deployable.
