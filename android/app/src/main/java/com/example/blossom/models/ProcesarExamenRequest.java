package com.example.blossom.models;
import java.util.Map;

public class ProcesarExamenRequest {
    private int usuario_id;
    private Map<String, String> respuestas; // Guarda {"1":"B", "2":"A", ...}

    public ProcesarExamenRequest(int usuario_id, Map<String, String> respuestas) {
        this.usuario_id = usuario_id;
        this.respuestas = respuestas;
    }
}