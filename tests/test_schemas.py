"""
Testes unitários para as schemas Pydantic
"""
import pytest
from pydantic import ValidationError
import sys
import os

# Adicionar diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from schemas import ChatRequest, ChatResponse

class TestChatRequest:
    """Testes para schema ChatRequest"""
    
    def test_valid_chat_request(self):
        """Testa criação de ChatRequest válido"""
        request = ChatRequest(
            message="Como funciona um buraco negro?",
            session_id="test-session-123"
        )
        assert request.message == "Como funciona um buraco negro?"
        assert request.session_id == "test-session-123"
    
    def test_chat_request_without_session_id(self):
        """Testa ChatRequest sem session_id (opcional)"""
        request = ChatRequest(message="Olá Rick")
        assert request.message == "Olá Rick"
        assert request.session_id is None
    
    def test_chat_request_empty_message_fails(self):
        """Testa que mensagem vazia falha validação"""
        with pytest.raises(ValidationError):
            ChatRequest(message="")
    
    def test_chat_request_whitespace_only_fails(self):
        """Testa que mensagem só com espaços falha validação"""
        with pytest.raises(ValidationError):
            ChatRequest(message="   ")
    
    def test_chat_request_too_long_message_fails(self):
        """Testa que mensagem muito longa falha validação"""
        long_message = "A" * 2001
        with pytest.raises(ValidationError):
            ChatRequest(message=long_message)

class TestChatResponse:
    """Testes para schema ChatResponse"""
    
    def test_valid_chat_response(self):
        """Testa criação de ChatResponse válido"""
        response = ChatResponse(
            reply="Olá, eu sou Rick Sanchez.",
            session_id="test-session-123"
        )
        assert response.reply == "Olá, eu sou Rick Sanchez."
        assert response.session_id == "test-session-123"
    
    def test_chat_response_requires_reply(self):
        """Testa que reply é obrigatório"""
        with pytest.raises(ValidationError):
            ChatResponse(session_id="test-session-123")
    
    def test_chat_response_requires_session_id(self):
        """Testa que session_id é obrigatório"""
        with pytest.raises(ValidationError):
            ChatResponse(reply="Resposta do Rick")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
