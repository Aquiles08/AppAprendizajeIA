import random

class GeneradorEjercicios:
    def __init__(self):
        self.operaciones = ['+', '-']

    def generar_ecuacion_lineal(self, dificultad):
        """
        Crea una ecuación de primer grado y devuelve un diccionario con 
        el texto del problema y la solución correcta.
        """
        # --- NIVEL FÁCIL: x + a = b ---
        if dificultad == 'fácil':
            x = random.randint(1, 10) # La respuesta
            a = random.randint(1, 15)
            operador = random.choice(self.operaciones)
            
            if operador == '+':
                resultado = x + a
                texto = f"x + {a} = {resultado}"
            else:
                resultado = x - a
                texto = f"x - {a} = {resultado}"
            
            return {"pregunta": texto, "solucion": str(x)}

        # --- NIVEL MEDIO: ax + b = c ---
        elif dificultad == 'media':
            x = random.randint(1, 12)
            a = random.randint(2, 5)
            b = random.randint(1, 20)
            
            c = (a * x) + b
            texto = f"{a}x + {b} = {c}"
            
            return {"pregunta": texto, "solucion": str(x)}

        # --- NIVEL DIFÍCIL: a(x + b) = c ---
        else:
            x = random.randint(1, 15)
            a = random.randint(2, 6)
            b = random.randint(2, 10)
            
            c = a * (x + b)
            texto = f"{a}(x + {b}) = {c}"
            
            return {"pregunta": texto, "solucion": str(x)}

    def crear_sesion(self, config):
        """
        Crea una lista completa de ejercicios basada en la config de la IA.
        """
        lista_ejercicios = []
        for _ in range(config['cantidad']):
            ejercicio = self.generar_ecuacion_lineal(config['dificultad'])
            lista_ejercicios.append(ejercicio)
        
        return lista_ejercicios