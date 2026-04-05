# MindPulse AI
## Final-Year Project Report

### 1. Title

MindPulse AI: An AI-Based Mood and Behavior Detection System for Student Mental Health Support

### 2. Student and Institution Details

Use this section on your submitted copy.

- Student Name: ______________________
- Register Number: ___________________
- Department: ________________________
- College Name: ______________________
- Guide Name: ________________________
- Academic Year: _____________________

### 3. Abstract

Student mental wellbeing has a direct impact on academic performance, social behavior, attendance, sleep quality, and overall quality of life. In many colleges, stress, burnout, anxiety, social isolation, and academic pressure are noticed only after the situation becomes serious. This project proposes MindPulse AI, a student wellness platform that helps detect early mental health signals using natural language processing, mood tracking, and behavioral analytics. The system is designed as a support platform and not as a medical diagnosis tool.

The application allows students to perform quick daily check-ins using mood selection, stress level, energy level, sleep hours, attendance percentage, assignment load, and social connectedness. Optional journal input is analyzed using sentiment analysis and emotion detection. These signals are processed through a risk analysis engine that classifies the student's state into Normal, Stressed, or High Risk. Based on the result, the system provides personalized suggestions, coping strategies, motivational support, and resource recommendations. If the student has explicitly enabled consent-based alerts, the platform can also prepare escalation notifications for a trusted mentor or contact.

The project is implemented using Streamlit for the frontend, Flask for API design, SQLite for storage, Pandas for analytics, TextBlob and VADER-style sentiment analysis for NLP, and scikit-learn for lightweight machine learning. It also includes a peer-support wall, counselor-level aggregate insights, multilingual support prompts, and a Render deployment configuration. The final system demonstrates how AI can be used responsibly to support students through early detection, self-awareness, and guided intervention in an ethical and privacy-conscious manner.

### 4. Introduction

Mental health challenges among students are increasing because of academic competition, examination pressure, career uncertainty, reduced sleep, and lack of emotional support. Students often continue struggling silently until the condition begins affecting class participation, grades, or personal wellbeing. Traditional support systems are helpful, but they are usually reactive and depend on the student actively asking for help.

This project addresses that gap by building a digital wellness companion that helps students reflect on their emotional state every day and receive early supportive guidance. Instead of waiting for a crisis, the system continuously studies mood and behavioral patterns, giving students practical, personalized, and ethical support. The aim is not to replace professional counselors, but to help identify early warning signals and encourage timely action.

### 5. Problem Statement

Many students experience stress, anxiety, loneliness, burnout, and emotional instability, but institutions often lack simple, accessible, and privacy-aware digital tools that can detect early warning signs and offer supportive intervention. Existing mood trackers are usually too basic, while medical systems are too complex and sensitive for student project use. Therefore, there is a need for a practical AI-powered platform like MindPulse AI that combines daily check-ins, sentiment analysis, behavioral insights, academic signal correlation, and ethical support recommendations in one platform.

### 6. Objectives

- To design and develop a student-friendly wellness support platform.
- To capture daily emotional and behavioral signals through structured check-ins.
- To analyze journal text using NLP-based sentiment and emotion detection.
- To classify student wellbeing status into Normal, Stressed, or High Risk.
- To generate personalized recommendations based on detected mood and stress signals.
- To connect academic indicators such as attendance, sleep, and assignment load with wellbeing trends.
- To provide privacy-aware counselor insights without exposing individual private journals.
- To prepare the application for real-world demo deployment using Render.

### 7. Scope of the Project

The scope of this project includes student self-reporting, AI-based text analysis, mood visualization, low-day forecasting, peer-support features, and aggregated wellness analytics. It is suitable for college demos, academic review, and prototype-level institutional discussion.

The system does not provide medical diagnosis, psychiatric judgment, or emergency response automation. It is intended only as a support assistant that promotes self-awareness and responsible help-seeking behavior.

### 8. Existing System and Limitations

In many institutions, student wellbeing support depends on manual observation by faculty mentors, classmates, or counselors. Some students may also use generic diary apps or simple mood trackers. These approaches have several limitations:

- No structured connection between mental state and academic behavior
- No early detection of trends across multiple days
- No intelligent sentiment analysis of student journal text
- No personalized intervention suggestions
- No privacy-aware analytics for counselors or mentors
- No lightweight deployment path for demonstration or campus pilots

### 9. Proposed System

The proposed system is MindPulse AI with the following capabilities:

- Daily emoji-style mood check-in
- Journal-based sentiment and emotion analysis
- Stress, energy, sleep, assignment, attendance, and social tracking
- Risk classification into Normal, Stressed, and High Risk
- Personalized support recommendations and breathing exercises
- Resource hub with campus support and helpline references
- Anonymous peer wall and study-buddy matching
- Aggregate counselor dashboard with anonymized insights
- Deployment-ready monorepo architecture using Streamlit and Flask

### 10. System Architecture

The project follows a modular architecture.

#### 10.1 Frontend Layer

The frontend is developed using Streamlit. It provides:

- Home dashboard
- Daily check-in page
- Mood analytics dashboard
- AI support companion
- Resource hub
- Peer support wall
- Counselor insights page

#### 10.2 Backend Layer

The backend uses Flask-style service routing and a shared platform layer. It handles:

- Request processing
- Data storage and retrieval
- NLP analysis
- Risk scoring
- Recommendation generation
- Dashboard aggregation

#### 10.3 Database Layer

SQLite is used as the local database for:

- user profiles
- mood logs
- alert events
- peer posts

#### 10.4 AI and Analytics Layer

The AI layer combines:

- TextBlob polarity and subjectivity analysis
- VADER-style sentiment scoring for compound sentiment
- keyword-based emotion classification
- supervised risk classification using Logistic Regression and Random Forest
- trend-based low-day forecasting using LinearRegression

#### 10.5 Training Dataset and Preprocessing

The deployed ML classifier is trained on a simulated student wellness dataset generated within the project. This design keeps the data source transparent and ethically safe for academic demonstration while still supporting supervised learning.

Dataset clarity:

- source: simulated student wellness records generated locally
- sample size: 1800 records
- labels: Normal, Stressed, High Risk
- feature set: mood score, stress, energy, sleep hours, attendance, assignments due, social connectedness, exam pressure, and NLP compound sentiment

Preprocessing and training flow:

- realistic student feature ranges are generated programmatically
- a weighted wellness burden score creates the three class labels
- an 80/20 stratified train-test split is applied
- Logistic Regression is used as the baseline classifier
- Random Forest is used as the nonlinear classifier
- the final production model is selected using macro-F1 and accuracy

### 11. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Interactive web interface |
| Backend | Flask + Python | APIs and business logic |
| Database | SQLite | Lightweight local storage |
| NLP | TextBlob, NLTK, VADER-style analysis | Sentiment and emotion detection |
| Analytics | Pandas, Plotly | Trends, metrics, dashboards |
| Machine Learning | scikit-learn | Risk classification and forecasting |
| Deployment | Render | Cloud hosting |

### 12. Functional Modules

#### 12.1 User Profile Module

This module stores essential student details such as name, course, year, campus, preferred language, anonymous mode, and consent-based alert preferences.

#### 12.2 Daily Check-In Module

Students submit the following daily signals:

- mood label
- mood score
- stress score
- energy score
- sleep hours
- attendance percentage
- assignment count
- social connectedness
- exam pressure
- optional journal note

#### 12.3 NLP Analysis Module

Journal notes are processed to extract:

- polarity
- subjectivity
- compound sentiment
- sentiment label
- emotion category
- detected keywords

This helps the system understand emotional context beyond numerical sliders.

#### 12.4 Risk Detection Module

Risk is estimated using a hybrid strategy:

- a rule-based weighted scoring system
- a supervised machine learning classifier trained on simulated student wellness samples

The final label is chosen from:

- Normal
- Stressed
- High Risk

#### 12.5 Suggestion Engine

The recommendation engine generates:

- priority actions
- coping suggestions
- breathing steps
- study hacks
- habit stack suggestions
- daily challenge
- badge or streak recognition

#### 12.6 Dashboard Module

The dashboard gives:

- weekly and monthly trend lines
- stress and sleep comparison
- risk distribution
- behavior-linked insights
- badge display
- low-day forecast

#### 12.7 Resource and Escalation Module

This module shows:

- campus support contacts
- national helplines
- journal prompts
- coping tools
- escalation guidance for high-risk patterns

#### 12.8 Peer Support Module

The peer-support system includes:

- anonymous encouragement posts
- recovery stories
- study tips
- buddy matching suggestions based on academic context

#### 12.9 Counselor Dashboard

The counselor dashboard is intentionally limited to anonymized, aggregate analytics. It avoids exposing private journals or personally sensitive emotional text.

### 13. Database Design

The project uses the following key tables:

#### 13.1 `user_profiles`

Stores student identity and preferences.

#### 13.2 `mood_logs`

Stores daily check-in records and AI analysis output.

#### 13.3 `alert_events`

Stores risk alerts and contact escalation metadata.

#### 13.4 `peer_posts`

Stores anonymous peer community messages.

### 14. Algorithmic Flow

The working flow of the system is:

1. Student enters daily wellness data.
2. Optional journal text is cleaned and analyzed.
3. Sentiment and emotion signals are extracted.
4. Numeric and text-based features are combined.
5. Risk engine computes score and prediction label.
6. Recommendation engine generates personalized next steps.
7. Dashboard updates metrics, trends, and forecast.
8. If risk is high and consent exists, alert metadata is generated.

### 15. Implementation Highlights

The project is implemented as a clean monorepo with separated frontend, backend, services, shared configuration, scripts, and tests. This improves maintainability and makes the project look production-oriented rather than script-based.

Important implementation highlights:

- encrypted journal note storage using `cryptography`
- hashed login and role-based access for student and counselor views
- modular Flask API endpoints
- real email and SMS alert integration through Resend and Twilio
- shared gateway for local or API-based execution
- Render deployment configuration
- seeded demo cohort for realistic dashboard visuals
- test scaffolding for platform and API validation

### 16. Security, Privacy, and Ethics

This project includes a clear ethics layer because mental health applications must be designed responsibly.

Privacy and ethics measures:

- journal notes are encrypted before storage
- anonymous mode is supported
- counselor insights are aggregate-only
- alerting is consent-based
- the application clearly avoids diagnosis claims
- human support is recommended for high-risk patterns

This is a major strength of the project because it demonstrates that AI can be designed with responsibility, user dignity, and safety in mind.

### 17. Testing Strategy

The project includes structured testing for:

- platform-level check-in flow
- dashboard generation
- peer-support helpers
- API route health and dashboard response

Manual testing can also be demonstrated with the following scenarios:

- normal low-stress student input
- exam-stress input
- low sleep and high workload input
- high-risk emotional journal input
- peer post submission
- counselor dashboard review

### 18. Sample Test Cases

| Test Case | Input | Expected Output |
|---|---|---|
| Mood check-in | Good mood, low stress, enough sleep | Normal label and positive suggestions |
| Burnout case | High stress, low energy, low sleep | Stressed or High Risk label |
| Journal analysis | "I feel overwhelmed and exhausted" | Negative sentiment and burnout-related emotion |
| Dashboard trend | Multiple past entries | Mood and stress charts visible |
| Peer support | Anonymous post submission | Message shown on peer wall |
| Admin insights | Multiple student records | Aggregate metrics visible |

### 19. Results and Outcomes

The implemented system successfully demonstrates:

- AI-driven mental wellness support at student-project scale
- effective use of NLP for emotional signal detection
- correlation between academic pressure and wellbeing metrics
- a practical dashboard for self-awareness and institutional insight
- a strong demo story for judging panels because it combines AI, ethics, analytics, and deployment

### 20. Advantages of the Proposed System

- Beginner-friendly technology stack
- Fast to deploy and demo
- Strong social relevance
- Combines multiple AI concepts in one project
- Includes practical and ethical intervention design
- Presentation-friendly with rich visuals and real workflows

### 21. Limitations

- The system depends partly on self-reported data
- The current model is a prototype and not medically validated
- Voice input is not yet integrated
- Real alert delivery depends on configured third-party provider credentials
- SQLite is suitable for demo use but not large-scale production

### 22. Future Enhancements

- voice sentiment and tone analysis
- multilingual translation integration
- Spotify or wellness playlist recommendation
- mobile notification support
- real counselor workflow integration
- larger institution-specific labeled datasets for retraining
- stronger time-series forecasting models

### 23. Conclusion

MindPulse AI is a meaningful and practical final-year project that combines artificial intelligence, data analytics, responsible system design, and student-centered problem solving. The system moves beyond basic sentiment analysis by integrating mood tracking, behavior signals, academic context, personalized intervention, privacy-aware analytics, and deployment readiness.

The project demonstrates technical depth through NLP, machine learning, dashboard visualization, backend modularity, and database design. At the same time, it remains socially useful, ethically grounded, and realistic for academic demonstration. This balance between innovation, usability, and responsibility makes the project highly suitable for final-year evaluation, judging panels, and future extension into a larger student-support platform.

### 24. References

Use these as report references and format them according to your department style.

1. TextBlob Documentation
2. NLTK Documentation
3. scikit-learn Documentation
4. Pandas Documentation
5. Streamlit Documentation
6. Flask Documentation
7. Research articles on student stress, emotional wellbeing, and AI in mental health support
