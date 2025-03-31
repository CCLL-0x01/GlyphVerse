import os
from pathlib import Path
from typing import List
from config import config

def get_lora_files() -> List[str]:
    valid_extensions=config["lora"]["ext"]
    matched_files = []
    base_path = Path(config["lora"]["path"])
    
    for entry in base_path.iterdir():
        if not entry.is_file():
            continue  
        suffix = entry.suffix.lower() 
        if suffix not in valid_extensions:
            continue
        matched_files.append(entry.name)
    
    return sorted(matched_files, key=lambda x: os.path.basename(x))