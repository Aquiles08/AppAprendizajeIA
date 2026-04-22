from google import genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # Usamos el nuevo Client con tu llave del .env
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        # Actualizamos al modelo que sí tienes disponible
        self.model_id = "gemini-2.5-flash"

    def generar_ejercicios_ia(self, tema, dificultad, cantidad=5):
        prompt = f"""
        Genera {cantidad} ejercicios de matemáticas sobre el tema '{tema}' 
        con dificultad '{dificultad}'.
        Responde ÚNICAMENTE en formato JSON con la siguiente estructura de lista:
        [
            {{
                "pregunta": "ecuación o problema",
                "solucion": "solo el valor numérico",
                "explicacion": "paso a paso breve"
            }}
        ]
        No incluyas texto extra fuera del JSON.
        """
        
        try:
            # Nueva forma de llamar al contenido
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            # Limpieza de markdown
            texto_limpio = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(texto_limpio)
        
        except Exception as e:
            print(f"❌ Error en IA Service: {e}")
            return []