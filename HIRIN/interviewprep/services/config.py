# interviewprep/services/config.py
import os
from pathlib import Path


class APIConfig:
    def __init__(self):
        self.api_key = self._load_api_key()
        self.model = "llama-3.3-70b-versatile"
        self.max_questions = 10
        self.aptitude_questions = 35
        self.aptitude_time = 35 * 60
    
    def _load_api_key(self):
        # Get the absolute path of this file
        current_file = Path(__file__).resolve()
        
        # Try all possible locations
        possible_paths = [
            # From services folder - go to Email folder
            current_file.parent.parent.parent / 'Email' / '.env',
            current_file.parent.parent / 'Email' / '.env',
            current_file.parent / 'Email' / '.env',
            Path.cwd() / 'Email' / '.env',
            Path('.env'),
            Path('../.env'),
            Path('../../.env'),
        ]
        
        for env_path in possible_paths:
            if env_path.exists():
                print(f"✅ Found .env at: {env_path}")
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('GROQ_API_KEY='):
                            key = line.split('=', 1)[1].strip()
                            if key:
                                print(f"✅ API key loaded successfully")
                                return key
        
        print("⚠️ No GROQ_API_KEY found")
        return ""
    
    @property
    def is_available(self):
        return bool(self.api_key) and len(self.api_key) > 10


config = APIConfig()