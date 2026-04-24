from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify 
from config.database import db # Importamos la instancia de SQLAlchemy para hacer consultas a la DB
from app.utils import bcrypt # Importamos bcrypt para verificar contraseñas
from google import genai # Importamos el cliente de Gemini para generar ejercicios personalizados
import os
from datetime import datetime

#Modelos
from app.models.tema import Tema # Importamos el modelo Tema para hacer consultas a la tabla de temas
from app.models.usuario import Usuario # Importamos el modelo Usuario para hacer consultas a la tabla de usuarios
from app.models.curso import Curso # Importamos el modelo Curso para hacer consultas a la tabla de cursos
from app.models.respuesta import Respuesta # Importamos el modelo Respuesta para guardar las respuestas del examen
from app.models.progresoUsuario import ProgresoUsuario # Importamos el modelo ProgresoUsuario para guardar el progreso de los usuarios
from app.models.historialTutor import HistorialTutor # Importamos el modelo HistorialTutor para guardar el historial de conversaciones con el tutor IA
from app.models.evaluacion import Evaluacion # Importamos el modelo Evaluacion para guardar los resultados de los exámenes
from app.models.progresoTema import ProgresoTema # Importamos el modelo ProgresoTema para guardar el progreso de cada tema
from app.models.progresoSubtema import ProgresoSubtema # Importamos el modelo ProgresoSubtema para guardar el progreso de cada subtema

#Servicios y lógica
from app.services.ia_service import AIService # Importamos el servicio de IA para generar ejercicios personalizados
from app.services.usuario_service import UsuarioService # Importamos el servicio de usuario para manejar la lógica de negocio relacionada con los usuarios
from app.logic.motor_ia import MotorIA # Importamos el motor de IA para tomar decisiones en la ruta de práctica
from app.logic.generador import GeneradorEjercicios # Importamos el generador de ejercicios para crear problemas matemáticos personalizados

ia_service = AIService() # Creamos una instancia del servicio de IA para usarlo en las rutas
usuario_bp = Blueprint('usuario', __name__)
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY')) # Creamos el cliente de Gemini
generador_local = GeneradorEjercicios() # Creamos una instancia del generador local para usarlo como respaldo en caso de que Gemini falle

# --- LOGIN --- 
@usuario_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo")
        password_candidata = request.form.get("contrasena")
        
        user = Usuario.query.filter_by(correo=correo).first()
        
        if user and bcrypt.check_password_hash(user.contrasena, password_candidata):
            #Guardamos el ID real de la base de datos en las sesion 
            session['usuario_id'] = user.id_usuario
            session['usuario_nombre'] = user.nombre
            session['tipo_usuario'] = user.tipo_usuario
            
            # Redirección basada en el tipo de usuario
            if user.tipo_usuario.lower() == 'docente':
                return redirect(url_for('usuario.dashboard_docente'))
            else:
                return redirect(url_for('usuario.dashboard'))
            
        else:
            flash("Correo o contraseña incorrectos. Inténtalo de nuevo.")
            return redirect(url_for('usuario.login'))
            
    return render_template("login.html")

# --- REGISTRAR ---
@usuario_bp.route("/registrar")
def registro():
    return render_template("registro.html")

# --- Crear Cuenta ---
@usuario_bp.route("/crear_cuenta", methods=["POST"])
def crear_cuenta():
    nombre = request.form.get("nombre")
    correo = request.form.get("correo")
    password = request.form.get("contrasena") 
    tipo_usuario = request.form.get("tipo_usuario")

    # Validacion. Buscamos si ya hay alguien con ese correo en la DB
    usuario_existente = Usuario.query.filter_by(correo=correo).first()
    
    if usuario_existente:
        # Si ya existe, detenemos el proceso y le avisamos al usuario
        return "Este correo ya está registrado. Por favor, intenta con otro o inicia sesión."

    # Si el correo es nuevo, continuamos normal:
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    nuevo_usuario = Usuario(
        nombre=nombre, 
        correo=correo, 
        contrasena=password_hash,
        tipo_usuario=tipo_usuario 
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return redirect(url_for('usuario.login'))

# --- EDITAR ---
@usuario_bp.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    user = Usuario.query.get_or_404(id)
    if request.method == "POST":
        user.nombre = request.form.get("nombre")
        user.correo = request.form.get("correo")
        db.session.commit()
        return redirect(url_for('usuario.dashboard'))
    return render_template("editar_perfil.html", user=user)

# --- ELIMINAR ---
@usuario_bp.route("/usuario/eliminar/<int:id>", methods=["POST"])
def eliminar_usuario(id):
    user = Usuario.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('usuario.login'))


# --- RUTAS DEL DASHBOARD ESTUDIANTE---

# --- Dashboard ---
@usuario_bp.route("/dashboard")
def dashboard():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))
    
    # Objetivo: Mostrar estadísticas reales del usuario en el dashboard 
    user = Usuario.query.get(u_id)  
    historial = ProgresoUsuario.query.filter_by(usuario_id=u_id).order_by(ProgresoUsuario.fecha.desc()).limit(5).all()
    
    total_ejercicios = sum(p.ejercicios_realizados for p in historial)
    total_aciertos = sum(p.aciertos for p in historial)
    
    return render_template("dashboard.html", user=user, 
                           historial=historial, 
                           total_ejercicios=total_ejercicios, 
                           total_aciertos=total_aciertos)

#--- Examen ---
@usuario_bp.route("/examen")
def examen():
    # Definimos las 12 preguntas basadas exactamente en tu temario
    preguntas_algebra = [
        {"id": 1, "tema": "Fundamentos del Álgebra", "texto": "¿Cuál es el resultado de 10 - 2 * 3 + 4?", "opciones": [{"id": "A", "texto": "28"}, {"id": "B", "texto": "8"}, {"id": "C", "texto": "12"}]},
        {"id": 2, "tema": "Lenguaje Algebraico", "texto": "Traduce a lenguaje algebraico: 'El triple de un número aumentado en 7'", "opciones": [{"id": "A", "texto": "3x + 7"}, {"id": "B", "texto": "x³ + 7"}, {"id": "C", "texto": "3(x + 7)"}]},
        {"id": 3, "tema": "Operaciones con Polinomios", "texto": "Simplifica: (5x² - 3x) + (2x² + 8x)", "opciones": [{"id": "A", "texto": "7x² + 5x"}, {"id": "B", "texto": "7x² - 11x"}, {"id": "C", "texto": "10x² + 5x"}]},
        {"id": 4, "tema": "Factorización", "texto": "Factoriza x² - 25", "opciones": [{"id": "A", "texto": "(x-5)(x-5)"}, {"id": "B", "texto": "(x+5)(x-5)"}, {"id": "C", "texto": "x(x-25)"}]},
        {"id": 5, "tema": "Ecuaciones de Primer Grado", "texto": "Resuelve: 2x + 10 = 20", "opciones": [{"id": "A", "texto": "x = 5"}, {"id": "B", "texto": "x = 15"}, {"id": "C", "texto": "x = 10"}]},
        {"id": 6, "tema": "Sistemas de Ecuaciones", "texto": "En el sistema {x + y = 5, x - y = 1}, ¿cuánto vale x?", "opciones": [{"id": "A", "texto": "x = 2"}, {"id": "B", "texto": "x = 3"}, {"id": "C", "texto": "x = 4"}]},
        {"id": 7, "tema": "Ecuaciones de Segundo Grado", "texto": "¿Cuáles son las raíces de x² - 5x + 6 = 0?", "opciones": [{"id": "A", "texto": "x=2, x=3"}, {"id": "B", "texto": "x=1, x=6"}, {"id": "C", "texto": "x=-2, x=-3"}]},
        {"id": 8, "tema": "Desigualdades", "texto": "Resuelve: 3x > 12", "opciones": [{"id": "A", "texto": "x < 4"}, {"id": "B", "texto": "x > 4"}, {"id": "C", "texto": "x > 36"}]},
        {"id": 9, "tema": "Funciones", "texto": "Si f(x) = 2x - 3, ¿cuánto es f(5)?", "opciones": [{"id": "A", "texto": "7"}, {"id": "B", "texto": "13"}, {"id": "C", "texto": "10"}]},
        {"id": 10, "tema": "Exponentes y Radicales", "texto": "Simplifica: (x³)⁴", "opciones": [{"id": "A", "texto": "x⁷"}, {"id": "B", "texto": "x¹²"}, {"id": "C", "texto": "x³⁴"}]},
        {"id": 11, "tema": "Expresiones Racionales", "texto": "Simplifica: (2x) / (4x²)", "opciones": [{"id": "A", "texto": "1 / 2x"}, {"id": "B", "texto": "2 / x"}, {"id": "C", "texto": "x / 2"}]},
        {"id": 12, "tema": "Logaritmos", "texto": "¿Cuál es el valor de log₁₀(100)?", "opciones": [{"id": "A", "texto": "10"}, {"id": "B", "texto": "2"}, {"id": "C", "texto": "1"}]}
    ]
    return render_template("examen.html", preguntas=preguntas_algebra)
# --- Examen: Procesar ---
@usuario_bp.route("/procesar_examen", methods=["POST"])
def procesar_examen():
    u_id = session.get('usuario_id')
    if not u_id: return redirect(url_for('usuario.login'))

    # 1. Definición del Temario con Subtemas
    temario_completo = {
        1: ["Números reales", "Propiedades", "Jerarquía de operaciones"],
        2: ["Variables y constantes", "Traducción de enunciados", "Términos semejantes"],
        3: ["Suma y resta", "Multiplicación", "División de polinomios"],
        4: ["Factor común", "Diferencia de cuadrados", "Trinomios"],
        5: ["Ecuaciones lineales", "Despejes", "Problemas de aplicación"],
        6: ["Método de sustitución", "Método de reducción", "Método gráfico"],
        7: ["Fórmula general", "Factorización de cuadráticas", "Discriminante"],
        8: ["Desigualdades lineales", "Intervalos", "Inecuaciones"],
        9: ["Concepto de función", "Dominio y rango", "Evaluación de funciones"],
        10: ["Leyes de exponentes", "Radicales", "Simplificación"],
        11: ["Fracciones algebraicas", "Simplificación racional", "Operaciones"],
        12: ["Definición de logaritmo", "Propiedades de logaritmos", "Ecuaciones logarítmicas"]
    }

    temas_nombres = [
        "Fundamentos del Álgebra", "Lenguaje Algebraico", "Operaciones con Polinomios",
        "Factorización", "Ecuaciones de Primer Grado", "Sistemas de Ecuaciones",
        "Ecuaciones de Segundo Grado", "Desigualdades", "Funciones",
        "Exponentes y Radicales", "Expresiones Racionales", "Logaritmos"
    ]

    soluciones = {
        "pregunta_1": "B", "pregunta_2": "A", "pregunta_3": "A", "pregunta_4": "B",
        "pregunta_5": "A", "pregunta_6": "B", "pregunta_7": "A", "pregunta_8": "B",
        "pregunta_9": "A", "pregunta_10": "B", "pregunta_11": "A", "pregunta_12": "B"
    }

    aciertos = 0
    total = 12
    from datetime import datetime

    # Guardamos la evaluación general
    evaluacion_diagnostica = Evaluacion(
        id_usuario=u_id, id_tema=0, puntuacion=0, 
        fecha=datetime.now(), tipo_evaluacion='Examen'
    )
    db.session.add(evaluacion_diagnostica)
    db.session.flush()

    # Limpiar progreso previo para generar la nueva ruta limpia
    # Importante: Esto también borrará los subtemas por el ON DELETE CASCADE de la DB
    ProgresoTema.query.filter_by(id_usuario=u_id).delete()

    primer_fallo_encontrado = False

    # Bucle principal de los 12 temas
    for i in range(1, total + 1):
        llave = f"pregunta_{i}"
        resp_usuario = request.form.get(llave)
        es_correcta = (resp_usuario == soluciones[llave])
        
        if es_correcta: aciertos += 1

        # Lógica de estados para la Ruta
        if es_correcta and not primer_fallo_encontrado:
            estado_tema = 'Completado'
        elif not primer_fallo_encontrado:
            estado_tema = 'Disponible'
            primer_fallo_encontrado = True
        else:
            estado_tema = 'Bloqueado'

        # 2. CREAR TEMA PADRE
        nuevo_progreso = ProgresoTema(
            id_usuario=u_id,
            id_tema=i,
            nombre_tema=temas_nombres[i-1],
            estado=estado_tema,
            puntuacion_max=100.00 if estado_tema == 'Completado' else 0.00
        )
        db.session.add(nuevo_progreso)
        db.session.flush() # Genera el ID para conectar los subtemas

        # 3. CREAR SUBTEMAS HIJOS
        subtemas_lista = temario_completo.get(i, ["General"])
        for sub_nombre in subtemas_lista:
            # Si el tema padre está completado, sus hijos también nacen "listos"
            es_completo = True if estado_tema == 'Completado' else False
            
            nuevo_sub = ProgresoSubtema(
                id_progreso_tema=nuevo_progreso.id_progreso,
                nombre_subtema=sub_nombre,
                completado=es_completo,
                fecha_completado=datetime.now() if es_completo else None
            )
            db.session.add(nuevo_sub)

    # Finalizar estadísticas del usuario
    puntaje = round((aciertos / total) * 100, 2)
    evaluacion_diagnostica.puntuacion = puntaje
    
    user = Usuario.query.get(u_id)
    if puntaje >= 85: user.nivel = "Avanzado"
    elif puntaje >= 50: user.nivel = "Intermedio"
    else: user.nivel = "Principiante"

    db.session.commit()
    
    return render_template("resultado_examen.html", puntaje=puntaje, nivel=user.nivel, aciertos=aciertos, total=total)

#--- Ruta --- 
@usuario_bp.route("/ruta")
def ruta():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))
    
    motor = MotorIA()
    progresos_db = ProgresoTema.query.filter_by(id_usuario=u_id).order_by(ProgresoTema.id_tema).all()

    modulos_dinamicos = []
    for p in progresos_db:
        # CALCULAMOS EL PROGRESO REAL:
        # Contamos cuántos subtemas tiene y cuántos están en True
        total_subtemas = len(p.subtemas_progreso)
        completados = len([s for s in p.subtemas_progreso if s.completado])
        
        porcentaje = round((completados / total_subtemas) * 100) if total_subtemas > 0 else 0
        
        # Guardamos el porcentaje en la DB para que persista
        p.puntuacion_max = porcentaje 
        
        modulos_dinamicos.append({
            'id': p.id_tema,
            'nombre': p.nombre_tema,
            'progreso': porcentaje,
            'status': p.estado.lower(),
            'subtemas': [s.nombre_subtema for s in p.subtemas_progreso]
        })

    # Buscamos qué subtema le toca practicar (el primero no completado del tema disponible)
    tema_actual_obj = next((p for p in progresos_db if p.estado == 'Disponible'), None)
    subtema_pendiente = "Inicio"
    
    if tema_actual_obj:
        sub_obj = next((s for s in tema_actual_obj.subtemas_progreso if not s.completado), None)
        if sub_obj:
            subtema_pendiente = sub_obj.nombre_subtema

    db.session.commit() # Guardamos los porcentajes actualizados

    # Obtenemos el usuario para acceder a su nivel
    user = Usuario.query.get(u_id)

    return render_template(
        "ruta.html", 
        ruta={'proximo_reto': tema_actual_obj.nombre_tema if tema_actual_obj else "Fin", 
              'subtema': subtema_pendiente,
              'config_practica': motor.generar_configuracion_ejercicios(user.nivel, "practica") }, 
        modulos=modulos_dinamicos
    )

# --- Práctica ---
@usuario_bp.route("/practica")
def practica():
    u_id = session.get('usuario_id')
    tema_id = request.args.get('tema_id', type=int)
    
    if not u_id or not tema_id:
        return redirect(url_for('usuario.ruta'))

    # Obtenemos datos del usuario y su progreso en la ruta
    user = Usuario.query.get(u_id)
    progreso_t = ProgresoTema.query.filter_by(id_usuario=u_id, id_tema=tema_id).first()
    
    if not progreso_t:
        return redirect(url_for('usuario.ruta'))

    # Identificamos el primer subtema que no esté completado
    subtema_actual = next((s for s in progreso_t.subtemas_progreso if not s.completado), progreso_t.subtemas_progreso[0])

    # Consultamos al Motor IA para la configuración de dificultad
    motor = MotorIA()
    stats = UsuarioService.obtener_estadisticas_globales(u_id)
    accion_ia = motor.decidir_accion(stats['total_ejercicios'], stats['total_aciertos'])
    config = motor.generar_configuracion_ejercicios(user.nivel, accion_ia)

    # Intentamos generar con Gemini (ia_service)
    # Le pasamos el tema y subtema para que sea ultra específico
    ejercicios = ia_service.generar_ejercicios_ia(
        tema=f"{progreso_t.nombre_tema}: {subtema_actual.nombre_subtema}", 
        dificultad=config['dificultad'], 
        cantidad=config['cantidad']
    )

    # Respaldo: Si la IA falla, usamos tu Generador local
    if not ejercicios:
        dificultad_map = {"Principiante": "fácil", "Intermedio": "media", "Avanzado": "difícil"}
        config_local = {
            'cantidad': config['cantidad'], 
            'dificultad': dificultad_map.get(user.nivel, "fácil")
        }
        ejercicios = generador_local.crear_sesion(config_local)

    # Guardamos en sesión el contexto para procesar el guardado al final
    session['practica_contexto'] = {
        'tema_id': tema_id,
        'subtema_id': subtema_actual.id_subtema_prog,
        'cantidad_total': len(ejercicios)
    }

    return render_template("practica.html", 
                           ejercicios=ejercicios, 
                           tema_nombre=progreso_t.nombre_tema,
                           subtema_nombre=subtema_actual.nombre_subtema)
# --- Practica: Procesar (Versión con Analítica para Docente) --- 
@usuario_bp.route("/procesar_practica_json", methods=["POST"])
def procesar_practica_json():
    data = request.get_json(silent=True, force=True)
    u_id = session.get('usuario_id')
    contexto = session.get('practica_contexto') # Contiene tema_id, subtema_id, etc.
    
    print(f"DEBUG: Datos recibidos en JSON: {data}")
    
    if not data:
        return jsonify({"status": "error", "message": "Datos no recibidos correctamente"}), 400
    if not u_id or not contexto:
        return jsonify({"status": "error", "message": "Sesión expirada o sin contexto"}), 400

    # --- 1. DETECCIÓN DE ERRORES CON IA ---
    error_detectado = "Ninguno"
    aciertos = int(data.get('aciertos', 0))
    total = int(data.get('total', 0))

    if aciertos < total:
        try:
            from services.ia_service import AIService
            ai_service = AIService()
            # Le pedimos a la IA que clasifique el error basándose en el tema
            error_detectado = ai_service.analizar_error_pedagogico(
                tema=contexto.get('nombre_tema', 'Matemáticas'), 
                preguntas_fallidas="El alumno falló ejercicios de práctica estándar"
            )
        except Exception as e:
            print(f"⚠️ No se pudo analizar el error con IA: {e}")
            error_detectado = "Indeterminado"

    # --- 2. REGISTRAR EN PROGRESO USUARIO (Con tiempo y error) ---
    try:
        nuevo_progreso = ProgresoUsuario(
            usuario_id=u_id,
            id_tema=contexto['tema_id'],
            ejercicios_realizados=total,
            aciertos=aciertos,
            dificultad_alcanzada="Normal"
        )
        # Campos nuevos para el reporte del profesor
        nuevo_progreso.tiempo_segundos = int(data.get('tiempo', 0))
        nuevo_progreso.tipo_error_comun = error_detectado
        
        db.session.add(nuevo_progreso)
        # Todavía no hacemos commit, esperamos a la lógica de la ruta
    except Exception as e:
        print(f"❌ Error al crear objeto ProgresoUsuario: {e}")

    # --- 3. LÓGICA DE AVANCE EN LA RUTA (BLOSSOM) ---
    if total > 0 and (aciertos / total) >= 0.7:
        sub = ProgresoSubtema.query.get(contexto['subtema_id'])
        if sub and not sub.completado:
            sub.completado = True
            sub.fecha_completado = datetime.now()
            
            tema_padre = sub.tema_padre
            if tema_padre:
                total_subs = len(tema_padre.subtemas_progreso)
                listos = len([s for s in tema_padre.subtemas_progreso if s.completado])
                
                # Actualizar progreso visual (%)
                tema_padre.puntuacion_max = (listos / total_subs) * 100
                
                # Desbloqueo del siguiente tema
                if listos == total_subs:
                    tema_padre.estado = 'Completado'
                    sig = ProgresoTema.query.filter_by(
                        id_usuario=u_id, 
                        id_tema=tema_padre.id_tema + 1
                    ).first()
                    if sig and sig.estado == 'Bloqueado':
                        sig.estado = 'Disponible'
    
    # Guardamos todo (Estadísticas + Avance de Ruta)
    db.session.commit()

    return jsonify({
        "status": "success", 
        "message": "Progreso guardado",
        "error_identificado": error_detectado
    })
# --- Practica: Finalizar ---
@usuario_bp.route("/finalizar_practica", methods=['POST'])
def finalizar_practica():
    data = request.get_json()
    u_id = session.get('usuario_id')
    if not u_id:
        return jsonify({"status": "error", "message": "Usuario no autenticado"}), 401
    
    # El Service se encarga de registrar el progreso y también de manejar la lógica de subida de nivel
    UsuarioService.registrar_progreso(
        u_id=u_id,
        tema=data.get('tema', 'General'),
        total=data.get('total'),
        aciertos=data.get('aciertos'),
        dificultad='Normal'
    )
    
    return jsonify({"status": "success", "message": "Progreso registrado correctamente"})  

# --- Resultados ---
@usuario_bp.route("/resultados")
def resultados():
    # Obtenemos los últimos resultados de la DB
    ultimo_progreso = ProgresoUsuario.query.filter_by(usuario_id=session['usuario_id']).order_by(ProgresoUsuario.fecha.desc()).first()
    
    if not ultimo_progreso:
        return redirect(url_for('usuario.dashboard'))

    motor = MotorIA()
    # La IA analiza el último desempeño
    decision = motor.decidir_accion(ultimo_progreso.ejercicios_realizados, ultimo_progreso.aciertos)
    
    return render_template('resultados.html', 
                           progreso=ultimo_progreso, 
                           decision=decision)

# --- Progreso ---
@usuario_bp.route('/progreso')
def progreso():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))
    
    #Usamos get or_404 para asegurarnos de que el usuario existe antes de mostrar su progreso, si no existe, lanzará un error 404
    user = Usuario.query.get_or_404(u_id)
    
    # Llamamos al servicio para obtener todo el paquete de datos
    datos_reales = UsuarioService.obtener_resumen_progreso(u_id)
    datos_reales['nivel'] = user.nivel
    
    return render_template('progreso.html', stats=datos_reales)

# --- Tutor ---
@usuario_bp.route("/tutor", methods=["GET", "POST"])
def tutor():
    u_id = session.get('usuario_id')
    if not u_id:
        return redirect(url_for('usuario.login'))
    
    if request.method == "POST":
        datos = request.get_json()
        pregunta_usuario = datos.get("mensaje")

        # 1. Guardar lo que escribió Gael
        nuevo_msj = HistorialTutor(usuario_id=u_id, contenido=pregunta_usuario, es_bot=False)
        db.session.add(nuevo_msj)

        try:
            # Llamada a Gemini 2.5 (tu código del test_aq)
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=pregunta_usuario
            )
            respuesta_ia = response.text
            
            # 2. Guardar lo que respondió el Robot
            respuesta_bot = HistorialTutor(usuario_id=u_id, contenido=respuesta_ia, es_bot=True)
            db.session.add(respuesta_bot)
            
            db.session.commit() # Guardamos ambos mensajes en MySQL
            return jsonify({"respuesta": respuesta_ia})
        except Exception as e:
            db.session.rollback()
            return jsonify({"respuesta": f"Error: {str(e)}"}), 500

    # 3. Al cargar (GET), traer el historial ordenado por fecha
    historial = HistorialTutor.query.filter_by(usuario_id=u_id).order_by(HistorialTutor.fecha.asc()).all()
    user = Usuario.query.get(u_id)
    return render_template("tutor.html", historial=historial, user=user)
# --- Tutor: Preguntar ---
@usuario_bp.route("/preguntar_tutor", methods=["POST"])
def preguntar_tutor():
    pregunta = request.form.get("pregunta")
    
    # Simulamos un historial para que veas cómo se ve en el HTML
    historial_simulado = [
        {"rol": "Usuario", "texto": pregunta},
        {"rol": "Tutor IA", "texto": f"Claro, sobre '{pregunta}', mi consejo es que revises las bases de cálculo..."}
    ]
    
    return render_template("tutor.html", historial=historial_simulado)

# --- LOGOUT ---
@usuario_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('usuario.login'))


# --- RUTAS DEL DASHBOARD DOCENTE ---

# --- Dashboard Docente ---
@usuario_bp.route("/dashboard_docente")
def dashboard_docente():
    u_id = session.get('usuario_id')
    rol = session.get('tipo_usuario')
    
    if not u_id or rol.lower() != 'docente':
        return redirect(url_for('usuario.login'))
    
    # 1. Lista de estudiantes
    estudiantes = Usuario.query.filter_by(tipo_usuario='Estudiante').all()

    # 2. Promedio de calificaciones por tema (Para Gráfica de Barras)
    stats_temas = db.session.query(
        ProgresoTema.nombre_tema,
        db.func.avg(ProgresoTema.puntuacion_max).label('promedio')
    ).group_by(ProgresoTema.nombre_tema).all()

    labels_temas = [s.nombre_tema for s in stats_temas]
    valores_temas = [round(float(s.promedio), 2) for s in stats_temas]

    # 3. Detección de Errores Frecuentes (Para Gráfica de Pastel)
    # Contamos cuántas veces aparece cada tipo de error
    conteo_errores = db.session.query(
        ProgresoUsuario.tipo_error_comun,
        db.func.count(ProgresoUsuario.id)
    ).filter(ProgresoUsuario.tipo_error_comun != None)\
     .group_by(ProgresoUsuario.tipo_error_comun).all()

    labels_errores = [e[0] for e in conteo_errores]
    valores_errores = [e[1] for e in conteo_errores]

    return render_template("dashboard_docente.html", 
                           alumnos=estudiantes,
                           labels_temas=labels_temas,
                           valores_temas=valores_temas,
                           labels_errores=labels_errores,
                           valores_errores=valores_errores)

# --- Reportes ---
# --- Reporte Individual del Estudiante (Usa reporte_individual.html)
@usuario_bp.route("/reporte_estudiante/<int:id_estudiante>")
def reporte_estudiante(id_estudiante):
    tipo = session.get('tipo_usuario')
    if not tipo or tipo.lower() != 'docente':
        return redirect(url_for('usuario.login'))

    alumno = Usuario.query.get_or_404(id_estudiante)
    
    # 1. Habilidades (Basado en puntuación_max de progreso_tema)
    progresos = ProgresoTema.query.filter_by(id_usuario=id_estudiante).all()
    habilidades = {
        'dominadas': [p.nombre_tema for p in progresos if p.puntuacion_max >= 85],
        'por_mejorar': [p.nombre_tema for p in progresos if p.puntuacion_max < 65 and p.estado != 'Bloqueado']
    }

    # 2. Tiempo dedicado (Sumatoria de segundos de la tabla progreso_usuario)
    tiempos_query = db.session.query(
        ProgresoTema.nombre_tema,
        db.func.sum(ProgresoUsuario.tiempo_segundos).label('total_segundos')
    ).join(ProgresoUsuario, (ProgresoUsuario.id_tema == ProgresoTema.id_tema) & (ProgresoUsuario.usuario_id == id_estudiante))\
     .group_by(ProgresoTema.nombre_tema).all()

    reporte_tiempo = []
    for t in tiempos_query:
        minutos = round((t.total_segundos or 0) / 60, 1)
        reporte_tiempo.append({'tema': t.nombre_tema, 'minutos': minutos})

    # Renderizamos la plantilla individual específica
    return render_template("reporte_individual.html", 
                           alumno=alumno, 
                           habilidades=habilidades, 
                           tiempos=reporte_tiempo)
    
# --- Reporte Grupal (Usa reportes.html, que muestra la lista de estudiantes y estadísticas globales) ---
@usuario_bp.route("/reporte_grupal")
def reporte_grupal():
    # IMPORTANTE: Aquí calculamos 'stats' para que reportes.html no falle
    alumnos = Usuario.query.filter_by(tipo_usuario='Estudiante').all()
    
    # Análisis de niveles
    expertos = Usuario.query.filter_by(tipo_usuario='Estudiante', nivel='Experto').count()
    principiantes = Usuario.query.filter_by(tipo_usuario='Estudiante', nivel='Principiante').count()
    
    stats_data = {
        'total': len(alumnos),
        'expertos': expertos,
        'principiantes': principiantes,
        'pendientes': len(alumnos) - (expertos + principiantes)
    }
    
    return render_template("reportes.html", alumnos=alumnos, stats=stats_data)