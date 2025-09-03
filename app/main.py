import os
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .nlp import extract_text_from_upload, preprocess_text, top_keywords
from .classifiers import classify_text
from .ai import generate_reply
from .schemas import ClassificationResult

app = FastAPI(title="AutoU - Classificador de Emails")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
static_path = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process", response_class=HTMLResponse)
async def process_form(request: Request, upload: UploadFile = File(None), text_input: str = Form("")):
    try:
        text = ""

        has_real_file = False
        if upload and getattr(upload, "filename", None):
            fname = (upload.filename or "").strip()
            if fname:
                content = await upload.read()
                if content:  
                    has_real_file = True
                    text = extract_text_from_upload(upload.filename, content, upload.content_type)

        if not has_real_file:
            text = (text_input or "").strip()

        if not text:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "Não foi possível ler texto. Envie um .txt/.pdf válido ou cole o conteúdo do email."},
                status_code=200
            )

        meta = classify_text(text)

        reply, used_ai, ai_model = generate_reply(text, meta["category"])

        result = ClassificationResult(
            category=meta["category"],
            confidence=meta["confidence"],
            keywords=meta["keywords"],
            used_ai=used_ai,
            model=ai_model if used_ai else meta["model"],
            reply=reply
        )
        return templates.TemplateResponse("index.html", {"request": request, "result": result, "original_text": text})

    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"Erro no processamento: {e}"},
            status_code=200
        )


@app.post("/api/classify", response_model=ClassificationResult)
async def api_classify(payload: dict):
    text = (payload or {}).get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Campo 'text' é obrigatório.")
    meta = classify_text(text)
    reply, used_ai, ai_model = generate_reply(text, meta["category"])
    return ClassificationResult(
        category=meta["category"],
        confidence=meta["confidence"],
        keywords=meta["keywords"],
        used_ai=used_ai,
        model=ai_model if used_ai else meta["model"],
        reply=reply
    )
