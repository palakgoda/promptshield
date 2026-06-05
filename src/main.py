import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from src.config import settings

# Import our active security shields
from plugins.regex_pii_masker import PIMaskerPlugin
from plugins.credential_leak_detector import CredentialLeakDetectorPlugin
from plugins.rate_limiter import RateLimiterPlugin

app = FastAPI(title="PromptShield Core Engine", version="1.0.0")
async_client = httpx.AsyncClient()

# Initialize and cache our security plugin instances
security_pipeline = [
    RateLimiterPlugin(max_requests=5, window_seconds=60), # Protects budget first
    PIMaskerPlugin(),
    CredentialLeakDetectorPlugin()
]

@app.on_event("shutdown")
async def shutdown_event():
    await async_client.aclose()

@app.get("/", response_class=HTMLResponse)
async def root_home():
    """
    Renders a professional local welcome page when accessed via a browser,
    completely fixing the annoying root 404 error!
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PromptShield Gateway Active</title>
        <style>
            body { background-color: #0d1117; color: #58a6ff; font-family: 'Courier New', monospace; padding: 40px; text-align: center; }
            .container { border: 1px solid #30363d; padding: 30px; display: inline-block; border-radius: 6px; background-color: #161b22; box-shadow: 0px 4px 20px rgba(0,0,0,0.5); }
            h1 { color: #2ea44f; margin-bottom: 5px; }
            p { color: #8b949e; margin-bottom: 25px; }
            .status-badge { background-color: rgba(46, 164, 79, 0.15); color: #3fb950; border: 1px solid rgba(46, 164, 79, 0.4); padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 14px; }
            .links { margin-top: 30px; font-size: 14px; }
            .links a { color: #58a6ff; text-decoration: none; margin: 0 15px; }
            .links a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ PromptShield Core</h1>
            <p>Local AI Security Proxy Firewall Gateway</p>
            <div><span class="status-badge">● ONLINE & SECURE</span></div>
            <div class="links">
                <a href="/health" target="_blank">🩺 API Health</a>
                <a href="/docs" target="_blank">📖 Interactive Docs</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "proxy": "PromptShield Firewall Active"}

@app.post("/v1/chat/completions")
async def proxy_llm_request(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload structure.")

    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Target AI provider API key is missing.")

    # --- 🛡️ RUN PROMPT THROUGH THE SECURITY PIPELINE 🛡️ ---
    try:
        messages = body.get("messages", [])
        if messages:
            # Grab the text from the latest message
            original_prompt = messages[-1].get("content", "")
            
            # Run the prompt text sequentially through every loaded plugin shield
            current_prompt = original_prompt
            for plugin in security_pipeline:
                result = plugin.inspect(current_prompt)
                
                # If any plugin flags the prompt as unsafe, block the entire request immediately!
                if not result["safe"]:
                    return JSONResponse(
                        status_code=403,
                        content={
                            "error": "Security Shield Exception",
                            "plugin": plugin.name,
                            "detail": result["reason"]
                        }
                    )
                # Pass down the modified/sanitized text to the next plugin
                current_prompt = result["prompt"]
            
            # Inject the sanitized prompt back into the request payload
            body["messages"][-1]["content"] = current_prompt
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Firewall Processing Error: {str(e)}")
    # -----------------------------------------------------

    # Forward the sanitized body to the real provider
    target_headers = {
        "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    target_url = f"{settings.DEFAULT_PROVIDER_URL}/chat/completions"
    
    try:
        response = await async_client.post(
            target_url,
            json=body,
            headers=target_headers,
            timeout=30.0
        )
        return JSONResponse(status_code=response.status_code, content=response.json())
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream provider communication error: {str(exc)}")