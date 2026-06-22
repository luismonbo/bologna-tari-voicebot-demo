# Phase 1: hardcoded TARI chunks + keyword-overlap retrieval.
# Phase 2 (§12 step 5): replace _score() with pgvector cosine similarity
# using the same multilingual embedding model used at ingestion time.

_CHUNKS = [
    {
        "text": (
            "La TARI (Tassa sui Rifiuti) è il tributo comunale che finanzia il servizio "
            "di raccolta e smaltimento dei rifiuti solidi urbani. È dovuta da chiunque "
            "possieda o detenga locali o aree scoperte suscettibili di produrre rifiuti."
        ),
        "source_url": "https://www.comune.bologna.it/servizi-informazioni/tari",
    },
    {
        "text": (
            "Il pagamento della TARI avviene tramite avvisi di pagamento inviati dal Comune. "
            "È possibile pagare online tramite il portale del Comune, presso gli sportelli "
            "bancari abilitati, agli uffici postali, oppure con modello F24."
        ),
        "source_url": "https://www.comune.bologna.it/servizi-informazioni/tari/pagamento",
    },
    {
        "text": (
            "Le scadenze TARI vengono comunicate annualmente tramite gli avvisi di pagamento. "
            "Di norma sono previste due o tre rate nel corso dell'anno. "
            "Le date esatte sono riportate sull'avviso ricevuto a casa."
        ),
        "source_url": "https://www.comune.bologna.it/servizi-informazioni/tari/scadenze",
    },
    {
        "text": (
            "Per richiedere riduzioni o esenzioni TARI (ad esempio per locali non utilizzati, "
            "compostaggio domestico, o situazioni di difficoltà economica) è necessario "
            "presentare apposita istanza all'Ufficio Tributi del Comune."
        ),
        "source_url": "https://www.comune.bologna.it/servizi-informazioni/tari/riduzioni",
    },
    {
        "text": (
            "In caso di cambio di residenza, vendita dell'immobile, oppure inizio o "
            "cessazione dell'attività, è obbligatorio presentare una dichiarazione di "
            "variazione TARI entro 90 giorni dall'evento all'Ufficio Tributi."
        ),
        "source_url": "https://www.comune.bologna.it/servizi-informazioni/tari/dichiarazioni",
    },
    {
        "text": (
            "La tariffa TARI è composta da una parte fissa (basata sulla superficie "
            "dell'immobile) e una parte variabile (basata sul numero di occupanti). "
            "Le tariffe sono deliberate annualmente dal Consiglio Comunale."
        ),
        "source_url": "https://www.comune.bologna.it/servizi-informazioni/tari/tariffe",
    },
    {
        "text": (
            "Per contestare un avviso TARI ritenuto errato è possibile presentare ricorso "
            "al Comune entro 60 giorni dalla notifica, oppure rivolgersi al Giudice Tributario "
            "entro 30 giorni. È consigliabile contattare prima l'Ufficio Tributi per un chiarimento."
        ),
        "source_url": "https://www.comune.bologna.it/servizi-informazioni/tari/ricorsi",
    },
    {
        "text": (
            "L'Ufficio Tributi del Comune di Bologna gestisce la TARI e altri tributi locali. "
            "Per informazioni o appuntamenti è possibile contattare lo sportello telefonico "
            "o prenotare un appuntamento tramite questo servizio."
        ),
        "source_url": "https://www.comune.bologna.it/ufficio-tributi",
    },
]


def _score(question_lower: str, chunk_text: str) -> float:
    words = set(question_lower.split())
    chunk_words = set(chunk_text.lower().split())
    overlap = len(words & chunk_words)
    return overlap / max(len(words), 1)


def query(question: str, top_k: int = 3) -> dict:
    question_lower = question.lower()
    scored = [
        {**chunk, "score": round(_score(question_lower, chunk["text"]), 4)}
        for chunk in _CHUNKS
    ]
    scored = [c for c in scored if c["score"] > 0]
    scored.sort(key=lambda c: c["score"], reverse=True)
    top = scored[:top_k]
    context = "\n\n".join(c["text"] for c in top)
    return {"context": context, "chunks": top}
