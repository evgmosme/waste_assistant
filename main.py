from flask import Flask, request, jsonify, render_template, session
import openai
import os
from dotenv import load_dotenv
from flask_session import Session  # Import Flask-Session
from datetime import timedelta  # For session timeout
import base64
from PIL import Image
import io
import tiktoken

# Load environment variables from .env file
load_dotenv()

# Fetch API key and secret key from .env
api_key = os.getenv('api_key')
secret_key = os.getenv('secret_key')

app = Flask(__name__)

# Set the secret key for session management
if not secret_key:
    raise ValueError("No secret key set in the environment variables.")
app.secret_key = secret_key

# Configure Flask-Session to use filesystem-based sessions (or Redis)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False  # Make session non-permanent
app.config['SESSION_FILE_DIR'] = './flask_session'  # Directory to store session files
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Expire session after 30 mins of inactivity
Session(app)

# Initialize the OpenAI client with your API key
client = openai.OpenAI(api_key=api_key)

# Load waste management instructions in both English and Finnish
with open('./model_instructions/gpt_instructions_en.txt', 'r') as file:
    instructions_en = file.read()

with open('./model_instructions/gpt_instructions_fi.txt', 'r') as file:
    instructions_fi = file.read()

with open('./model_instructions/waste_management_instructions_en.txt', 'r') as file:
    waste_sorting_instructions_en = file.read()

with open('./model_instructions/waste_management_instructions_fi.txt', 'r') as file:
    waste_sorting_instructions_fi = file.read()

# Define a function to get the correct instructions based on language
def get_instructions(language):
    if language == 'fi':
        return f"""
        {instructions_fi}
        """
    else:
        return f"""
        {instructions_en}
        """

@app.route('/')
def home():
    return render_template('index.html')

def compress_image(image, max_size=(500, 500), quality=75):
    """Compresses an image to a specified size and quality."""
    img = Image.open(image)

    # Resize the image if it's larger than the max size
    img.thumbnail(max_size, Image.Resampling.LANCZOS)  # Use LANCZOS for high-quality downsampling

    # Save the image to a BytesIO object to preserve it in memory
    img_io = io.BytesIO()

    # Compress the image (reduce quality for smaller size)
    img.save(img_io, format='JPEG', quality=quality)

    # Reset the file pointer to the beginning
    img_io.seek(0)
    return img_io

def count_tokens(messages, model="gpt-4o-mini"):
    # Load the tokenizer for the model (gpt-4o-mini uses GPT-4's tokenizer)
    encoding = tiktoken.encoding_for_model(model)

    tokens_per_message = 0

    for message in messages:
        content = message['content']

        # If the content is a list (as with image submissions), extract the text part
        if isinstance(content, list):
            # Extract text content from the list (assuming it has 'text' and 'image_url' keys)
            text_content = next((item['text'] for item in content if 'text' in item), "")
            tokens_per_message += len(encoding.encode(text_content))
        elif isinstance(content, str):
            # If it's a string, directly encode and count tokens
            tokens_per_message += len(encoding.encode(content))

    return tokens_per_message

@app.route('/ask', methods=['POST'])
def ask():
    query = request.form.get('query')
    
    if not query and 'image' not in request.files:
        return jsonify({"error": "No query or image provided"}), 400

    # Check if 'language' is set in the session
    if 'language' not in session:
        session['language'] = request.form.get('language', 'en')

    # Initialize conversation memory for the current session if it doesn't exist
    if 'conversation' not in session:
        session['conversation'] = []  # New conversation for each session

    # Add user's text query to the conversation if provided
    if query:
        session['conversation'].append({"role": "user", "content": query})

    # Get the appropriate instructions based on the language
    instruction = get_instructions(session['language'])

    # Prepare the full message with system instructions and conversation history
    full_message = [
        {"role": "system", "content": instruction}  # Add instructions for every query
    ] + session['conversation']  # Add conversation history

    # Check if an image was uploaded and process it correctly
    if 'image' in request.files:
        image = request.files['image']

        # Compress the image before sending
        compressed_image = compress_image(image)

        # Convert the compressed image to base64
        image_base64 = base64.b64encode(compressed_image.read()).decode('utf-8')

        # Add the base64 encoded image as part of the user's message
        full_message.append({
            "role": "user",
            "content": [
                {"type": "text", "text": query if query else "Image provided."},  # Text part (optional)
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                        "detail": "low"
                        }
                }
            ]
        })
    else:
        # If no image, just proceed with the user query
        full_message.append({
            "role": "user",
            "content": query
        })

    # Count tokens in full_message
    # token_count = count_tokens(full_message) + 85
    # print(f"Total tokens used: {token_count}")  # Print the token count

    # Use the OpenAI client to perform the chat completion (including instructions + conversation history)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=full_message,
        temperature=1,
        max_tokens=400
    )

    # Extract the assistant's response
    answer = response.choices[0].message.content
    print(response)

    # Append the assistant's response to the conversation
    session['conversation'].append({"role": "assistant", "content": answer})

    # Return the assistant's answer
    return jsonify(answer)

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Endpoint to reset the conversation memory."""
    session.clear()  # Clears the session fully (both conversation and any persistent data)
    return jsonify({"message": "Conversation reset."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8086)
    # app.run