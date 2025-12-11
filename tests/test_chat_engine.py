"""
Testes unitários para o chat_engine
Mockando chamadas à OpenAI API
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from chat_engine import (
    preprocess_message,
    moderate_message,
    generate_session_id,
    truncate_history,
    postprocess_response
)

class TestPreprocessing:
    """Testes de pré-processamento de mensagens"""
    
    def test_preprocess_removes_extra_spaces(self):
        """Testa remoção de espaços em excesso"""
        message = "Olá    Rick,    como    vai?"
        result = preprocess_message(message)
        assert result == "Olá Rick, como vai?"
    
    def test_preprocess_trims_message(self):
        """Testa trim de espaços nas extremidades"""
        message = "  Olá Rick  "
        result = preprocess_message(message)
        assert result == "Olá Rick"
    
    def test_preprocess_handles_long_message(self):
        """Testa truncamento de mensagens longas"""
        message = "A" * 3000
        result = preprocess_message(message)
        assert len(result) == 2000
    
    def test_preprocess_empty_message_raises_error(self):
        """Testa que mensagem vazia gera erro"""
        with pytest.raises(ValueError):
            preprocess_message("   ")

class TestModeration:
    """Testes de moderação de conteúdo"""
    
    def test_moderate_safe_message(self):
        """Testa que mensagem segura passa na moderação"""
        message = "Como funciona um buraco negro?"
        is_safe, reason = moderate_message(message)
        assert is_safe is True
        assert reason is None
    
    def test_moderate_handles_scientific_terms(self):
        """Testa que termos científicos são permitidos"""
        message = "Explique física quântica e entrelaçamento"
        is_safe, reason = moderate_message(message)
        assert is_safe is True

class TestSessionManagement:
    """Testes de gerenciamento de sessões"""
    
    def test_generate_session_id_format(self):
        """Testa formato do session_id gerado"""
        session_id = generate_session_id()
        # UUID tem 36 caracteres (incluindo hífens)
        assert len(session_id) == 36
        assert session_id.count('-') == 4
    
    def test_generate_unique_session_ids(self):
        """Testa que session_ids são únicos"""
        id1 = generate_session_id()
        id2 = generate_session_id()
        assert id1 != id2

class TestHistoryManagement:
    """Testes de gerenciamento de histórico"""
    
    def test_truncate_history_no_truncation_needed(self):
        """Testa que histórico pequeno não é truncado"""
        history = [
            {"role": "user", "content": "msg1"},
            {"role": "assistant", "content": "reply1"}
        ]
        result = truncate_history(history, max_messages=10)
        assert len(result) == 2
        assert result == history
    
    def test_truncate_history_truncates_correctly(self):
        """Testa truncamento de histórico longo"""
        history = [
            {"role": "user", "content": f"msg{i}"}
            for i in range(30)
        ]
        result = truncate_history(history, max_messages=10)
        assert len(result) == 10
        # Deve manter as últimas mensagens
        assert result[0]["content"] == "msg20"
        assert result[-1]["content"] == "msg29"

class TestPostprocessing:
    """Testes de pós-processamento de respostas"""
    
    def test_postprocess_removes_extra_spaces(self):
        """Testa remoção de espaços em excesso na resposta"""
        response = "Olá,    isso    é    uma    resposta."
        result = postprocess_response(response)
        assert result == "Olá, isso é uma resposta."
    
    def test_postprocess_trims_response(self):
        """Testa trim de espaços na resposta"""
        response = "  Resposta do Rick  "
        result = postprocess_response(response)
        assert result == "Resposta do Rick"

class TestChatEngine:
    """Testes de integração do chat engine"""
    
    @patch('chat_engine.client')
    def test_ask_bot_returns_response_and_session_id(self, mock_client):
        """Testa que ask_bot retorna resposta e session_id"""
        # Mock da resposta da OpenAI
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Olá, eu sou Rick Sanchez."
        mock_response.usage.total_tokens = 100
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Importar aqui para pegar o mock
        from chat_engine import ask_bot
        
        # Testar
        reply, session_id = ask_bot("Olá Rick")
        
        assert isinstance(reply, str)
        assert len(reply) > 0
        assert isinstance(session_id, str)
        assert len(session_id) == 36  # UUID format
    
    @patch('chat_engine.client')
    def test_ask_bot_maintains_session(self, mock_client):
        """Testa que ask_bot mantém sessão entre chamadas"""
        # Mock da resposta da OpenAI
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta do Rick"
        mock_response.usage.total_tokens = 100
        
        mock_client.chat.completions.create.return_value = mock_response
        
        from chat_engine import ask_bot
        
        # Primeira mensagem
        reply1, session_id1 = ask_bot("Mensagem 1")
        
        # Segunda mensagem com mesmo session_id
        reply2, session_id2 = ask_bot("Mensagem 2", session_id=session_id1)
        
        # Session ID deve ser mantido
        assert session_id1 == session_id2
    
    @patch('chat_engine.client')
    def test_ask_bot_handles_empty_message(self, mock_client):
        """Testa que ask_bot rejeita mensagem vazia"""
        from chat_engine import ask_bot
        
        with pytest.raises(ValueError):
            ask_bot("   ")

class TestIntegration:
    """Testes de integração completos"""
    
    @patch('chat_engine.client')
    def test_full_conversation_flow(self, mock_client):
        """Testa fluxo completo de conversa"""
        # Mock das respostas
        responses = [
            "Primeira resposta do Rick",
            "Segunda resposta do Rick",
            "Terceira resposta do Rick"
        ]
        
        mock_responses = []
        for resp_text in responses:
            mock_resp = MagicMock()
            mock_resp.choices = [MagicMock()]
            mock_resp.choices[0].message.content = resp_text
            mock_resp.usage.total_tokens = 100
            mock_responses.append(mock_resp)
        
        mock_client.chat.completions.create.side_effect = mock_responses
        
        from chat_engine import ask_bot
        
        # Simular conversa
        session_id = None
        
        for i, expected_response in enumerate(responses):
            reply, session_id = ask_bot(f"Mensagem {i+1}", session_id=session_id)
            assert reply == expected_response
            assert session_id is not None

if __name__ == "__main__":
    # Rodar testes
    pytest.main([__file__, "-v"])
