from flask import Flask, request, Response, jsonify
import os
import re
import markdown2
import google.generativeai as genai
from dotenv import load_dotenv
import instructor
from pydantic import BaseModel, Field

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash')
client = instructor.from_gemini(
    client=genai.GenerativeModel(
        model_name="models/gemini-1.5-flash",
    ),
    mode=instructor.Mode.GEMINI_JSON,
)

class GoogleDocsNotes(BaseModel):
    title: str = Field(description="Title of the class session")
    summary: str = Field(description="Brief summary of the class content")
    notes_content: str = Field(description="Detailed notes content in markdown format")

def generate_class_notes(transcript: str, attempt: int) -> GoogleDocsNotes:
    system_prompt = """
    You are an AI assistant that generates comprehensive class notes from a given transcript.
    The notes should be formatted in markdown.
    """

    descriptor = ["detailed", "", "brief"][attempt]

    user_prompt = f"""
    Please analyze the following class transcript and generate {descriptor} notes:

    {transcript}

    Create well-structured notes with the following guidelines:
    1. Use a clear hierarchy with headers and subheaders (use # for main headers, ## for subheaders, etc.)
    2. Include timestamps for all bullets in your notes (format: [HH:MM:SS] or [MM:SS] or [H:MM:SS])
    3. Use bullet points for lists
    4. Bold important terms or concepts
    5. Include a brief summary at the beginning

    Format the notes in markdown so they can be easily converted to HTML.

    Make sure NOT to exceed the output limit.
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_model=GoogleDocsNotes
    )

    return response

def timestamp_to_seconds(timestamp):
    parts = timestamp.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    else:
        return 0  # Return 0 for invalid formats

def create_html_content(notes: GoogleDocsNotes, base_url: str):
    def replace_timestamp(match):
        timestamp = match.group(1)
        seconds = timestamp_to_seconds(timestamp)
        return f'<a href="{base_url}&start={seconds}" target="_blank">[{timestamp}]</a>'

    # Replace timestamps in the markdown content
    notes_content_with_links = re.sub(r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]', replace_timestamp, notes.notes_content)

    # Convert markdown to HTML
    html_content = markdown2.markdown(notes_content_with_links)

    # Create full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{notes.title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>{notes.title}</h1>
        <div class="summary">
            <h2>Summary</h2>
            <p>{notes.summary}</p>
        </div>
        <div class="notes-content">
            {html_content}
        </div>
    </body>
    </html>
    """
    return full_html

@app.route('/generate_notes', methods=['POST'])
def generate_notes():
    app.logger.info('Received request to /generate_notes')
    try:
        data = request.get_json(force=True)
        app.logger.info(f'Received data: {data}')

        transcript = data.get('transcript')
        base_url = data.get('base_url')


        max_attempts = 3
        html_content = None

        for attempt in range(1, max_attempts + 1):
            try:
                html_content = create_html_content(generate_class_notes(transcript, attempt), base_url)
                break  # If successful, exit the loop
            except Exception as e:
                print(f"Attempt {attempt} failed: {str(e)}")
                if attempt == max_attempts:
                    print("All attempts failed.")
                    raise  # Re-raise the last exception if all attempts fail

        if html_content is not None:
            # Use html_content here
            print("HTML content created successfully.")
        else:
            print("Failed to create HTML content after all attempts.")
        return Response(html_content, mimetype='text/html')

    except:
        print(f'Bad request')
        return "Bad Request", 400

if __name__ == '__main__':
    app.run(debug=True)