import os
from langchain_deepseek import ChatDeepSeek

from src.env import config_env

def get_llm():
    config_env()

    return ChatDeepSeek(
        model="deepseek-v4-flash",
        temperature=0.0,
        api_key=os.get("DEEPSEEK"),
        extra_body={"thinking": { # to disable the reasoning (creates problems in formating tool)
            "type": "disabled"
        }} 
    )