package com.example.blossom.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class PracticaResponse {
    private boolean success;
    private String mensaje;

    @SerializedName("tema_id")
    private int tema_id;

    @SerializedName("subtema_id")
    private int subtema_id;

    @SerializedName("tema_nombre")
    private String tema_nombre;

    @SerializedName("subtema_nombre")
    private String subtema_nombre;

    @SerializedName("ejercicios")
    private List<Ejercicio> ejercicios;

    // Getters y Setters limpios
    public boolean isSuccess() { return success; }
    public String getMensaje() { return mensaje; }
    public int getTemaId() { return tema_id; }
    public int getSubtemaId() { return subtema_id; }
    public String getTemaNombre() { return tema_nombre; }
    public String getSubtemaNombre() { return subtema_nombre; } // Tu método original corregido
    public List<Ejercicio> getEjercicios() { return ejercicios; }

    // Clase interna para mapear cada ejercicio/pregunta individual
    // Clase interna para mapear cada ejercicio/pregunta individual
    // Clase interna para mapear cada ejercicio/pregunta individual
    public static class Ejercicio {
        @SerializedName("id")
        private int id;

        @SerializedName("pregunta")
        private String pregunta;

        @SerializedName("respuesta_correcta")
        private String respuestaCorrecta; // Usamos camelCase estándar en Java

        @SerializedName("explicacion")
        private String explicacion;

        public int getId() { return id; }
        public String getPregunta() { return pregunta; }

        // Mantenemos el nombre exacto de este método para que NO rompa tu EjercicioAdapter.java
        public String getRespuestaCorrecta() {
            return respuestaCorrecta != null ? respuestaCorrecta : "";
        }

        public String getExplicacion() { return explicacion; }
    }
}