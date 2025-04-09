from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import uuid
import os
from datetime import datetime, timedelta

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY",)
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

SYSTEM_PROMPT = """Prompt Especialista:  IA para Análise Jurídica de Pleitos Migratórios
"""

sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

@app.post("/ask-deepseek")
async def ask_deepseek(request: ChatRequest):
    if not request.session_id or request.session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "history": [{"role": "system", "content": SYSTEM_PROMPT}],  # Adiciona prompt inicial
            "last_activity": datetime.now()
        }
    else:
        session_id = request.session_id
        sessions[session_id]["last_activity"] = datetime.now()

    # Adiciona mensagem do usuário ao histórico
    sessions[session_id]["history"].append({"role": "user", "content": request.message})

    response = requests.post(
        DEEPSEEK_API_URL,
        json={
            "model": "deepseek-chat",
            "messages": sessions[session_id]["history"],  # Envia todo o histórico
            "temperature": 0.3
        },
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="DeepSeek API error")

    try:
        data = response.json()
        ai_response = data["choices"][0]["message"]["content"]
        sessions[session_id]["history"].append({"role": "assistant", "content": ai_response})
    except (KeyError, IndexError) as e:
        raise HTTPException(status_code=500, detail=f"Invalid API response: {str(e)}")

    return {
        "response": ai_response,
        "session_id": session_id,
        "history": sessions[session_id]["history"]  # Retorna todo o histórico
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
