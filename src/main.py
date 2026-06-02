import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from src.config import settings

app = FastAPI(title="PromptShield Core Engine", version="1.0.0")

# Initialize a reusable, global async HTTP client for fast connection pooling
async_client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up the client connections when the server stops
    await async_client.aclose()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "proxy": "PromptShield Engine Active"}

@app.post("/v1/chat/completions")
async def proxy_llm_request(request: Request):
    """
    Core Interception Route: Mimics standard OpenAI/Gemini endpoint format.
    Intercepts incoming JSON prompt payloads and forwards them to the AI Provider.
    """
    try:
        # 1. Parse the incoming JSON body from the client app
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload structure.")

    # 2. Check for an active API Key setup (Defaulting to Gemini for local testing)
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Target AI provider API key is missing. Please set GEMINI_API_KEY in your terminal environment."
        )

    # Construct headers to securely authorize with the target provider
    target_headers = {
        "Authorization": f"Bearer {settings.GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }

    # 3. Asynchronously forward the exact payload to the live provider endpoint
    target_url = f"{settings.DEFAULT_PROVIDER_URL}/chat/completions"
    
    try:
        response = await async_client.post(
            target_url,
            json=body,
            headers=target_headers,
            timeout=30.0  # Safe timeout boundary for heavy prompts
        )
        
        # 4. Return the exact response status and payload seamlessly back to the app
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
        
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, 
            detail=f"Error communicating with upstream AI provider gateway: {str(exc)}"
        )