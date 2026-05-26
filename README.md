# YouTube Demand & Niche Analyzer (Showcase)

> **Hinweis:** Dieses Repository ist ein reduziertes **Showcase-Projekt** für Bewerbungs- und Portfolio-Zwecke. Es enthält nicht die vollständige, lauffähige Applikation, sondern ausgewählte Code-Snippets, die die Kernarchitektur und meine Arbeitsweise demonstrieren.

## Über das Projekt
Dieses Projekt ist ein automatisiertes Python-Tool zur datengetriebenen Analyse von YouTube-Nischen. Es generiert Keywords, fragt Metadaten über die YouTube Data API ab und nutzt Large Language Models (LLMs), um fundierte Content-Strategien und Video-Ideen zu entwickeln.

## Gezeigte Code-Snippets & Skills

* `search_videos.py` & `http_request.py`: **API-Integration & Automatisierung.** Effiziente Abfrage der YouTube Data API (inkl. Batching) und Verarbeitung von HTTP-Requests.
* `llm.py`: **LLM Integration & Prompt Engineering.** Steuerung der OpenAI API zur Generierung strukturierter Daten. Nutzung von `Pydantic` (BaseModels), um konsistente und typensichere JSON-Outputs der KI zu erzwingen.
* `json_utils.py`: **Data Handling.** Sicheres Lesen, Bereinigen (via Regex) und Speichern komplexer JSON-Datenstrukturen.
* `data.json`: Ein Beispiel für die verarbeiteten API-Responses (Metadaten, Statistiken).

## 🛠️ Tech-Stack
* **Sprache:** Python 3.11
* **Haupt-Bibliotheken:** `google-api-python-client`, `requests`, `openai`, `pydantic`, `regex`
* **APIs:** YouTube Data API v3, OpenAI API

*Bei Fragen zum vollständigen Code, der NLP-Pipeline oder der Systemarchitektur stehe ich in einem persönlichen Interview gerne zur Verfügung!*






