import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

# Create the model
generation_config = {
  "temperature": 0.75,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
  system_instruction="You are an AI trained to process construction-related documents. \n            Extract the following information from the text below into a structured JSON format:\n\n            - Plankopf: (it is in bottom right corner of the photo) \n                - Planschlüssel (Plan ID)\n                - Stat.Pos\n                - Auft. Nr\n                - Index (You can get this from the planschlussel string as the  before last alphabet)\n                - Fertigteil Position\n                - Stück\n                - Volumen (m3)\n                - Gewicht (to)\nReturn only the JSON object, structured like this:\n            {\n                \"Plankopf\": {{\n                    \"Planschlüssel\": \"\",\n                    \"Stat.Pos\": \"\",\n                    \"Auftr. Nr\":\"\",\n                    \"Index\":\"\",\n                    \"Fertigteil Position\":\"\",\n                    \"Stück\": 0,\n                    \"Volumen (m3)\": 0.0,\n                    \"Gewicht (to)\": 0.0\n                }}\n}\n",
)

# TODO Make these files available on the local file system
# You may need to update the file paths
files = [
  upload_to_gemini("", mime_type="image/jpeg"),
  upload_to_gemini("", mime_type="image/png"),
]

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        files[0],
      ],
    },
    {
      "role": "model",
      "parts": [
        "json\n{\n    \"Plankopf\": {\n        \"Planschlüssel\": \"FT_XX_13-005_e_F\",\n        \"Stat.Pos\": \"-\",\n        \"Auftr. Nr\": \"819-19\",\n         \"Index\":\"e\",\n        \"Fertigteil Position\": \"13-005\",\n        \"Stück\": 1,\n        \"Volumen (m3)\": 3.69,\n        \"Gewicht (to)\": 9.23\n    }\n}\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        files[1],
      ],
    },
    {
      "role": "model",
      "parts": [
        "json\n{\n    \"Plankopf\": {\n        \"Planschlüssel\": \"FT_XX_10-103_a_F\",\n        \"Stat.Pos\": \"W01\",\n        \"Auftr. Nr\": \"819-19\",\n        \"Index\": \"a\",\n        \"Fertigteil Position\": \"10-103\",\n        \"Stück\": 4,\n        \"Volumen (m3)\": 4.75,\n        \"Gewicht (to)\": 11.88\n    }\n}\n",
      ],
    },
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

print(response.text)