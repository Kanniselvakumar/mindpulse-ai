# MindPulse AI
## ML Dataset and Preprocessing Note

### Why this note matters

Judges often ask two questions:

- Where did the data come from?
- Where is the actual machine learning?

This project answers both clearly.

### Current Data Source

MindPulse AI trains its deployed risk classifier on a simulated student wellness dataset generated inside the project.

Dataset profile:

- source type: simulated student wellness records
- sample count: 1800
- labels: `Normal`, `Stressed`, `High Risk`
- storage: generated at training time inside the risk engine

### Features Used

The classifier is trained on these features:

- `mood_score`
- `stress_score`
- `energy_score`
- `sleep_hours`
- `attendance_rate`
- `assignments_due`
- `social_connectedness`
- `exam_pressure`
- `compound` sentiment score from NLP

### Label Generation

The project uses a weighted wellness burden score to create three supervised labels:

- `Normal`
- `Stressed`
- `High Risk`

This makes the training process explicit and easy to defend in a college review setting.

### Models Used

MindPulse AI compares two real scikit-learn classifiers:

- `LogisticRegression` as the baseline model
- `RandomForestClassifier` as the nonlinear model

The final deployed model is selected using:

- macro-F1 score
- accuracy

### Preprocessing Flow

1. Generate realistic student wellness records with bounded numeric ranges.
2. Derive labels from the weighted wellness burden score.
3. Split the data using an 80/20 stratified train-test split.
4. Standardize features for Logistic Regression.
5. Train and compare Logistic Regression and Random Forest.
6. Use the better-performing classifier for inference in the app.

### How to Explain This to Judges

Use this short answer:

“The NLP layer uses TextBlob and VADER-style sentiment scoring, but the risk classification is not only rule-based. I trained two supervised scikit-learn models, Logistic Regression and Random Forest, on a simulated student wellness dataset with 1800 labeled records. The deployed model is selected using macro-F1 and accuracy.”

### Optional Future Upgrade

If you want a stronger research-style version later, you can extend the project with:

- public mental health text datasets for richer NLP benchmarking
- anonymized institution-specific student wellness datasets
- manual expert-reviewed labels instead of generated labels
