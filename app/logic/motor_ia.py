from app import db
from app.models.progresoUsuario import ProgresoUsuario

class MotorIA:
    def __init__(self):
        self.UMBRAL_MAESTRIA = 0.85
        self.UMBRAL_REFUERZO = 0.60
        self.MINIMO_EJERCICIOS = 5

        self.MAPA_RUTAS = {
        1: "Fundamentos del Álgebra",
        2: "Lenguaje Algebraico",
        3: "Operaciones con Polinomios",
        4: "Factorización",
        5: "Ecuaciones de Primer Grado",
        6: "Sistemas de Ecuaciones",
        7: "Ecuaciones de Segundo Grado",
        8: "Desigualdades",
        9: "Funciones",
        10: "Exponentes y Radicales",
        11: "Expresiones Racionales",
        12: "Logaritmos"
    }

    # 1. ERROR CORREGIDO: Se añadió 'self' y se eliminó el código del controlador de aquí
    def decidir_accion(self, total_ejercicios, aciertos):
        if total_ejercicios == 0:
            return "INICIO_DIAGNOSTICO"
        
        precision = aciertos / total_ejercicios
        
        if precision >= self.UMBRAL_MAESTRIA and total_ejercicios >= self.MINIMO_EJERCICIOS:
            return "AVANZAR"
        if precision < self.UMBRAL_REFUERZO:
            return "REFORZAR"
        
        return "MANTENER"

    def generar_configuracion_ejercicios(self, nivel_texto, accion_ia):
        config = {
            'cantidad': 5,
            'dificultad': 'media',
            'tipo_ayuda': 'estándar'
        }

        if nivel_texto == "Principiante":
            config['cantidad'] = 5
            config['dificultad'] = 'fácil'
        elif nivel_texto == "Intermedio":
            config['cantidad'] = 8
            config['dificultad'] = 'media'
        else: # Avanzado
            config['cantidad'] = 12
            config['dificultad'] = 'difícil'

        if accion_ia == "REFORZAR":
            config['cantidad'] += 2
            config['dificultad'] = 'fácil'
            config['tipo_ayuda'] = 'tutor_activo'
        
        return config

    def obtener_siguiente_tema(self, tema_actual):
        return self.MAPA_RUTA.get(tema_actual, "Ruta Completada")

    def obtener_nivel_texto(self, temas_completados):
        if temas_completados >= 15: return "Avanzado"
        elif temas_completados >= 7: return "Intermedio"
        else: return "Principiante"