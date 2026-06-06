import re
from plugins.base import BasePlugin

class CredentialLeakDetectorPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="Credential Leak Detector")
        # Detect common API key patterns (e.g., sk-proj-... or AIzaSy...)
        self.secret_patterns = [
        re.compile(r'sk-[a-zA-Z0-9_-]{32,48}'),  # Added _ and - inside the character set
        re.compile(r'AIzaSy[a-zA-Z0-9-_]{33}')
    ]

    def inspect(self, prompt_text: str, context: dict = None) -> dict:
        for pattern in self.secret_patterns:
            if pattern.search(prompt_text):
                return {
                    "safe": False,
                    "prompt": prompt_text,
                    "reason": "Security Violation: Hardcoded API key detected in the prompt payload."
                }
                
        return {
            "safe": True,
            "prompt": prompt_text,
            "reason": ""
        }