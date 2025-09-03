import io
import re
import unicodedata
from typing import List, Tuple
from pypdf import PdfReader
import pytesseract
from PIL import Image

# Stopwords simples em PT-BR
PT_STOPWORDS = {
    "a","à","às","ao","aos","as","o","os","um","uma","uns","umas",
    "de","da","das","do","dos","d","e","é","em","no","nos","na","nas","num","numa",
    "para","pra","por","com","sem","sob","sobre","entre","até","após","antes","contra",
    "que","quem","quando","onde","como","qual","quais","porque","porquê",
    "mas","mais","menos","também","todavia","porém","ou","se",
    "já","ainda","muito","muitos","muita","muitas","pouco","pouca","poucos","poucas"
}

def normalize_text(text: str) -> str:
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = re.sub(r"[\r\t]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Zà-úÀ-Ú0-9]+", text, flags=re.UNICODE)

def remove_stopwords(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in PT_STOPWORDS and len(t) > 2]

def preprocess_text(text: str) -> Tuple[str, list]:
    norm = normalize_text(text)
    tokens = tokenize(norm)
    clean = remove_stopwords(tokens)
    return " ".join(clean), clean

# ---- EXTRAÇÃO DE PDF ----

def _extract_with_pypdf(file_bytes: bytes) -> str:
    try:
        with io.BytesIO(file_bytes) as bio:
            reader = PdfReader(bio)
            parts = []
            for page in reader.pages:
                parts.append(page.extract_text() or "")
        return "\n".join(parts).strip()
    except Exception:
        return ""

def _extract_with_pdfminer(file_bytes: bytes) -> str:
    try:
        from pdfminer.high_level import extract_text
        with io.BytesIO(file_bytes) as bio:
            text = extract_text(bio) or ""
        return text.strip()
    except Exception:
        return ""

def _extract_with_ocr(file_bytes: bytes) -> str:
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(file_bytes)
        parts = []
        for img in images:
            txt = pytesseract.image_to_string(img, lang="por")
            if txt:
                parts.append(txt)
        return "\n".join(parts).strip()
    except Exception as e:
        print(f"[WARN] OCR falhou: {e}")
        return ""

def extract_text_from_pdf(file_bytes: bytes) -> str:
    # 1) tenta PyPDF
    text = _extract_with_pypdf(file_bytes)
    if text:
        return text

    # 2) tenta pdfminer
    text = _extract_with_pdfminer(file_bytes)
    if text:
        return text

    # 3) fallback: OCR com Tesseract
    text = _extract_with_ocr(file_bytes)
    return text

def extract_text_from_upload(filename: str, content: bytes, content_type: str) -> str:
    is_pdf = (filename or "").lower().endswith(".pdf") or (content_type or "").lower() == "application/pdf"
    if is_pdf:
        return extract_text_from_pdf(content)

    # assume texto puro
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return content.decode(enc, errors="ignore").strip()
        except Exception:
            continue
    return ""

def top_keywords(tokens: list, k: int = 8) -> list:
    from collections import Counter
    freq = Counter(tokens)
    return [w for w, _ in freq.most_common(k)]
