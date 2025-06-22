# Waste Assistant Chatbot for Jyväskylä ♻️

**Waste Assistant** is a friendly Flask + OpenAI bot that helps newcomers—and anyone else—figure out where every item belongs in the city’s recycling system.

> “Where should this go in Jyväskylä?”\
> Ask in English or Finnish, or snap a photo—the bot knows the answer.

---

## ✨ Features

- **Local expertise** — tailored to Jyväskylä’s official sorting rules.
- **Text *****or***** photo** — type a question *or* upload an image of the item.
- **Bilingual UI** — instantly switch between **English** and **Finnish**.
- **Smart image compression** — 500 × 500 JPEG (quality 75) → fewer OpenAI tokens & lower cost.
- **GPT‑4o‑mini vision + chat** — one model for language *and* image reasoning.
- **Serverless host** — runs on Google Cloud Run; scales to zero when idle.

---

## 🔧 Tech stack

| Layer         | Tool / Service               |
| ------------- | ---------------------------- |
| Language      | Python 3.10                  |
| Web framework | Flask                        |
| AI / Vision   | OpenAI API (gpt‑4o‑mini)     |
| Container     | Docker                       |
| CI / CD       | GitHub Actions → Cloud Build |
| Runtime       | Google Cloud Run             |

---

## 🚀 Quick start (local)

```bash
# 1 Clone & enter repo
git clone https://github.com/<your‑user>/waste-assistant.git
cd waste-assistant

# 2 Virtual env
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3 Install deps
pip install -r requirements.txt

# 4 Create .env (local only)
cat > .env <<EOF
api_key=YOUR_OPENAI_API_KEY
secret_key=YOUR_FLASK_SECRET_KEY
EOF

# 5 Run
python app.py   # → http://localhost:8086
```

Open the URL, ask “Where do I throw plastic bags?” or upload a picture, and get an instant answer.

---

## 🖥️ Usage tips

- **Ask anything** — "Cardboard pizza box?", "Where do batteries go?" …\
  The bot replies with the right bin, plus nuances (e.g. rinse / remove labels).
- **Photo mode** — drag‑and‑drop or tap the camera icon on mobile.\
  The compressed image is analysed by GPT‑4o‑mini vision.
- **Session memory** — context survives for 30 minutes so follow‑ups are fluid.

---

## 🗂️ Code overview

- `` — Flask routes (`/`, `/ask`, `/reset`) + OpenAI calls.
- **Prompts** — system messages live in `model_instructions/` (EN & FI).
- **Image pipeline** — `compress_image()` resizes & recompresses uploads.
- **Session** — Flask‑Session stores chat history on disk (`./flask_session`).

---

## ☁️ Continuous deployment (Cloud Run)

The workflow `.github/workflows/deploy.yml` builds from source with Cloud Build and deploys a new revision on every push to `main`.

1. **Checkout** the repo.
2. **Authenticate** using the service‑account key in `GCP_SA_KEY`.
3. `gcloud run deploy --source .` — Buildpacks build & push the image.
4. Cloud Run rolls out the revision and keeps the public URL unchanged.

> Public URL format: `https://wasteassistant‑xxxxx.a.run.app`

### GitHub Secrets required by the workflow

| Name                 | Purpose                                                  |
| -------------------- | -------------------------------------------------------- |
| **GCP\_SA\_KEY**     | JSON key with roles: Artifact Registry, Cloud Build, Run |
| **GCP\_PROJECT\_ID** | e.g. `gpt-models-436109`                                 |
| **GCP\_REGION**      | e.g. `europe-north1`                                     |

### Runtime secrets (Secret Manager)

`OPENAI_API_KEY` and `FLASK_SECRET_KEY` are **not stored in GitHub**. They live in **Google Cloud Secret Manager** and are injected by Cloud Run as environment variables.

```bash
# Create the secrets
echo -n "sk-…" | gcloud secrets create OPENAI_API_KEY --data-file=-
openssl rand -hex 32 | gcloud secrets create FLASK_SECRET_KEY --data-file=-

# Allow Cloud Run’s runtime SA to read them
PROJECT_ID="gpt-models-436109"
PROJECT_NUM=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
RUN_SA="${PROJECT_NUM}-compute@developer.gserviceaccount.com"

for SEC in OPENAI_API_KEY FLASK_SECRET_KEY; do
  gcloud secrets add-iam-policy-binding $SEC \
    --member="serviceAccount:${RUN_SA}" \
    --role="roles/secretmanager.secretAccessor"
done
```

The workflow maps the latest secret versions to env‑vars:

```yaml
secrets: |
  OPENAI_API_KEY=projects/${{ secrets.GCP_PROJECT_ID }}/secrets/OPENAI_API_KEY:latest
  FLASK_SECRET=projects/${{ secrets.GCP_PROJECT_ID }}/secrets/FLASK_SECRET_KEY:latest
```

The app then reads them with `os.getenv("api_key")` and `os.getenv("secret_key")`.

---

## 🤝 Contributing

Pull requests are welcome!

1. Fork → branch → commit with clear messages.
2. Push and open a PR against ``.
3. CI will build & deploy the preview automatically.

Found a bug or have an idea? Open an issue.

---

## 📄 License

Apache‑2.0 — see `LICENSE` for full text.

