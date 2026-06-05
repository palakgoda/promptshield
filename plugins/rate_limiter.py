import time
from plugins.base import BasePlugin

class RateLimiterPlugin(BasePlugin):
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        super().__init__(name="Local Rate Limiter")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # In-memory database tracking timestamps for each token/client
        # Storing a simple list of request execution timestamps
        self.request_history = []

    def inspect(self, prompt_text: str) -> dict:
        current_time = time.time()
        
        # Clear out timestamps that are older than our evaluation window
        self.request_history = [
            t for t in self.request_history 
            if current_time - t < self.window_seconds
        ]
        
        # Check if the remaining active count exceeds our maximum safety boundary
        if len(self.request_history) >= self.max_requests:
            return {
                "safe": False,
                "prompt": prompt_text,
                "reason": f"Rate Limit Exceeded: Maximum threshold of {self.max_requests} requests per minute breached."
            }
            
        # Log the current valid transaction execution timestamp
        self.request_history.append(current_time)
        return {
            "safe": True,
            "prompt": prompt_text,
            "reason": ""
        }