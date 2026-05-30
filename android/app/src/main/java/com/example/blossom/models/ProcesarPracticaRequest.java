package com.example.blossom.models;

import java.util.List;

public class ProcesarPracticaRequest {
    private int usuario_id;
    private int tema_id;
    private int subtema_id;
    private String tema_nombre;
    private int aciertos;
    private int total;
    private List<DetalleIntento> detalles;

    // Constructor completo para armarlo fácil en la Activity
    public ProcesarPracticaRequest(int usuario_id, int tema_id, int subtema_id, String tema_nombre, int aciertos, int total, List<DetalleIntento> detalles) {
        this.usuario_id = usuario_id;
        this.tema_id = tema_id;
        this.subtema_id = subtema_id;
        this.tema_nombre = tema_nombre;
        this.aciertos = aciertos;
        this.total = total;
        this.detalles = detalles;
    }

    // Clase interna para estructurar el reporte pedagógico de cada fallo
    public static class DetalleIntento {
        private String pregunta;
        private String tu_respuesta;
        private String correcta;
        private String explicacion;
        private boolean es_correcta;

        // 🔥 Constructor actualizado con los 5 parámetros idénticos a la web
        public DetalleIntento(String pregunta, String tu_respuesta, String correcta, String explicacion, boolean es_correcta) {
            this.pregunta = pregunta;
            this.tu_respuesta = tu_respuesta;
            this.correcta = correcta;
            this.explicacion = explicacion;
            this.es_correcta = es_correcta;
        }

        // Getters y Setters (Por si Gson o Retrofit los necesitan al serializar)
        public String getPregunta() { return pregunta; }
        public String getTuRespuesta() { return tu_respuesta; }
        public String getCorrecta() { return correcta; }
        public String getExplicacion() { return explicacion; }
        public boolean isEsCorrecta() { return es_correcta; }
    }
}