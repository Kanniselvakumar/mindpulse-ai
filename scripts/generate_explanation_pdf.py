import os
import sys
import subprocess
import datetime

# Ensure fpdf2 is installed
try:
    from fpdf import FPDF
except ImportError:
    print("fpdf2 library not found. Installing now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2"])
    from fpdf import FPDF

class MindPulseExplanationPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.current_section = ""
        self.set_auto_page_break(auto=True, margin=15)
        self.alias_nb_pages()

    def header(self):
        if self.page_no() == 1:
            return  # No header on cover page
            
        # Draw header top line and text
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 110, 120)
        self.cell(0, 10, f"MindPulse AI - Module Explanations  |  Section: {self.current_section}", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        # Horizontal rule
        self.set_draw_color(220, 225, 230)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            return  # No footer on cover page
            
        self.set_y(-15)
        # Horizontal rule above footer
        self.set_draw_color(220, 225, 230)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, "MINDPULSE AI - SYSTEM ARCHITECTURE DOCUMENTATION", border=0, align="L")
        
        # Page X of Y
        page_str = f"Page {self.page_no()}/{{nb}}"
        self.set_x(-40)
        self.cell(30, 10, page_str, border=0, align="R", new_x="LMARGIN", new_y="NEXT")

def clean_text(text):
    """
    Cleans text to be compatible with PDF standard Latin-1 encoding.
    Replaces common unicode symbols and removes/escapes others.
    """
    replacements = {
        '\u2013': '-', # en dash
        '\u2014': '-', # em dash
        '\u2018': "'", # left single quote
        '\u2019': "'", # right single quote
        '\u201c': '"', # left double quote
        '\u201d': '"', # right double quote
        '\u2022': '*', # bullet
        '\u2026': '...', # ellipsis
        '\xa0': ' ',     # non-breaking space
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    
    # Strip any emoji or non-latin-1 char by keeping ord < 256
    return "".join(c if ord(c) < 256 else '?' for c in text)

def add_heading1(pdf, text):
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(26, 54, 93) # Deep Blue
    pdf.cell(0, 10, clean_text(text), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(26, 54, 93)
    pdf.line(pdf.get_x(), pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

def add_heading2(pdf, text):
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 41, 55) # Dark Gray
    pdf.cell(0, 8, clean_text(text), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

def add_paragraph(pdf, text):
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(51, 65, 85) # Slate Gray
    pdf.multi_cell(0, 5, clean_text(text), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2.5)

def add_bullet(pdf, text):
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(51, 65, 85)
    pdf.set_x(15)
    pdf.cell(5, 5, "* ")
    pdf.multi_cell(0, 5, clean_text(text), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(10) # Reset margin
    pdf.ln(1.5)

def add_file_card(pdf, filepath, purpose, details=""):
    pdf.ln(2)
    pdf.set_fill_color(248, 250, 252) # Soft Gray
    pdf.set_draw_color(226, 232, 240)
    
    # Render border and text block
    content = f"File: {filepath}\nPurpose: {purpose}"
    if details:
        content += f"\nDetails: {details}"
        
    pdf.set_font("Courier", "B", 9)
    pdf.set_text_color(26, 54, 93)
    pdf.multi_cell(0, 4.5, clean_text(content), border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

def build_pdf():
    print("Generating MindPulse AI Module Explanations PDF...")
    pdf = MindPulseExplanationPDF()
    
    # --- 1. COVER PAGE ---
    pdf.add_page()
    
    # Visual banner background
    pdf.set_fill_color(26, 54, 93) # Deep Blue
    pdf.rect(0, 0, 210, 85, 'F')
    
    # Title in banner
    pdf.set_y(25)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "MINDPULSE AI", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(226, 232, 240)
    pdf.cell(0, 10, "Student Mental Health Support & Analytics Platform", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(0, 10, "System Architecture & Detailed Module Explanations", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Body Area of Cover Page
    pdf.set_text_color(30, 41, 59)
    pdf.set_y(95)
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "About This Document", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    
    doc_desc = (
        "This document provides a complete technical analysis and explanation of all code modules "
        "comprising the MindPulse AI platform. It is structured to detail the architecture, "
        "database designs, backend API endpoints, analytical algorithms, machine learning risk engine, "
        "anonymous peer wall support system, and interactive Streamlit frontend layout. Emojis and "
        "source code references are detailed contextually."
    )
    pdf.multi_cell(0, 5, doc_desc, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    
    # Metadata Box
    pdf.set_draw_color(200, 210, 220)
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(10, 140, 190, 80, 'DF')
    
    pdf.set_y(145)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Document Metadata", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(15)
    pdf.cell(50, 6, "System Version:", border=0)
    pdf.cell(0, 6, "v1.1 (Production/Demo ready)", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_x(15)
    pdf.cell(50, 6, "Generated Date:", border=0)
    pdf.cell(0, 6, datetime.datetime.now().strftime("%B %d, %Y"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_x(15)
    pdf.cell(50, 6, "Architecture Type:", border=0)
    pdf.cell(0, 6, "Separated Monorepo (Flask Backend API + Streamlit Frontend UI)", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_x(15)
    pdf.cell(50, 6, "Database Engine:", border=0)
    pdf.cell(0, 6, "SQLite 3", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_x(15)
    pdf.cell(50, 6, "Tech Stack Layers:", border=0)
    pdf.cell(0, 6, "Python 3, Streamlit, Flask, SQLite, Scikit-learn, TextBlob, Plotly", new_x="LMARGIN", new_y="NEXT")

    # --- 2. ARCHITECTURE OVERVIEW ---
    pdf.current_section = "Overview"
    pdf.add_page()
    
    add_heading1(pdf, "1. Architecture Overview & Design Intent")
    
    add_paragraph(pdf, 
        "MindPulse AI is designed to serve as an ethical, privacy-conscious student wellbeing "
        "support tool. It correlates behavioral patterns (attendance, assignment loads, social connectivity, "
        "sleep, exam pressure) with mood trends to detect early warning signs of stress or mental health struggles."
    )
    
    add_heading2(pdf, "System Components Diagram")
    add_paragraph(pdf, 
        "+-------------------------------------------------------------------------+\n"
        "|                         Streamlit Frontend Web App                      |\n"
        "|   (Mood Log Form, Charts, Multilingual AI Chat, Counselor Aggregate)    |\n"
        "+-------------------------------------------------------------------------+\n"
        "                                     | (JSON REST API)\n"
        "                                     v\n"
        "+-------------------------------------------------------------------------+\n"
        "|                           Flask API Gateway Server                      |\n"
        "|   (User Authentication, Request Validation, Endpoint Route Handlers)    |\n"
        "+-------------------------------------------------------------------------+\n"
        "                                     | (Python Class Calls)\n"
        "                                     v\n"
        "+-------------------------------------------------------------------------+\n"
        "|                           Business Logic & Services                     |\n"
        "|   * NLP Engine: Sentiment Polarity & Keyword-based Emotion Extraction    |\n"
        "|   * ML Risk Engine: Logistic Regression vs Random Forest Classifiers    |\n"
        "|   * AI Assistant: Preserves context, handles English, Hindi, Tamil      |\n"
        "|   * Escalation Service: Twilio SMS API & Resend Email Client            |\n"
        "+-------------------------------------------------------------------------+\n"
        "                                     | (SQL Queries)\n"
        "                                     v\n"
        "+-------------------------------------------------------------------------+\n"
        "|                           SQLite 3 Storage Layer                        |\n"
        "|   (Stores Users, Profiles, Daily logs, Alert Logs, Peer Encouragements) |\n"
        "+-------------------------------------------------------------------------+"
    )
    
    add_paragraph(pdf, 
        "Separating the user interface (Streamlit) from the database and business logic (Flask API) "
        "ensures the app is robust, clean, and extensible. It allows counselors to access aggregate "
        "data via APIs without direct read permissions to individual database tables, protecting privacy."
    )

    # --- 3. DATABASE LAYER ---
    pdf.current_section = "Database Layer"
    pdf.add_page()
    
    add_heading1(pdf, "2. Database Layer & Data Bootstrapping")
    
    add_paragraph(pdf,
        "The project uses SQLite 3 for database storage due to its lightweight footprint, "
        "making it ideal for academic projects, developer environments, and lightweight web service deployments. "
        "The database is structured to securely store passwords, daily mood logs, alert logs, and peer wall entries."
    )
    
    add_heading2(pdf, "Database Schema Tables")
    add_bullet(pdf, "users: Stores account credentials. Passwords are encrypted using cryptographically secure hashing (bcrypt or pbkdf2 with SHA256).")
    add_bullet(pdf, "profiles: Stores student profile settings, including name, department, year, preferred language, anonymous status, and trusted contact details for alerts.")
    add_bullet(pdf, "checkins: Logs daily student check-ins containing numerical metrics (mood_score, stress, energy, sleep, attendance, assignments, social, exam_pressure), NLP sentiments, and encrypted journal text.")
    add_bullet(pdf, "alerts: Logs alert events (counselor triggers, trusted contact email/SMS dispatches) to maintain an audit trail of mental health escalations.")
    add_bullet(pdf, "peer_posts: Logs anonymous posts, encouragement messages, and peer recovery stories posted to the community wall.")
    add_bullet(pdf, "buddy_matches: Records pairs of students recommended for study pairings based on shared academic context and mutual buddy matching preferences.")
    
    add_heading2(pdf, "Database Files & Utilities")
    
    add_file_card(pdf, 
        "backend/database.py",
        "Initializes and manages the SQLite database connections and table schemas.",
        "Defines standard context managers to connect, query, and close database handles safely. "
        "Contains DDL scripts to create database tables (users, profiles, checkins, alerts, peer_posts, etc.)."
    )
    
    add_file_card(pdf, 
        "backend/data/seed.py",
        "Seeds simulated database records to demonstrate system features.",
        "Generates initial dummy accounts (including student and counselor profiles) and sets up mock student check-in history to render analytical patterns on dashboards immediately."
    )
    
    add_file_card(pdf, 
        "scripts/bootstrap_data.py",
        "A command-line script to initialize the project database.",
        "Can be run via 'python scripts/bootstrap_data.py' to wipe out old DB records, create fresh tables, and execute seed.py for initial demo usage."
    )

    # --- 4. BACKEND API & ROUTING ---
    pdf.current_section = "Backend Core"
    pdf.add_page()
    
    add_heading1(pdf, "3. Backend API Platform & Routing Gateway")
    
    add_paragraph(pdf,
        "The backend API acts as the core handler of student data, running on Flask. All frontend "
        "operations perform HTTP requests to access or modify resources, enforcing security, validation, and role-based permissions."
    )
    
    add_heading2(pdf, "Core Backend Modules")
    
    add_file_card(pdf,
        "backend/app_platform.py",
        "Configures the Flask API instance and error handling middleware.",
        "Handles JSON serialization, CORS configs (allowing frontend Streamlit communication), "
        "environment variables configuration, and request logging. Also runs the local development port binding."
    )
    
    add_file_card(pdf,
        "backend/api/routes.py",
        "Defines all REST API endpoints used by the Streamlit application.",
        "Maps URL patterns to service methods. Key routes handle login/register, check-ins, user dashboard graphs, counselor summaries, peer support, Twilio/Resend alerts, and AI companion inputs."
    )

    add_file_card(pdf,
        "shared/gateway.py",
        "Maintains API routing configurations and base gateway routes.",
        "Manages request routing to ensure the local frontend knows whether it is interacting with a local Flask service, a mock service, or a remote production backend on Render."
    )
    
    add_heading2(pdf, "Key REST API Endpoints")
    add_bullet(pdf, "POST /api/auth/register - Registers new users (hashes password).")
    add_bullet(pdf, "POST /api/auth/login - Validates login, sets session context and user roles.")
    add_bullet(pdf, "POST /api/checkins - Submits daily emoji check-in data, processes NLP scores, and saves logs.")
    add_bullet(pdf, "GET /api/dashboard/<user_id> - Aggregates daily logs for visualization on the student's dashboard.")
    add_bullet(pdf, "GET /api/admin/overview - Returns aggregated, anonymized student statistics strictly for counselors.")
    add_bullet(pdf, "POST /api/assistant - Forwards journal prompts to the AI chatbot to fetch supportive guidance.")

    # --- 5. SERVICES LAYER ---
    pdf.current_section = "Backend Services"
    pdf.add_page()
    
    add_heading1(pdf, "4. Business Logic & Support Services")
    
    add_paragraph(pdf,
        "The services folder contains the computational core of MindPulse AI. This layer performs "
        "Natural Language Processing on text, runs Machine Learning algorithms for risk analysis, "
        "orchestrates the conversational companion, and interfaces with communication APIs."
    )
    
    add_heading2(pdf, "NLP Sentiment & Emotion Engine")
    add_file_card(pdf,
        "backend/services/nlp_engine.py",
        "Extracts emotional metrics and sentiment ratings from the user's journal notes.",
        "Uses TextBlob to measure polarity (-1.0 to 1.0) and subjectivity (0.0 to 1.0). "
        "Implements a VADER-style rule matrix to compute compound sentiment scores. "
        "Extracts keyword-based emotions (e.g. Joy, Sadness, Anger, Fear, Anxiety) by cross-referencing text against emotional word banks."
    )
    
    add_heading2(pdf, "Supervised ML Risk Engine")
    add_paragraph(pdf,
        "MindPulse AI classifies students' wellness risk into Normal, Stressed, and High Risk. "
        "Unlike basic apps using fixed rules, this system uses supervised Machine Learning."
    )
    add_bullet(pdf, "Dataset: Trained on 1,800 simulated student wellness profiles to ensure data transparency.")
    add_bullet(pdf, "Features: Uses 9 dimensions (mood score, stress levels, sleep hours, attendance, assignments, NLP compound sentiment, social connectedness, energy, and exam pressure).")
    add_bullet(pdf, "Supervised Classifier Comparison: Compares a Logistic Regression model (serving as a linear baseline) and a Random Forest Classifier (serving as a non-linear, high-accuracy ensemble model).")
    add_bullet(pdf, "Model Selection: Automatically calculates accuracy, precision, recall, and macro-F1 score on test splits, deploying the model with the highest F1 score.")
    
    add_file_card(pdf,
        "backend/services/risk_engine.py",
        "Orchestrates dataset creation, model preprocessing, training, comparison, and inference.",
        "Splits data into an 80/20 train-test ratio, runs MinMaxScaler preprocessing, compares LogisticRegression and RandomForestClassifier, and saves/restores the best model for live check-in scoring."
    )

    pdf.add_page() # New page for remaining services
    add_heading2(pdf, "Multilingual AI Support Companion")
    add_paragraph(pdf,
        "The AI companion provides conversational support using LLM prompting. "
        "It acts as a wellness partner rather than a diagnostic tool, adhering to ethical boundaries."
    )
    add_bullet(pdf, "Multilingual Capability: Supports prompt and response styling in English, Hindi, and Tamil.")
    add_bullet(pdf, "Ethical Guardrails: Explicitly instructed to avoid clinical diagnoses, suggest real-world campus counselors for heavy topics, and provide positive coping habits.")
    add_bullet(pdf, "Context Preservation: Stores chat history context in the SQLite checkins journal thread to preserve conversational flow across interactions.")
    
    add_file_card(pdf,
        "backend/services/assistant.py",
        "Configures AI system prompts, structures multilingual prompts, and handles chatbot responses.",
        "Interfaces with external generative API nodes using configured API keys and formats user inputs into appropriate, safety-filtered responses."
    )
    
    add_heading2(pdf, "Escalation & Live Notification Alerts")
    add_paragraph(pdf,
        "When the risk engine classifies a student as 'High Risk', the system triggers an escalation warning. "
        "If the student has saved contact details and enabled alert permissions, notifications are sent immediately."
    )
    add_bullet(pdf, "Email Alerts via Resend: Connects to the Resend API to deliver mental health alert emails to a trusted mentor or campus counselor.")
    add_bullet(pdf, "SMS Alerts via Twilio: Interfaces with the Twilio SMS Gateway to dispatch real-time emergency alert texts.")
    
    add_file_card(pdf,
        "backend/services/alerts.py",
        "Validates consent preferences and delivers email/SMS alerts using external communication APIs.",
        "Checks profile flags (ALERT_REAL_DELIVERY_ENABLED) and executes HTTP API requests to Twilio and Resend when high-risk scenarios are detected."
    )

    # --- 6. FRONTEND APPLICATION ---
    pdf.current_section = "Frontend Web App"
    pdf.add_page()
    
    add_heading1(pdf, "5. Frontend Web Application (Streamlit)")
    
    add_paragraph(pdf,
        "The frontend is built using Streamlit, providing an interactive dashboard. "
        "It features dynamic charts, clean metrics boxes, and a mobile-friendly responsive layout."
    )
    
    add_heading2(pdf, "Authentication & Layout Core")
    
    add_file_card(pdf,
        "frontend/Home.py",
        "The main entry point of the Streamlit application.",
        "Renders the login and registration forms. Implements role-aware session routing: "
        "directs students to the check-in and dashboard pages, and counselors to the insights portal."
    )
    
    add_file_card(pdf,
        "frontend/ui.py",
        "Defines the visual design system, custom CSS, and shared layouts.",
        "Implements premium aesthetic adjustments (glassmorphism details, styling classes), "
        "custom CSS styles, emojis grids for the mood selection form, and helper metric boxes."
    )
    
    add_heading2(pdf, "Interactive Pages")
    
    add_file_card(pdf,
        "frontend/pages/1_Daily_Check_In.py",
        "Renders the daily check-in form where students submit emotional indicators.",
        "Includes mood selections, sleep sliders, attendance percentages, and text fields for journals. "
        "Submits inputs to Flask, runs the NLP/ML engines, and displays coping suggestions immediately."
    )
    
    add_file_card(pdf,
        "frontend/pages/2_Mood_Dashboard.py",
        "Renders wellness history graphs using Plotly.",
        "Visualizes mood/stress correlations over time. Features a trend forecaster "
        "which uses simple LinearRegression on the user's past 15 days to forecast potential upcoming low-mood days."
    )
    
    add_file_card(pdf,
        "frontend/pages/3_AI_Support_Companion.py",
        "Renders the interactive chat layout for the AI support partner.",
        "Displays message history and filters input languages based on user settings."
    )

    pdf.add_page()
    add_file_card(pdf,
        "frontend/pages/4_Resource_Hub.py",
        "Lists campus resources, helplines, journal prompts, and coping tools.",
        "Provides phone numbers, location information, and interactive coping tools."
    )
    
    add_file_card(pdf,
        "frontend/pages/5_Peer_Support.py",
        "Renders the community wall and buddy matcher.",
        "Displays anonymous recovery stories and academic buddy matches (pairing students with similar academic loads for mutual support)."
    )
    
    add_file_card(pdf,
        "frontend/pages/6_Counselor_Insights.py",
        "Renders anonymized aggregate metrics for administrative staff.",
        "Displays campus stress distribution metrics and risk counts without exposing private journals."
    )

    # --- 6. NEWLY PROPOSED CORE MODULES ---
    pdf.current_section = "Proposed Modules"
    pdf.add_page()
    add_heading1(pdf, "6. Proposed Core Module Extensions")
    
    add_paragraph(pdf,
        "Based on institutional requirements for comprehensive student support, the following "
        "necessary modules are proposed for inclusion in future system iterations to expand "
        "lifestyle analytics, early warnings, clinical interventions, and systemic insights."
    )
    
    add_file_card(pdf,
        "Sleep & Lifestyle Tracker (Proposed)",
        "Expands sleep logging into a weekly quality/lifestyle analysis panel.",
        "Generates weekly sleep pattern charts using Plotly, calculates cumulative sleep debt, "
        "and correlates sleep quality directly with mood trends. Recommends lifestyle nudges based on sleep patterns."
    )
    
    add_file_card(pdf,
        "Academic Calendar Stress Predictor (Proposed)",
        "Preemptively flags high-stress weeks based on exam/assignment schedules.",
        "Integrates with college schedules, cross-references calendars with current stress trends, "
        "and sends preventative coping tips and reminders to students ahead of time."
    )
    
    add_file_card(pdf,
        "Student Progress & Recovery Tracker (Proposed)",
        "Tracks student wellness progress and recovery journey longitudinally.",
        "Visualizes longitudinal wellness metrics, celebrates positive check-in milestones, "
        "and tracks coping plan completion to determine the efficacy of interventions."
    )
    
    add_file_card(pdf,
        "Counselor Appointment Booking Module (Proposed)",
        "Allows direct support session bookings inside the app interface.",
        "Provides booking portals with counselor slot settings. Uses Resend and Twilio "
        "integration to deliver session booking confirmations and SMS/email reminders."
    )
    
    add_file_card(pdf,
        "Group & Cohort Analytics (Proposed)",
        "Aggregates analytics by department or batch for counselor cohort insights.",
        "Draws department-wide and batch-wise stress heatmaps, allowing counselors to identify "
        "systemic issues (e.g. curriculum overload) while strictly preserving student anonymity."
    )

    # --- 7. TESTING SUITE ---
    pdf.current_section = "Testing"
    add_heading1(pdf, "7. Test Suite & Verification")
    
    add_paragraph(pdf,
        "MindPulse AI includes a test suite running on pytest. "
        "This validates API endpoints, risk engine accuracy, and alerting logic to prevent deployment errors."
    )
    
    add_file_card(pdf,
        "tests/conftest.py",
        "Configures shared pytest fixtures and temporary test databases.",
        "Sets up mock Flask clients and temporary SQLite instances to ensure tests run in isolation without modifying live data."
    )
    
    add_file_card(pdf,
        "tests/test_api.py",
        "Validates core API routes, response formats, and status codes.",
        "Tests endpoints such as registration, logging check-ins, dashboard feeds, and buddy matching."
    )
    
    add_file_card(pdf,
        "tests/test_platform.py",
        "Verifies system initialization and server-wide configurations.",
        "Checks environment variable parsing, database migration checks, and server CORS configs."
    )
    
    add_file_card(pdf,
        "tests/test_auth_alerts.py",
        "Validates hashing security, role permissions, and alert triggers.",
        "Ensures password validation works, non-counselors are blocked from the admin portal, "
        "and alert dispatches are triggered correctly for high-risk flags."
    )

    # --- Output PDF file ---
    output_filename = "MindPulse_AI_Module_Explanations.pdf"
    try:
        pdf.output(output_filename)
    except PermissionError:
        output_filename = "MindPulse_AI_Module_Explanations_v2.pdf"
        print(f"Primary file locked. Saving fallback to: {output_filename}")
        pdf.output(output_filename)
    print(f"Success! PDF generated successfully: {output_filename}")
    return output_filename

if __name__ == "__main__":
    build_pdf()
