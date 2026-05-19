import fitz
import re

from src import config

def get_jd(jd_path=config.jd_path):
    try:
        with open(jd_path, "r") as f:
            file = f.read()
        return file
    except Exception as e:
        return f"Exception: {e}"

def get_resume(resume_path):
    doc = fitz.open(resume_path)
    html_content = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Keep the correct reading order
        page_html = page.get_text("text", sort=True)
        # --- CLEANING LAYER ---
        # 1. Replace all non-breaking spaces (\xa0) with standard spaces
        page_html = page_html.replace('\xa0', ' ')
        # 2. Collapse any sequence of 3 or more consecutive spaces down to a single newline or clean tab
        page_html = re.sub(r' {3,}', '\n', page_html)
        # 3. Clean up any accidental double-newlines created by the step above
        page_html = re.sub(r'\n+', '\n', page_html)
        # ----------------------

        html_content += f"\n"
        html_content += page_html
        html_content += "\n\n"

    return html_content


