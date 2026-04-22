from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=api_key)

print("--- Probando con Gemini 2.5 (El modelo de tu lista) ---")

try:
    # Usamos exactamente uno de los nombres que te salieron en la lista
    # pero sin el prefijo 'models/'
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents="Hola, genera una ecuación lineal de un paso y su solución para Blossom."
    )

    print("\n✅ ¡POR FIN FUNCIONA!")
    print("RESPUESTA DE IA:")
    print(response.text)

except Exception as e:
    print(f"\n❌ Error: {e}")