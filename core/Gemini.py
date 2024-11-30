import google.generativeai as genai
import json

api_key = json.loads(open("core/API_KEYS.json").read())["gemini_api_key"]
genai.configure(api_key=api_key)

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("What does the fox say?")
print(response.text)