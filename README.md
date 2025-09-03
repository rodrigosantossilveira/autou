# 📧 AutoU Email Classifier

Aplicação desenvolvida para o **case AutoU**.

## Sobre o Projeto
- Upload de emails em **.txt / .pdf** ou colar texto diretamente.  
- **Classificação automática**:  
  - **Produtivo** → requer ação/resposta (status, suporte, protocolo, etc).  
  - **Improdutivo** → não requer ação (felicitações, agradecimentos, etc).  
- **Resposta sugerida**:  
  - Baseline com templates prontos.  
  - Opcional: integração com **OpenAI** (se `OPENAI_API_KEY` configurada).  
- Interface web simples e intuitiva (**FastAPI + Jinja2 + CSS**).  
- API REST (`/api/classify`) para integração programática.  

---

## Instalação Local

### 1. Clonar repositório
```bash
git clone https://github.com/<seu-usuario>/autou-email-classifier.git
cd autou-email-classifier
```

### 2. Criar ambiente virtual
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. (Opcional) Configurar chave da OpenAI
```bash
OPENAI_API_KEY=sua_chave # Colocar no .env
```
### 5. Executar servidor
```bash
uvicorn app.main:app --reload
```
> Acesse: http://127.0.0.1:8000

---

## Deploy na Nuvem (Render)

> - 1. Crie um repositório público no GitHub com o código.
>
> - 2. No Render:
>
>   - New Web Service → conecte o repositório.
>
>   - Build: pip install -r requirements.txt
>
>   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
> 
>   - (Opcional) configure OPENAI_API_KEY como variável de ambiente.
>
> - 3. Use a URL pública gerada para acessar a aplicação.

## Uso

### Interface Web

> 1. Abra a aplicação.
>
> 2. Faça upload de um .txt / .pdf ou cole o texto do email.
>
> 3. Clique em Processar.
>
> 4. Veja o resultado: categoria, confiança, palavras-chave e resposta sugerida.
>
> 5. Use os botões Copiar ou Baixar JSON para reutilizar a resposta.

### API REST

> Endpoint: POST /api/classify
>
> Exemplo de payload:
```json
{
  "text": "Poderiam me informar o status do protocolo 12345? Ainda não consigo acessar o sistema."
}
```
### Resposta:
```json
{
  "category": "Produtivo",
  "confidence": 0.83,
  "keywords": ["status","protocolo","acesso"],
  "used_ai": false,
  "model": "rule-keyword-v1",
  "reply": "Olá! Recebemos sua mensagem..."
}
```

## Estrutura

app/
  ai.py             # Geração de resposta
  classifiers.py    # Classificação Produtivo/Improdutivo
  main.py           # Rotas FastAPI
  nlp.py            # Pré-processamento + extração de texto
  schemas.py        # Modelos Pydantic
  templates/        # HTML
  static/           # CSS + JS
sample_emails/      # Arquivos de teste
requirements.txt
README.md


## Testes Rápidos

> - Upload: sample_emails/produtivo1.txt → Produtivo.
>
> - Upload: sample_emails/improdutivo1.txt → Improdutivo.
>
> - Colar texto simples → resultado direto.
