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

class MindPulsePDF(FPDF):
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
        self.cell(0, 10, f"MindPulse AI - Technical Code Compilation  |  Section: {self.current_section}", border=0, align="R")
        self.ln(6)
        # Horizontal rule
        self.set_draw_color(220, 225, 230)
        self.line(self.get_x(), self.get_y(), 210 - self.get_x(), self.get_y())
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
        self.cell(0, 10, "CONFIDENTIAL - ACADEMIC PROJECT USE ONLY", border=0, align="L")
        
        # Page X of Y
        page_str = f"Page {self.page_no()}/{{nb}}"
        self.set_x(-40)
        self.cell(30, 10, page_str, border=0, align="R")

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

def get_directory_tree(startpath):
    """
    Generates a textual directory tree of the project.
    """
    ignore_dirs = {'.git', '.pytest_cache', '__pycache__', '.venv', 'pytest-cache-files-', 'node_modules', '.gemini', '.agents'}
    lines = []
    
    def _tree(dir_path, prefix=""):
        try:
            items = sorted(os.listdir(dir_path))
        except OSError:
            return
            
        # Filter items
        filtered_items = []
        for item in items:
            # Check prefix ignores for dynamic directories
            if any(item.startswith(ign) for ign in ignore_dirs) or item in ignore_dirs:
                continue
            filtered_items.append(item)
            
        for i, item in enumerate(filtered_items):
            is_last = (i == len(filtered_items) - 1)
            connector = "`-- " if is_last else "|-- "
            path = os.path.join(dir_path, item)
            
            lines.append(f"{prefix}{connector}{item}")
            if os.path.isdir(path):
                new_prefix = prefix + ("    " if is_last else "|   ")
                _tree(path, new_prefix)
                
    lines.append("student-wellness-system (Project Root)")
    _tree(startpath)
    return "\n".join(lines)

def build_pdf():
    print("Gathering files to document...")
    
    categories = {
        "Backend Core Modules": [
            "backend/app_platform.py",
            "backend/database.py",
            "backend/wsgi.py",
            "backend/__init__.py",
        ],
        "Backend API Routing": [
            "backend/api/routes.py",
            "backend/api/__init__.py",
        ],
        "Backend Models": [
            "backend/models/payloads.py",
            "backend/models/__init__.py",
        ],
        "Backend Business Logic & Services": [
            "backend/services/accounts.py",
            "backend/services/alerts.py",
            "backend/services/analytics.py",
            "backend/services/assistant.py",
            "backend/services/nlp_engine.py",
            "backend/services/peer_support.py",
            "backend/services/recommendations.py",
            "backend/services/resources.py",
            "backend/services/risk_engine.py",
            "backend/services/security.py",
            "backend/services/__init__.py",
        ],
        "Frontend Application": [
            "frontend/Home.py",
            "frontend/ui.py",
            "frontend/__init__.py",
            "frontend/pages/1_Daily_Check_In.py",
            "frontend/pages/2_Mood_Dashboard.py",
            "frontend/pages/3_AI_Support_Companion.py",
            "frontend/pages/4_Resource_Hub.py",
            "frontend/pages/5_Peer_Support.py",
            "frontend/pages/6_Counselor_Insights.py",
        ],
        "Shared Code": [
            "shared/config.py",
            "shared/gateway.py",
            "shared/__init__.py",
        ],
        "Scripts & Runners": [
            "scripts/bootstrap_data.py",
            "scripts/__init__.py",
            "bootstrap_data.py",
            "run_app.py",
        ],
        "Unit & Integration Tests": [
            "tests/conftest.py",
            "tests/test_api.py",
            "tests/test_assistant_response.py",
            "tests/test_auth_alerts.py",
            "tests/test_platform.py",
        ]
    }

    pdf = MindPulsePDF()
    
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
    pdf.cell(0, 10, "Technical Module Code Compilation & Reference Guide", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Body Area of Cover Page
    pdf.set_text_color(30, 41, 59)
    pdf.set_y(95)
    
    # Project Info Table/Box
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Project Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    
    description_text = (
        "MindPulse AI is a support system that allows students to check in daily, track "
        "their academic stress signals (attendance, assignments, exams), perform NLP-based "
        "sentiment analysis, and match with peer support buddies. It features a counselor "
        "dashboard with aggregate and anonymized metrics, and integrates with alert systems "
        "(Resend/Twilio) for high-risk flags. The project is designed with a separate backend API "
        "(Flask) and a frontend web application (Streamlit)."
    )
    pdf.multi_cell(0, 5, description_text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_draw_color(200, 210, 220)
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(10, 140, 190, 80, 'DF')
    
    pdf.set_y(145)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Document Metadata", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(15)
    pdf.cell(50, 6, "Platform Version:", border=0)
    pdf.cell(0, 6, "v1.1 (Production/Demo ready)", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_x(15)
    pdf.cell(50, 6, "Generated Date:", border=0)
    pdf.cell(0, 6, datetime.datetime.now().strftime("%B %d, %Y"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_x(15)
    pdf.cell(50, 6, "Total Sections:", border=0)
    pdf.cell(0, 6, f"{len(categories)} Modules", new_x="LMARGIN", new_y="NEXT")
    
    # Calculate file numbers and lines
    total_files = sum(len(files) for files in categories.values())
    pdf.set_x(15)
    pdf.cell(50, 6, "Total Source Files:", border=0)
    pdf.cell(0, 6, f"{total_files} modules", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_x(15)
    pdf.cell(50, 6, "Core Tech Stack:", border=0)
    pdf.cell(0, 6, "Python 3, Streamlit, Flask, SQLite, Scikit-learn, NLP (VADER/TextBlob)", new_x="LMARGIN", new_y="NEXT")
    
    # --- 2. ARCHITECTURE & TREE PAGE ---
    pdf.current_section = "Project Structure"
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Project Architecture & Directory Structure", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 10)
    structure_info = (
        "The project is organized in a modular structure separating the frontend user interface, "
        "the backend service layer, shared settings, and verification tests. "
        "Below is the complete directory structure of the repository:"
    )
    pdf.multi_cell(0, 5, structure_info, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Directory Tree Box
    pdf.set_font("Courier", "", 8)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    
    tree_text = get_directory_tree(os.getcwd())
    
    # Split tree into pages if it is too long, or render in a box
    # Multi_cell handles page breaks automatically inside FPDF2
    pdf.multi_cell(0, 4.5, clean_text(tree_text), border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    
    # --- 3. SECTIONS AND SOURCE CODE ---
    for section_name, file_list in categories.items():
        print(f"Processing section: {section_name}...")
        pdf.current_section = section_name
        pdf.add_page()
        
        # Section Intro Header Page
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(26, 54, 93)
        pdf.cell(0, 20, section_name.upper(), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_draw_color(26, 54, 93)
        pdf.line(50, pdf.get_y(), 160, pdf.get_y())
        pdf.ln(15)
        
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(0, 10, f"This section compiles the modules under {section_name}. Included files:", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        
        # List of files in this section
        for filepath in file_list:
            if os.path.exists(filepath):
                size_kb = os.path.getsize(filepath) / 1024.0
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(10, 6, "- ")
                pdf.set_font("Courier", "B", 10)
                pdf.cell(100, 6, filepath)
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(0, 6, f"({size_kb:.2f} KB)", new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.set_font("Helvetica", "I", 9)
                pdf.cell(0, 6, f"- {filepath} (File missing/not found in workspace)", new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(10)
        
        # Loop over each file and output its content
        for filepath in file_list:
            if not os.path.exists(filepath):
                continue
                
            pdf.add_page()
            
            # File title bar
            pdf.set_fill_color(226, 232, 240)
            pdf.set_draw_color(148, 163, 184)
            pdf.rect(10, pdf.get_y(), 190, 12, 'DF')
            
            pdf.set_font("Courier", "B", 11)
            pdf.set_text_color(15, 23, 42)
            pdf.set_y(pdf.get_y() + 2)
            pdf.cell(0, 8, f" File: {filepath}", align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(6)
            
            # File Metadata info
            size_kb = os.path.getsize(filepath) / 1024.0
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            line_count = len(lines)
            
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(71, 85, 105)
            pdf.cell(0, 6, f"File Size: {size_kb:.2f} KB  |  Total Lines: {line_count}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            # Display source code
            pdf.set_font("Courier", "", 7.5)
            pdf.set_text_color(30, 41, 59)
            
            # Print lines of code
            for idx, line in enumerate(lines, 1):
                # Replace tab character with spaces
                clean_line = clean_text(line.replace('\t', '    ').rstrip('\r\n'))
                # Prepend line number
                formatted_line = f"{idx:4d} | {clean_line}"
                
                # Check for page overflows and format wrap spacing
                pdf.multi_cell(0, 3.8, formatted_line, border=0, new_x="LMARGIN", new_y="NEXT")

    # Output PDF file
    output_filename = "MindPulse_AI_Code_Modules.pdf"
    pdf.output(output_filename)
    print(f"Success! PDF generated successfully: {output_filename}")
    return output_filename

if __name__ == "__main__":
    build_pdf()
