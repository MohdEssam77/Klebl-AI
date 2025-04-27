import os
import google.generativeai as genai

def configure_gemini():
    """Configure Gemini API with environment variable."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=api_key)

def upload_to_gemini(path, mime_type="image/png"):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def get_model():
    """Create and configure the Gemini model."""
    generation_config = {
        "temperature": 0.85,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }
    
    system_instruction = """You are an AI trained to process construction-related documents.
            Extract the following information from the text below into a structured JSON format:
            - Seitenansicht/Draufsicht:
                - Bauteil:
                    - Breite (it is mostly on the side of the diagram which is the height from the viewer's point of view)
            
            Return only the JSON object, structured like this:
            {
                "Seitenansicht_Draufsicht": {
                    "Bauteil": {
                        "Breite": 0.0
                    }
                }
            }"""
    
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

def process_draufsicht_image(image_path):
    """
    Process an elevation/plan view image using Gemini API and return structured JSON data.
    
    Args:
        image_path (str): Path to the elevation/plan view image file
        
    Returns:
        str: JSON response from Gemini containing view dimensions
    """
    try:
        # Configure Gemini
        configure_gemini()
        
        # Upload the image
        image_file = upload_to_gemini(image_path)
        
        # Get the model
        model = get_model()
        
        # Initialize chat with historical context
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [image_file],
                }
            ]
        )
        
        # Get response
        response = chat_session.send_message("Please extract the component width from this elevation/plan view.")
        
        return response.text
        
    except Exception as e:
        print(f"Error processing view image: {str(e)}")
        raise

def main():
    """Main function for testing."""
    try:
        # Example usage
        image_path = r"plancir\cropped_sections\Draufsicht.png"
        result = process_draufsicht_image(image_path)
        print("Processed Result:")
        print(result)
        
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()