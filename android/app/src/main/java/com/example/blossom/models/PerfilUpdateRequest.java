package com.example.blossom.models;

public class PerfilUpdateRequest {
    public int usuario_id;
    public String tutor_mode;
    public String enfoque_temas;

    public PerfilUpdateRequest(int id, String modo, String temas) {
        this.usuario_id = id;
        this.tutor_mode = modo;
        this.enfoque_temas = temas;
    }
}