import os
from dotenv import load_dotenv
import google.generativeai as genai
from flask import Flask, request, jsonify

# Load environment variables (for local testing, Render handles them securely)
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in .env file")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

app = Flask(__name__)

@app.route('/')
def home():
    return "CalcGPT AI API is running. Use /calculate for AI help."

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
        response = model.generate_content(combined_prompt)
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
