import os

from src import config

def get_jd(jd_path=config.jd_path):
    try:
        with open(jd_path, "r") as f:
            file = f.read()
        return file
    except Exception as e:
        return f"Exception: {e}"