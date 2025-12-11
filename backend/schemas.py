from typing import Optional
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        description="Mensagem do usuário para o chatbot",
        min_length=1,
        max_length=2000,
        example="Como funciona um buraco negro?"
    )
    session_id: Optional[str] = Field(
        None,
        description="ID da sessão (opcional, será gerado se ausente)",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Mensagem não pode ser vazia ou apenas espaços')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Rick, como funciona viagem no tempo?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

class ChatResponse(BaseModel):
    reply: str = Field(
        ...,
        description="Resposta do Rick Sanchez",
        example="*suspiro* Viagem no tempo? Ah, você quer mesmo abrir essa caixa de Pandora..."
    )
    session_id: str = Field(
        ...,
        description="ID da sessão",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "reply": "Olha, viagem no tempo é complicado. Você tem loops causais, paradoxos do avô, toda aquela bagunça temporal. Eu resolvi isso criando uma dimensão-buffer que... ah, esqueça, você não vai entender a matemática mesmo.",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

class ErrorResponse(BaseModel):
    detail: str = Field(
        ...,
        description="Descrição do erro",
        example="Mensagem contém conteúdo inapropriado"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Erro interno do servidor. Por favor, tente novamente."
            }
        }
