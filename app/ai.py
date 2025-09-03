import os
from typing import Optional

SYS_PROMPT = (
    "Você é um assistente de atendimento ao cliente para uma empresa de tecnologia financeira. "
    "Responda de forma objetiva, cordial e em português do Brasil. "
    "Se houver pedido de status, solicite/valide dados mínimos (ex.: número do protocolo, CPF/CNPJ, email cadastrado). "
    "Se houver menção a anexo, confirme o recebimento e diga que será encaminhado para análise. "
    "Evite promessas específicas de prazos se não houver SLA indicado; informe canais oficiais e prazos padrão quando aplicável. "
)

def _openai_available() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))

def _openai_chat(prompt: str, model: str = "gpt-4o-mini") -> str:
    try:
        # Prefer official SDK if available
        try:
            from openai import OpenAI
            client = OpenAI()
            # Use Chat Completions for broader compatibility
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role":"system","content": SYS_PROMPT},
                    {"role":"user","content": prompt}
                ],
                temperature=0.3,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            import requests, json
            headers = {
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            }
            body = {
                "model": model,
                "messages": [
                    {"role":"system","content": SYS_PROMPT},
                    {"role":"user","content": prompt}
                ],
                "temperature": 0.3
            }
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=20)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return ""

def generate_reply(email_text: str, category: str) -> (str, bool, str):
    """Return (reply_text, used_ai, model)"""
    used_ai = False
    model = "rule-template-v1"

    # Rule-based baseline
    baseline_prod = (
        "Olá! Tudo bem?\n\n"
        "Recebemos sua mensagem e já registramos o atendimento. "
        "Para agilizar a análise, pode confirmar por favor: número do protocolo (ou CPF/CNPJ), "
        "e o email cadastrado no sistema? "
        "Caso haja algum documento/anexo relacionado, fique à vontade para reenviar. "
        "Assim que tivermos a verificação, retornamos com a atualização.\n\n"
        "Atenciosamente,\nSuporte AutoU"
    )
    baseline_improd = (
        "Olá! Muito obrigado pela sua mensagem.\n\n"
        "Agradecemos o contato e seguimos à disposição se precisar de algo.\n\n"
        "Abraços,\nEquipe AutoU"
    )

    baseline = baseline_prod if category == "Produtivo" else baseline_improd

    # Try OpenAI for a richer, context-aware reply
    if _openai_available():
        prompt = (
            f"Categoria detectada: {category}.\n"
            "Gere uma resposta curta (até 6 linhas), cordial e objetiva em PT-BR para o email abaixo. "
            "Evite informações sensíveis e não prometa prazos específicos se não forem fornecidos.\n\n"
            f"EMAIL:\n{email_text}"
        )
        text = _openai_chat(prompt=prompt).strip()
        if text:
            used_ai = True
            model = "openai:gpt-4o-mini"
            return text, used_ai, model

    # Fallback
    return baseline, used_ai, model
