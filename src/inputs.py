import fitz
import re

from src import config

def get_jd(jd_path=config.jd_path):
    with open(jd_path, "r") as f:
        return f.read()

def get_resume(resume_path):
    doc = fitz.open(resume_path)
    html_content = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        page_html = page.get_text("text", sort=True)
        page_html = page_html.replace('\xa0', ' ')
        page_html = re.sub(r' {3,}', '\n', page_html)
        page_html = re.sub(r'\n+', '\n', page_html)

        html_content += f"\n"
        html_content += page_html
        html_content += "\n\n"

    return html_content


def get_cover_letter(cover_letter_path):
    """Extract text from a cover letter PDF using PyMuPDF."""
    if not cover_letter_path:
        return ""

    doc = fitz.open(cover_letter_path)
    text_parts = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text("text", sort=True)
        page_text = page_text.replace('\xa0', ' ')
        text_parts.append(page_text)

    doc.close()
    return "\n\n".join(text_parts).strip()


