import os
import re
import uuid
import logging
from typing import Optional, Tuple, List, Dict
from openai import OpenAI
from dotenv import load_dotenv

from persona import (
    SYSTEM_PROMPT,
    format_message_for_history,
    get_moderation_prompt,
    get_truncation_message,
    PERSONA_CONFIG
)

load_dotenv()

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversation_history: Dict[str, List[Dict[str, str]]] = {}

MODEL = os.getenv("MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.8"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

BANNED_WORDS_PATTERN = re.compile(
    r'\b(palavra_banida_exemplo)\b',
    re.IGNORECASE
)

def generate_session_id() -> str:
    return str(uuid.uuid4())

def preprocess_message(message: str) -> str:
    processed = " ".join(message.split())
    
    if len(processed) > 2000:
        logger.warning("Mensagem truncada por exceder limite")
        processed = processed[:2000]
    
    processed = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', processed)
    
    if not processed.strip():
        raise ValueError("Mensagem vazia após pré-processamento")
    
    return processed

def moderate_message(message: str) -> Tuple[bool, Optional[str]]:
    if BANNED_WORDS_PATTERN.search(message):
        return False, "Mensagem contém conteúdo inapropriado"
    
    return True, None

def get_or_create_session(session_id: Optional[str]) -> str:
    if session_id and session_id in conversation_history:
        return session_id
    
    new_session_id = session_id or generate_session_id()
    conversation_history[new_session_id] = []
    logger.info(f"Nova sessão criada: {new_session_id}")
    
    return new_session_id

def get_conversation_history(session_id: str) -> List[Dict[str, str]]:
    return conversation_history.get(session_id, [])

def truncate_history(history: List[Dict[str, str]], max_messages: int) -> List[Dict[str, str]]:
    if len(history) <= max_messages:
        return history
    
    truncated = history[-max_messages:]
    logger.info(f"Histórico truncado de {len(history)} para {len(truncated)} mensagens")
    
    return truncated

def add_to_history(session_id: str, user_msg: str, bot_msg: str):
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    user_formatted, bot_formatted = format_message_for_history(user_msg, bot_msg)
    
    conversation_history[session_id].append({"role": "user", "content": user_formatted})
    conversation_history[session_id].append({"role": "assistant", "content": bot_formatted})
    
    conversation_history[session_id] = truncate_history(
        conversation_history[session_id],
        MAX_HISTORY_MESSAGES
    )

def build_messages(history: List[Dict[str, str]], current_message: str) -> List[Dict[str, str]]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    messages.extend(history)
    
    messages.append({"role": "user", "content": current_message})
    
    return messages

def call_openai_api(messages: List[Dict[str, str]], temperature: float = TEMPERATURE) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=MAX_TOKENS,
            timeout=30
        )
        
        reply = response.choices[0].message.content
        
        logger.info(f"Resposta recebida da OpenAI (tokens: {response.usage.total_tokens})")
        
        return reply
    
    except Exception as e:
        logger.error(f"Erro na chamada à OpenAI API: {str(e)}")
        raise

def postprocess_response(response: str) -> str:
    processed = " ".join(response.split())
    
    processed = processed.strip()
    
    return processed

def ask_bot(message: str, session_id: Optional[str] = None, use_refinement: bool = False) -> Tuple[str, str]:
    processed_message = preprocess_message(message)
    
    is_safe, reason = moderate_message(processed_message)
    if not is_safe:
        raise ValueError(f"Mensagem rejeitada: {reason}")
    
    session_id = get_or_create_session(session_id)
    
    history = get_conversation_history(session_id)
    
    messages = build_messages(history, processed_message)
    
    if use_refinement:
        draft = call_openai_api(messages, temperature=0.9)
        
        refinement_messages = messages + [
            {"role": "assistant", "content": draft},
            {"role": "user", "content": "Refine a resposta acima mantendo o tom de Rick Sanchez mas sendo mais direto e conciso."}
        ]
        response = call_openai_api(refinement_messages, temperature=0.7)
    else:
        response = call_openai_api(messages)
    
    final_response = postprocess_response(response)
    
    add_to_history(session_id, processed_message, final_response)
    
    return final_response, session_id

def clear_session_history(session_id: str) -> bool:
    if session_id in conversation_history:
        del conversation_history[session_id]
        logger.info(f"Histórico da sessão {session_id} limpo")
        return True
    return False

def get_active_sessions_count() -> int:
    return len(conversation_history)
