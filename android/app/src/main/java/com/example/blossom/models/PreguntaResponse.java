package com.example.blossom.models;
import java.util.List;

public class PreguntaResponse {
    private boolean success;
    private List<Pregunta> preguntas;

    public boolean isSuccess() { return success; }
    public List<Pregunta> getPreguntas() { return preguntas; }

    public static class Pregunta {
        private int id;
        private String tema;
        private String texto;
        private List<String> opciones;

        public int getId() { return id; }
        public String getTema() { return tema; }
        public String getTexto() { return texto; }
        public List<String> getOpciones() { return opciones; }
    }
}