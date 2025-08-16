import os
from dotenv import load_dotenv
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from PIL import Image
import io
import base64
from transformers import pipeline

# Load environment variables (for local testing, Render handles them securely)
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in .env file")

genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# Initialize Hugging Face OCR pipeline
# Using 'microsoft/trocr-base-handwritten' for general text recognition
# For mathematical expressions, a more specialized model might be needed,
# but this can serve as a starting point for general text in images.
ocr_pipeline = pipeline("image-to-text", model="microsoft/trocr-base-handwritten")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression')

    if not expression:
        return jsonify({"error": "No expression provided"}), 400

    system_prompt = """You are CalcGPT, a friendly calculator that gives quick, concise answers.
    Keep responses under 4 short paragraphs total.
    Use simple language and be encouraging but brief.
    Format: Quick greeting -> Result -> Brief explanation -> Short tip/encouragement
    """
    user_prompt = f"""Expression: {expression}
    Give me a quick analysis with:
    - The result
    - A simple explanation in 2-3 sentences
    - One quick helpful tip
    Be concise and friendly!
    """

    try:
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = gemini_model.generate_content(combined_prompt)
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({"error": "No image data provided"}), 400

    try:
        # Decode base64 image
        header, encoded = image_data.split(",", 1)
        binary_data = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(binary_data)).convert("RGB")

        # Use Hugging Face model to extract text
        extracted_text = ocr_pipeline(image)[0]['generated_text']

        if not extracted_text:
            return jsonify({"result": "No text or mathematical expression could be extracted from the image. Please try a clearer image."})

        # Send extracted text to Gemini for analysis
        system_prompt = """You are CalcGPT, a friendly calculator that gives quick, concise answers.
        You have received text extracted from an image. Analyze it for mathematical problems or concepts.
        Keep responses under 4 short paragraphs total.
        Use simple language and be encouraging but brief.
        Format: Quick greeting -> Analysis/Result -> Brief explanation -> Short tip/encouragement
        """
        user_prompt = f"""Extracted text from image: "{extracted_text}"
        Analyze this text for mathematical problems or concepts.
        Give me a quick analysis with:
        - The result/solution (if applicable)
        - A simple explanation in 2-3 sentences
        - One quick helpful tip
        Be concise and friendly!
        """
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = gemini_model.generate_content(combined_prompt)
        return jsonify({"result": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
