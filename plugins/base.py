from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """
    The abstract structural blueprint for all PromptShield security plugins.
    Every new guardrail must inherit from this class.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def inspect(self, prompt_text: str) -> dict:
        """
        Inspects the incoming prompt text.
        Returns a dictionary: 
        {
            "safe": True/False,
            "prompt": "Modified or original text",
            "reason": "Why it was blocked (if unsafe)"
        }
        """
        pass