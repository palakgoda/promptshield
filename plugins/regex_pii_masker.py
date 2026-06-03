import re
from plugins.base import BasePlugin

class PIMaskerPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="Regex PII Masker")
        # Regular expressions for standard email and credit card formats
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.card_pattern = re.compile(r'\b(?:\d[ -]*?){13,16}\b')

    def inspect(self, prompt_text: str) -> dict:
        modified_text = prompt_text
        
        # Mask Emails
        modified_text = self.email_pattern.sub("[REDACTED_EMAIL]", modified_text)
        
        # Mask Credit Cards
        modified_text = self.card_pattern.sub("[REDACTED_CARD]", modified_text)
        
        return {
            "safe": True,
            "prompt": modified_text,
            "reason": ""
        }