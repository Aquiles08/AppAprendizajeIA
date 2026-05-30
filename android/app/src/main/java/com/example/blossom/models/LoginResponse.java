package com.example.blossom.models;

public class LoginResponse {
    private boolean success;
    private String mensaje;
    private int usuario_id;
    private String nombre;

    public boolean isSuccess() { return success; }
    public String getMensaje() { return mensaje; }
    public int getUsuarioId() { return usuario_id; }
    public String getNombre() { return nombre; }
}