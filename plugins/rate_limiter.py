import time
from plugins.base import BasePlugin

class RateLimiterPlugin(BasePlugin):
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        super().__init__(name="Local Rate Limiter")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # In-memory dictionary tracking timestamps per client IP/token
        self.request_history = {}

    def inspect(self, prompt_text: str, context: dict = None) -> dict:
        client_id = "global"
        if context and "client_ip" in context:
            client_id = context["client_ip"]

        current_time = time.time()
        
        # Get history for this client, default to empty list
        history = self.request_history.get(client_id, [])
        
        # Clear out timestamps that are older than our evaluation window
        history = [
            t for t in history 
            if current_time - t < self.window_seconds
        ]
        self.request_history[client_id] = history
        
        # Check if the remaining active count exceeds our maximum safety boundary
        if len(history) >= self.max_requests:
            return {
                "safe": False,
                "prompt": prompt_text,
                "reason": f"Rate Limit Exceeded: Maximum threshold of {self.max_requests} requests per minute breached."
            }
            
        # Log the current valid transaction execution timestamp
        history.append(current_time)
        return {
            "safe": True,
            "prompt": prompt_text,
            "reason": ""
        }