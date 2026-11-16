# ✍️ PDF Signer

Webapp locale per firmare PDF: carica la tua firma una volta sola, apri il documento, posiziona la firma con drag & drop, esporta il PDF firmato.

---

## Requisiti

- Python 3.9+
- [`uv`](https://github.com/astral-sh/uv) **oppure** Python `venv` standard

---

## Avvio rapido

### Con `uv` (consigliato)

```bash
git clone https://github.com/lucahardonk/document_signer.git
cd document_signer

uv venv
uv pip install -r requirements.txt
uv run python app.py
```

### Con `venv` standard

```bash
git clone https://github.com/lucahardonk/document_signer.git
cd document_signer

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Con lo script automatico (Linux/macOS)

```bash
git clone https://github.com/lucahardonk/document_signer.git
cd document_signer
chmod +x run.sh
./run.sh
```

Poi apri il browser su:

```
http://localhost:5000
```

Per usare un'altra porta, passala come argomento a `run.sh` (viene inoltrata a `app.py --port`):

```bash
./run.sh 8080          # → http://localhost:8080
# oppure direttamente:
python3 app.py --port 8080
```

---

## Uso

1. **Carica la firma** — clicca il box a sinistra e seleziona un'immagine PNG o JPG della tua firma. Viene salvata automaticamente in `~/.pdf_signer.json` e ricaricata ad ogni avvio.
2. **Apri il PDF** — clicca **📂 Apri PDF** e seleziona il documento da firmare.
3. **Posiziona la firma** — trascinala dove vuoi; ridimensionala dall'angolino rosso in basso a destra; regola rotazione e opacità con gli slider nel pannello sinistro.
4. **Esporta** — clicca **💾 Esporta _firmato**: il file viene scaricato con `_firmato` aggiunto al nome originale.

> **Consiglio:** usa una firma su sfondo trasparente (PNG con canale alfa) per un risultato più pulito.

---

## Dipendenze

| Pacchetto   | Uso                          |
|-------------|------------------------------|
| Flask       | Server HTTP locale           |
| PyMuPDF     | Lettura e scrittura PDF      |
| Pillow      | Elaborazione immagine firma  |

---

## Struttura progetto

```
document_signer/
├── app.py               # Backend Flask
├── requirements.txt
├── run.sh               # Script avvio con venv automatico
└── templates/
    └── index.html       # Frontend (PDF.js + drag & drop)
```

---

## Note

- La webapp funziona **interamente in locale**: nessun dato viene inviato a server esterni. Il PDF.js usato per la preview del documento viene caricato via CDN al primo avvio (serve connessione internet una tantum; dopo è in cache del browser).
- Testato su **Linux**. Funziona anche su macOS e Windows con `uv` o `venv`.
