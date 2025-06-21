# Waste Assistant Chatbot for Jyväskylä

This project is a chatbot designed to assist new residents and immigrants in Jyväskylä, Finland, with waste sorting. Finland's waste sorting system can be challenging for newcomers, especially in a city like Jyväskylä with its specific local regulations. This chatbot provides an easy way to get answers about waste sorting and can even analyze photos of waste items to suggest the correct disposal method.

## Features

- Answers questions about waste sorting specific to Jyväskylä.
- Analyzes uploaded images of waste items to recommend proper disposal.
- Supports both **English** and **Finnish** languages.
- Powered by OpenAI's GPT-4o-mini for natural language processing and image analysis.
- Deployed on **Google Cloud Run** for scalability and accessibility.

## Technologies Used

- **Python**: Core programming language.
- **Flask**: Web framework for the chatbot interface.
- **OpenAI API**: Enables natural language understanding and image processing.
- **Google Cloud Run**: Hosts the application in a serverless environment.
- **Google Cloud Build**: Automates building the Docker image.
- **GitHub Actions**: Handles continuous deployment.
- **Docker**: Containerizes the application for consistency.

## Setup and Installation

To run the project locally, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/waste-assistant.git
   ```

2. **Navigate to the project directory**:

   ```bash
   cd waste-assistant
   ```

3. **Create a virtual environment**:

   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

5. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

6. **Set up environment variables**:

   - Create a `.env` file in the project root.
   - Add the following (replace with your own keys):

     ```
     api_key=YOUR_OPENAI_API_KEY
     secret_key=YOUR_FLASK_SECRET_KEY
     ```

7. **Run the application**:

   ```bash
   python app.py
   ```

   The chatbot will be available at `http://localhost:8086`.

## Usage

- Open a browser and go to `http://localhost:8086`.
- Use the chat interface to:
  - Ask questions about waste sorting (e.g., "Where do I throw plastic bags?").
  - Upload an image of a waste item for analysis.
- The chatbot will respond with instructions tailored to Jyväskylä's waste sorting rules.
- Switch between English and Finnish via the interface (defaults to English).

## How It Works

### Code Overview

- **Flask App**: The `app.py` file sets up a Flask web server with routes for the homepage (`/`), asking questions (`/ask`), and resetting the conversation (`/reset`).
- **OpenAI Integration**: Uses the `gpt-4o-mini` model to process text queries and analyze images. Instructions specific to Jyväskylä's waste sorting rules are loaded from text files (`gpt_instructions_en.txt`, `gpt_instructions_fi.txt`, etc.).
- **Image Processing**: Uploaded images are compressed using PIL and converted to base64 for OpenAI's image analysis.
- **Session Management**: Flask-Session stores conversation history in the filesystem, with a 30-minute timeout.
- **Language Support**: Dynamically selects English or Finnish instructions based on user preference.

### Deployment

The project is deployed to Google Cloud Run using a GitHub Actions workflow:

- **Workflow**: Defined in `.github/workflows/deploy.yml`.
- **Trigger**: Runs on every push to the `main` branch or manually via the "Run workflow" button.
- **Steps**:
  1. Checks out the repository.
  2. Authenticates to Google Cloud using a service account key stored in GitHub secrets (`GCP_SA_KEY`).
  3. Builds a Docker image with Cloud Build and deploys it to the `wasteassistant` service on Cloud Run.
- **Access**: The deployed app is publicly accessible at `https://wasteassistant-XXXXX.a.run.app` (URL varies by deployment).

## Contributing

Contributions are welcome! To contribute:

- Fork the repository.
- Create a branch for your feature or fix.
- Commit your changes with clear messages.
- Push to your fork and submit a pull request to the `main` branch.