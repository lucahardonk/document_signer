import os, json, base64, io, uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
import pymupdf as fitz
from PIL import Image

app = Flask(__name__)

SETTINGS_FILE = Path.home() / ".pdf_signer.json"
UPLOAD_DIR    = Path.home() / ".pdf_signer_tmp"
UPLOAD_DIR.mkdir(exist_ok=True)

# ── helpers ────────────────────────────────────────────────────────────────

def load_settings():
    try:
        return json.loads(SETTINGS_FILE.read_text())
    except Exception:
        return {}

def save_settings(d):
    SETTINGS_FILE.write_text(json.dumps(d))

# ── routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/signature", methods=["GET", "POST"])
def signature_api():
    if request.method == "POST":
        f = request.files.get("file")
        if not f:
            return jsonify(ok=False, error="Nessun file"), 400
        img = Image.open(f).convert("RGBA")
        buf = io.BytesIO()
        img.save(buf, "PNG")
        s = load_settings()
        s["sig"] = base64.b64encode(buf.getvalue()).decode()
        save_settings(s)
        return jsonify(ok=True)
    # GET
    s = load_settings()
    if "sig" not in s:
        return ("", 404)
    return send_file(io.BytesIO(base64.b64decode(s["sig"])), mimetype="image/png")


@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files.get("pdf")
    if not f:
        return jsonify(ok=False, error="Nessun PDF"), 400
    tid = uuid.uuid4().hex
    dest = UPLOAD_DIR / f"{tid}.pdf"
    f.save(str(dest))
    doc = fitz.open(str(dest))
    pages = doc.page_count
    doc.close()
    return jsonify(ok=True, id=tid, name=f.filename, pages=pages)


@app.route("/api/pdf/<tid>")
def serve_pdf(tid):
    p = UPLOAD_DIR / f"{tid}.pdf"
    if not p.exists():
        return ("", 404)
    return send_file(str(p), mimetype="application/pdf")


@app.route("/api/export", methods=["POST"])
def export():
    d = request.json
    p = UPLOAD_DIR / f"{d['id']}.pdf"
    if not p.exists():
        return jsonify(error="PDF non trovato sul server, ricaricalo"), 404

    s = load_settings()
    if "sig" not in s:
        return jsonify(error="Nessuna firma configurata"), 400

    img_bytes = base64.b64decode(s["sig"])
    angle = float(d.get("angle", 0))

    x, y = float(d["x"]), float(d["y"])
    w, h = float(d["w"]), float(d["h"])
    cx, cy = x + w / 2, y + h / 2

    # Ruota come nel browser: stira l'immagine a w:h, ruota con expand, centra
    if angle:
        import math
        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        k = 4  # pixel per punto PDF (qualità)
        img = img.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
        img = img.rotate(-angle, expand=True, resample=Image.BICUBIC)
        buf = io.BytesIO()
        img.save(buf, "PNG")
        img_bytes = buf.getvalue()
        a = math.radians(angle)
        w, h = (abs(w * math.cos(a)) + abs(h * math.sin(a)),
                abs(w * math.sin(a)) + abs(h * math.cos(a)))
        x, y = cx - w / 2, cy - h / 2

    # Applica opacità se < 1
    opacity = float(d.get("opacity", 1.0))
    if opacity < 0.99:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        r_ch, g_ch, b_ch, a_ch = img.split()
        a_ch = a_ch.point(lambda v: int(v * opacity))
        img.putalpha(a_ch)
        buf = io.BytesIO()
        img.save(buf, "PNG")
        img_bytes = buf.getvalue()

    # Embed nel PDF con PyMuPDF
    doc  = fitz.open(str(p))
    page = doc[int(d.get("page", 0))]
    rect = fitz.Rect(x, y, x + w, y + h)
    page.insert_image(rect, stream=img_bytes, keep_proportion=False)

    # Salva
    stem     = Path(d.get("name", "documento.pdf")).stem
    out_name = f"{stem}_firmato.pdf"
    out_path = UPLOAD_DIR / out_name
    doc.save(str(out_path))
    doc.close()

    return send_file(
        str(out_path),
        as_attachment=True,
        download_name=out_name,
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="PDF Signer")
    ap.add_argument("--port", type=int, default=5000, help="porta HTTP (default 5000)")
    args = ap.parse_args()
    print(f"🖊️  PDF Signer avviato → http://localhost:{args.port}")
    app.run(port=args.port, debug=False)
