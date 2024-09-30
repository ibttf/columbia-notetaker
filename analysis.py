import os
import google.generativeai as genai
from dotenv import load_dotenv
import instructor
from pydantic import BaseModel, Field

load_dotenv("/Users/neel/Documents/vidnotes/.env")

model = genai.GenerativeModel('gemini-1.5-flash')
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

client = instructor.from_gemini(
    client=genai.GenerativeModel(
        model_name="models/gemini-1.5-flash",
    ),
    mode=instructor.Mode.GEMINI_JSON,
)

class LatexNotes(BaseModel):
    summary: str = Field(description="Brief summary of the class content")
    latex_content: str = Field(description="Complete LaTeX content for the class notes")

def generate_class_notes(transcript: str) -> LatexNotes:
    system_prompt = """
    You are an AI assistant that generates comprehensive class notes in LaTeX format from a given transcript.
    Analyze the transcript carefully and extract the most important information.
    """
    
    user_prompt = f"""
    Please analyze the following class transcript and generate detailed notes in LaTeX format:

    {transcript}

    Make sure to include timestamp categories.
    Create a well-structured LaTeX document with brief notes from the transcript.
    Include timestamps from the video for major sections/headers in your notes.

    
    Use appropriate LaTeX commands and environments to structure the document.
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_model=LatexNotes
    )

    return response

def main():
    print("Welcome to the Class Notes Generator!")
    
    while True:
        file_name = input("Please enter the name of the text file containing your class transcript: ")
        
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r') as file:
                    transcript = file.read()
                break
            except Exception as e:
                print(f"Error reading the file: {e}")
                print("Please try again.")
        else:
            print("File not found. Please make sure the file exists and try again.")
    
    print("\nGenerating class notes... This may take a moment.")
    notes = generate_class_notes(transcript)
    
    print("\nClass notes generated successfully!")
    
    # Save LaTeX content to a file
    output_filename = "linguistics_notes.tex"
    with open(output_filename, 'w') as f:
        f.write(notes.latex_content)
    
    print(f"\nLaTeX file saved as: {output_filename}")
    print("You can now compile this file using your preferred LaTeX compiler.")

if __name__ == "__main__":
    main()