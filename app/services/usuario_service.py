from config.database import db
from app.models.progresoUsuario import ProgresoUsuario
from app.models.usuario import Usuario

class UsuarioService:
    @staticmethod
    def obtener_estadisticas_globales(u_id):
        """Calcula el total de ejercicios y aciertos de un usuario"""
        stats = db.session.query(
            db.func.sum(ProgresoUsuario.ejercicios_realizados),
            db.func.sum(ProgresoUsuario.aciertos)
        ).filter(ProgresoUsuario.usuario_id == u_id).first()
        
        return {
            'total_ejercicios': stats[0] if stats[0] else 0,
            'total_aciertos': stats[1] if stats[1] else 0
        }

    @staticmethod
    def registrar_progreso(u_id, tema, total, aciertos, dificultad):
    # --- LA PARTE FORMAL ---
    # Como tu DB espera un INT en id_tema, mapeamos el nombre al ID.
    # Si después tienes una tabla 'temas', aquí harías un: Tema.query.filter_by(nombre=tema).first()
    
        mapa_temas = {
            "Ecuaciones de Primer Grado": 1,
            "Sistemas de Ecuaciones": 2,
            "Operaciones Básicas": 3
        }
    
    # Obtenemos el ID, si no existe el tema en el mapa, le ponemos 1 por defecto
        tema_id_final = mapa_temas.get(tema, 1)

    # 1. Guardar el progreso usando id_tema
        nuevo_progreso = ProgresoUsuario(
            usuario_id=u_id,
            id_tema=tema_id_final,
            ejercicios_realizados=total,
            aciertos=aciertos,
            dificultad_alcanzada=dificultad
        )
        db.session.add(nuevo_progreso)
    
    # 2. Lógica de Subida de Nivel (Se mantiene igual)
        if total > 0 and aciertos == total:
            usuario = Usuario.query.get(u_id)
            niveles = ["Sin realizar examen", "Principiante", "Intermedio", "Avanzado", "Experto"]
        
            if usuario and usuario.nivel in niveles:
                indice_actual = niveles.index(usuario.nivel)
                if indice_actual < len(niveles) - 1:
                    usuario.nivel = niveles[indice_actual + 1]
                    print(f"¡Usuario {u_id} subió a {usuario.nivel}!")

        db.session.commit()
        return nuevo_progreso
    
    @staticmethod
    def obtener_resumen_progreso(u_id):
        # 1. Totales (Lo que ya teníamos)
        stats = db.session.query(
            db.func.sum(ProgresoUsuario.ejercicios_realizados),
            db.func.sum(ProgresoUsuario.aciertos)
        ).filter(ProgresoUsuario.usuario_id == u_id).first()
        
        # 2. Historial reciente (Para ver los últimos logros)
        historial = ProgresoUsuario.query.filter_by(usuario_id=u_id)\
                    .order_by(ProgresoUsuario.fecha.desc()).limit(5).all()

        return {
            'total_ejercicios': stats[0] if stats[0] else 0,
            'total_aciertos': stats[1] if stats[1] else 0,
            'historial': historial
        }