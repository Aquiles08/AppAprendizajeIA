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

    # --- MÉTODO MODIFICADO: Ahora acepta preferencias de perfil ---
    def generar_ejercicios_ia(self, tema, dificultad, cantidad=5, tutor_mode='paciente'):
        # Ajustamos la instrucción de la explicación según el perfil
        instruccion_modo = ""
        if tutor_mode == 'directo':
            instruccion_modo = "La explicación debe ser técnica, breve y directa al grano."
        elif tutor_mode == 'retador':
            instruccion_modo = "La explicación debe dar pistas y conceptos clave en lugar de resolverlo todo."
        else: # paciente
            instruccion_modo = "La explicación debe ser muy detallada, paso a paso, con un lenguaje motivador y claro."

        prompt = f"""
        Genera {cantidad} ejercicios de matemáticas sobre el tema '{tema}' 
        con dificultad '{dificultad}'.
        
        Instrucción de estilo: {instruccion_modo}

        Responde ÚNICAMENTE en formato JSON con la siguiente estructura de lista:
        [
            {{
                "pregunta": "ecuación o problema",
                "solucion": "solo el valor numérico",
                "explicacion": "redacta según la instrucción de estilo"
            }}
        ]
        No incluyas texto extra fuera del JSON.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            texto_limpio = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(texto_limpio)
        
        except Exception as e:
            print(f"❌ Error en IA Service (Generar): {e}")
            return []

    def analizar_error_pedagogico(self, tema, preguntas_fallidas):
        if not preguntas_fallidas:
            return "Ninguno"

        prompt = f"""
        Actúa como un experto en pedagogía matemática. 
        Un estudiante falló los siguientes ejercicios del tema '{tema}':
        {preguntas_fallidas}

        ¿Cuál es la causa más probable del error? 
        Responde ÚNICAMENTE con una o dos palabras de esta lista:
        - Signos
        - Despeje
        - Jerarquía de operaciones
        - Aritmética básica
        - Concepto base
        - Fórmulas
        """
        
        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            error_identificado = response.text.strip()
            return error_identificado[:50] 
        except Exception as e:
            print(f"❌ Error analizando error: {e}")
            return "Indeterminado"

    # --- NUEVO MÉTODO: Para el Tutor IA Personalizado del Perfil ---
    def obtener_respuesta_tutor(self, mensaje_usuario, tutor_mode='paciente', enfoques=''):
        """
        Este método servirá para el botón de 'Tutor IA' usando la personalidad elegida.
        """
        estilos = {
            'paciente': "Eres un tutor paciente. Explica con manzanas, paso a paso y anima al alumno.",
            'directo': "Eres un tutor eficiente. Da respuestas cortas, precisas y fórmulas directas.",
            'retador': "Eres un tutor socrático. No des la respuesta, responde con preguntas que guíen al alumno."
        }
        
        contexto = estilos.get(tutor_mode, estilos['paciente'])
        contexto_temario = f"""
            Actúa basándote en el temario oficial de Álgebra de Blossom:
            1. Fundamentos, 2. Lenguaje Algebraico, 3. Polinomios, 4. Factorización, 
            5. Ecuaciones 1er Grado, 6. Sistemas, 7. Ecuaciones 2do Grado, 8. Desigualdades, 
            9. Funciones, 10. Exponentes y Radicales, 11. Expresiones Racionales, 12. Logaritmos.
    
            El estudiante está enfocado actualmente en: {enfoques if enfoques else 'Temas generales de álgebra'}.
            Prioriza estos temas en tus ejemplos.
            """
        
        prioridad = f" El usuario tiene especial interés en: {enfoques}." if enfoques else ""
        
        prompt = f"""
            {contexto}
            {prioridad}
            {contexto_temario}
            Usa el temario oficial de Álgebra (Fundamentos, Polinomios, Factorización, Ecuaciones, etc.) para tus explicaciones.
            Pregunta del alumno: {mensaje_usuario}
            """
        
        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            return response.text
        except Exception as e:
            print(f"❌ ERROR REAL: {e}")
            return f"Lo siento, hubo un error conectando con mi cerebro de IA: {e}"