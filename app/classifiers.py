from typing import Dict, Tuple
from .nlp import preprocess_text, top_keywords

# Keyword sets to drive a simple rule-based baseline
PRODUCTIVE_HINTS = {
    "status","atualizacao","andamento","suporte","suporte tecnico","erro","falha","problema",
    "duvida","duvidas","solicitacao","solicitacoes","pedido","chamado","os","protocolo",
    "anexo","documento","envio","fatura","boleto","pagamento","recibo","nota","nfe","prazo","sla",
    "urgente","bloqueio","acesso","login","senha","cadastro","liberacao","retorno","resposta"
}

UNPRODUCTIVE_HINTS = {
    "obrigado","obrigada","agradeco","agradecimento","feliz","parabens","bom dia","boa tarde","boa noite",
    "boas festas","natal","ano novo","att","atenciosamente","grato","grata","abraços","abcs","obg","valeu"
}

def _score(text: str) -> Tuple[str, float, list]:
    cleaned, tokens = preprocess_text(text)
    toks_set = set(tokens)
    prod_hits = toks_set.intersection(PRODUCTIVE_HINTS)
    impr_hits = toks_set.intersection(UNPRODUCTIVE_HINTS)

    # basic scoring
    prod_score = len(prod_hits) + sum(1 for t in tokens if t in PRODUCTIVE_HINTS)*0.1
    impr_score = len(impr_hits) + sum(1 for t in tokens if t in UNPRODUCTIVE_HINTS)*0.1

    if prod_score == impr_score:
        category = "Produtivo" if any(w in cleaned for w in ("status","suporte","erro","duvida","solicitacao")) else "Improdutivo"
    elif prod_score > impr_score:
        category = "Produtivo"
    else:
        category = "Improdutivo"

    # a soft confidence between 0.5 and 0.95
    diff = abs(prod_score - impr_score)
    conf = min(0.95, 0.5 + min(0.45, diff * 0.1))

    return category, conf, top_keywords(tokens, k=8)

def classify_text(text: str) -> Dict:
    category, confidence, keywords = _score(text)
    return {
        "category": category,
        "confidence": round(confidence, 3),
        "keywords": keywords,
        "used_ai": False,
        "model": "rule-keyword-v1"
    }
