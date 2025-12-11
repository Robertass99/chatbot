import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from schemas import ChatRequest, ChatResponse
from chat_engine import ask_bot

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Rick Sanchez Chatbot API",
    description="Backend API para chatbot que personifica Rick Sanchez (versão acadêmica controlada)",
    version="1.0.0"
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY não configurada!")
        raise ValueError("OPENAI_API_KEY é obrigatória. Configure no arquivo .env")
    logger.info("✓ Servidor iniciado com sucesso")
    logger.info(f"✓ CORS configurado para: {ALLOWED_ORIGINS}")

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Rick Sanchez Chatbot API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(request: ChatRequest):
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mensagem não pode estar vazia"
            )
        
        logger.info(f"Recebida mensagem da sessão: {request.session_id or 'nova'}")
        
        reply, session_id = ask_bot(
            message=request.message,
            session_id=request.session_id
        )
        
        logger.info(f"Resposta gerada para sessão: {session_id}")
        
        return ChatResponse(reply=reply, session_id=session_id)
    
    except ValueError as ve:
        logger.warning(f"Erro de validação: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    
    except Exception as e:
        logger.error(f"Erro interno: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor. Por favor, tente novamente."
        )

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    from chat_engine import clear_session_history
    
    try:
        cleared = clear_session_history(session_id)
        if cleared:
            logger.info(f"Sessão {session_id} limpa com sucesso")
            return {"message": f"Sessão {session_id} limpa com sucesso"}
        else:
            return {"message": f"Sessão {session_id} não encontrada"}
    except Exception as e:
        logger.error(f"Erro ao limpar sessão: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao limpar sessão"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
