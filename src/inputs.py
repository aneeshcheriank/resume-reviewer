import os
import fitz

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

        # the "html" content perserve font, colors, and positioning
        page_html = page.get_text()

        html_content = f"<!-- Start of page {page_num + 1} -->\n"
        html_content += page_html
        html_content += "\n<!-- End of page -->\n"

    return html_content


