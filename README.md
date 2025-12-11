# RickBot - Chatbot Rick Sanchez

Chatbot com personalidade de Rick Sanchez usando FastAPI e OpenAI API.

## Sobre

Backend em Python (FastAPI) + Frontend com interface espacial cyberpunk. Rick sarcástico, superinteligente e impaciente, mas sem conteúdo inapropriado.

## Estrutura

```
chatbot-rick/
├── backend/
│   ├── app.py
│   ├── chat_engine.py
│   ├── persona.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── tests/
```

## Como Usar no Seu PC

### 1. Pré-requisitos

- Python 3.8+
- Chave API da OpenAI ([obter aqui](https://platform.openai.com/api-keys))

### 2. Baixar o Projeto

```bash
git clone <url-do-repositorio>
cd chatbot-rick
```

### 3. Configurar OpenAI API Key

Crie o arquivo `backend/.env`:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
MODEL=gpt-4o-mini
TEMPERATURE=0.8
MAX_TOKENS=500
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:8080
```

### 4. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 5. Iniciar o Backend

```bash
python -m uvicorn app:app --reload --port 8000
```

Backend rodando em: `http://localhost:8000`

### 6. Iniciar o Frontend (nova aba do terminal)

```bash
cd frontend
python -m http.server 8080
```

### 7. Abrir no Navegador

Acesse: `http://localhost:8080`

## Características do Rick

Permitido:
- Sarcasmo e humor ácido  
- Referências científicas complexas  
- Impaciência com perguntas básicas  

Não permitido:
- Sem palavrões explícitos  
- Sem conteúdo sexual ou violento  
- Sem apologia a drogas/álcool  

## API

**POST** `/api/chat`
```json
{
  "message": "Como funciona um buraco negro?",
  "session_id": "opcional"
}
```

**GET** `/health`

## Licença

MIT License
