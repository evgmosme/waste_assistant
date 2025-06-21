# Waste Assistant Chatbot for Jyväskylä ♻️

**Waste Assistant** is a friendly Flask + OpenAI bot that helps newcomers—and anyone else—figure out where every item belongs in the city’s recycling system.

> "Where should this go in Jyväskylä?"
> Ask in English or Finnish, or snap a photo—the bot knows the answer.

---

## ✨ Features

* **Local expertise** Tailored to Jyväskylä’s official sorting rules.
* **Text *or* photo** Type a question *or* upload an image of the item.
* **Bilingual UI** Instantly switch between **English** and **Finnish**.
* **Smart image compression** 500 × 500 JPEG (quality 75) before sending to OpenAI → fewer tokens & lower cost.
* **GPT-4o-mini vision + chat** One model for language *and* image reasoning.
* **Serverless host** Runs on Google Cloud Run; scales to zero when idle.

---

## 🔧 Tech stack

| Layer         | Tool / Service                 |
| ------------- | ------------------------------ |
| Language      | Python 3.10                    |
| Web framework | Flask                          |
| AI / Vision   | OpenAI API (gpt-4o-mini)       |
| Container     | Docker                         |
| CI / CD       | GitHub Actions  →  Cloud Build |
| Runtime       | Google Cloud Run               |

---

## 🚀 Quick start (local)

```bash
# 1 Clone & enter repo
git clone https://github.com/<your-user>/waste-assistant.git
cd waste-assistant

# 2 Virtual env
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3 Install deps
pip install -r requirements.txt

# 4 Create .env
cat > .env <<EOF
api_key=YOUR_OPENAI_API_KEY
secret_key=YOUR_FLASK_SECRET_KEY
EOF

# 5 Run
python app.py   # → http://localhost:8086
```

Open the URL, ask “Where do I throw plastic bags?” or upload a picture, and get an instant answer.

---

## 🖥️ Usage tips

* **Ask anything** "Cardboard pizza box?", "Where do batteries go?" …
  The bot replies with the right bin, plus nuances (e.g. rinse / remove labels).
* **Photo mode** Drag-and-drop or tap the camera icon on mobile.
  The compressed image is analysed by GPT-4o-mini vision.
* **Language toggle** Switch EN ↔ FI in the header; the bot answers accordingly.
* **Session memory** Context survives for 30 minutes so follow-ups are fluid.

---

## 🗂️ Code overview

* **`app.py`** Flask routes (`/`, `/ask`, `/reset`) + OpenAI calls.
* **Prompts** System messages live in `model_instructions/` (EN & FI).
* **Image pipeline** `compress_image()` resizes & recompresses uploads to save tokens.
* **Session** Flask-Session stores chat history on disk (`./flask_session`).

---

## ☁️ Continuous deployment (Cloud Run)

A single GitHub Actions workflow (`.github/workflows/deploy.yml`) handles CI/CD:

1. **Checkout** code.
2. **Authenticate** with a service-account key (`GCP_SA_KEY`).
3. `gcloud run deploy --source .` – Buildpacks build & push the image.
4. Cloud Run rolls out a new revision of the `wasteassistant` service.

> Public URL format: `https://wasteassistant-xxxxx.a.run.app`

Required secrets:

| Secret name      | Purpose / example value                                |
| ---------------- | ------------------------------------------------------ |
| GCP\_SA\_KEY     | JSON key (Artifact Registry + Cloud Build + Run roles) |
| GCP\_PROJECT\_ID | e.g. `gpt-models-436109`                               |
| GCP\_REGION      | e.g. `europe-north1`                                   |
| OPENAI\_API\_KEY | `sk-…`                                                 |
| FLASK\_SECRET    | `openssl rand -hex 32` (any long random string)        |

---

## 🤝 Contributing

Pull requests are welcome!

1. Fork → branch → commit with clear messages.
2. Push and open a PR against `main`.
3. CI will build & deploy the preview automatically.

Found a bug or want to suggest a new feature? Open an issue.

---

## 📄 License

Apache-2.0.  See `LICENSE` for full text
