import httpx
import importlib
import pkgutil
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.config import settings
from src.database import init_db, log_request, get_recent_logs, get_db_metrics
import plugins
from plugins.base import BasePlugin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database
    init_db()
    print("[Database] Database initialized successfully.")
    yield
    # Close client
    await async_client.aclose()

app = FastAPI(title="PromptShield Core Engine", version="1.0.0", lifespan=lifespan)
async_client = httpx.AsyncClient()

def load_security_plugins():
    """
    Dynamically scans the plugins folder and instantiates any subclasses of BasePlugin.
    This fulfills the modular plugin drop-in architecture claim!
    """
    loaded_plugins = []
    plugins_path = plugins.__path__
    for _, module_name, _ in pkgutil.iter_modules(plugins_path):
        if module_name in ["base", "__init__"]:
            continue
        try:
            module = importlib.import_module(f"plugins.{module_name}")
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    # Instantiate plugin (falls back to defaults if needed)
                    instance = obj()
                    loaded_plugins.append(instance)
                    print(f"[Shield] Successfully loaded plugin: {instance.name}")
        except Exception as e:
            print(f"[Warning] Error loading plugin {module_name}: {e}")
            
    # Ensure RateLimiterPlugin runs first if present to protect LLM budget first
    loaded_plugins.sort(key=lambda p: 0 if "RateLimiter" in p.__class__.__name__ else 1)
    return loaded_plugins

# Load active security shields dynamically
security_pipeline = load_security_plugins()

# Mount dashboard static directory
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

@app.get("/", response_class=HTMLResponse)
async def root_home():
    """
    Renders a professional local welcome page when accessed via a browser.
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
                <a href="/dashboard">📊 Live Dashboard</a>
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

@app.get("/api/metrics")
async def get_live_metrics():
    """
    Exposes dynamically computed metrics data stream from our SQLite database.
    """
    return get_db_metrics()

@app.get("/api/logs")
async def get_logs_endpoint(limit: int = 50):
    """
    Exposes recent logged request entries from our SQLite database.
    """
    return get_recent_logs(limit)

@app.post("/v1/chat/completions")
async def proxy_llm_request(request: Request):
    try:
        body = await request.json()
    except Exception:
        log_request(endpoint="/v1/chat/completions", status_code=400, message="Invalid JSON payload structure.")
        raise HTTPException(status_code=400, detail="Invalid JSON payload structure.")

    # --- 🛡️ RUN PROMPT THROUGH THE SECURITY PIPELINE 🛡️ ---
    plugin_triggered = None
    mitigation_msg = None
    sanitized = False
    
    try:
        messages = body.get("messages", [])
        if messages:
            # Grab the text from the latest message
            original_prompt = messages[-1].get("content", "")
            
            # Run the prompt text sequentially through every dynamically loaded plugin shield
            current_prompt = original_prompt
            for plugin in security_pipeline:
                result = plugin.inspect(current_prompt)
                
                # If any plugin flags the prompt as unsafe, block the entire request immediately!
                if not result["safe"]:
                    plugin_triggered = plugin.name
                    mitigation_msg = result["reason"]
                    
                    # Log blocked malicious events
                    log_request(
                        endpoint="/v1/chat/completions", 
                        status_code=403, 
                        plugin_triggered=plugin_triggered, 
                        message=mitigation_msg
                    )
                    
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
            
            # Check if data was mutated/redacted by the PII masker or other plugin
            if current_prompt != original_prompt:
                sanitized = True
                plugin_triggered = "Regex PII Masker"
                mitigation_msg = "Passed: PII entities redacted dynamically."

            # Inject the sanitized prompt back into the request payload
            body["messages"][-1]["content"] = current_prompt
    except Exception as e:
        log_request(endpoint="/v1/chat/completions", status_code=500, message=f"Internal Firewall Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Firewall Processing Error: {str(e)}")
    # -----------------------------------------------------

    # --- 🔀 DYNAMIC PROVIDER ROUTING ENGINE 🔀 ---
    model = body.get("model", "")
    client_auth = request.headers.get("Authorization")
    
    if model.startswith(("gpt-", "o1-", "text-davinci-", "dall-e")):
        # Route to OpenAI
        target_url = "https://api.openai.com/v1/chat/completions"
        auth_key = settings.OPENAI_API_KEY or (client_auth.replace("Bearer ", "") if client_auth else "")
        if not auth_key:
            log_request(endpoint="/v1/chat/completions", status_code=400, message="OpenAI API key missing.")
            raise HTTPException(status_code=400, detail="OpenAI API key is required but missing.")
        target_headers = {
            "Authorization": f"Bearer {auth_key}",
            "Content-Type": "application/json"
        }
    elif model.startswith("gemini-"):
        # Route to Google Gemini (OpenAI compatible endpoint)
        target_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        auth_key = settings.GEMINI_API_KEY or (client_auth.replace("Bearer ", "") if client_auth else "")
        if not auth_key:
            log_request(endpoint="/v1/chat/completions", status_code=400, message="Gemini API key missing.")
            raise HTTPException(status_code=400, detail="Gemini API key is required but missing.")
        target_headers = {
            "Authorization": f"Bearer {auth_key}",
            "Content-Type": "application/json"
        }
    else:
        # Fallback to configuration default provider URL
        target_url = f"{settings.DEFAULT_PROVIDER_URL}/chat/completions"
        if client_auth:
            target_headers = {
                "Authorization": client_auth,
                "Content-Type": "application/json"
            }
        else:
            if not settings.GEMINI_API_KEY:
                log_request(endpoint="/v1/chat/completions", status_code=500, message="Default API provider key missing.")
                raise HTTPException(status_code=500, detail="Target AI provider API key is missing.")
            target_headers = {
                "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
                "Content-Type": "application/json"
            }
    # ---------------------------------------------

    # Forward the sanitized body to the real provider
    try:
        response = await async_client.post(
            target_url,
            json=body,
            headers=target_headers,
            timeout=30.0
        )
        
        # Log successful pass-through or upstream errors
        final_plugin = plugin_triggered if plugin_triggered else "Clean Forward Pass"
        final_msg = mitigation_msg if mitigation_msg else "Forwarded: Safe structural context parameters matched."
        if response.status_code != 200:
            final_plugin = "Upstream Route Error"
            final_msg = f"Upstream provider returned status {response.status_code}"
            
        log_request(
            endpoint="/v1/chat/completions",
            status_code=response.status_code,
            plugin_triggered=final_plugin,
            message=final_msg
        )
        
        return JSONResponse(status_code=response.status_code, content=response.json())
    except httpx.HTTPError as exc:
        log_request(endpoint="/v1/chat/completions", status_code=502, message=f"Upstream provider error: {str(exc)}")
        raise HTTPException(status_code=502, detail=f"Upstream provider communication error: {str(exc)}")