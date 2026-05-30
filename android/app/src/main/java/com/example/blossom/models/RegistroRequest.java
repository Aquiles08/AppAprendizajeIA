package com.example.blossom.models;

public class RegistroRequest {
    private String nombre;
    private String correo;
    private String contrasena;
    private String rol;

    public RegistroRequest(String nombre, String correo, String contrasena, String rol) {
        this.nombre = nombre;
        this.correo = correo;
        this.contrasena = contrasena;
        this.rol = rol;
    }
}