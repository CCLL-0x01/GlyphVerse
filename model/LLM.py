from .LLM_api import GPT
from config import config
import json

def knowledge_acquisition(char):
    response = GPT(config["model"]["llm_prompt"] % char)
    response = response.replace('```json', '').replace('```', '')
    return json.loads(response)
