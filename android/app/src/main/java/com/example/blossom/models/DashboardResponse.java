package com.example.blossom.models;

import java.util.List;

public class DashboardResponse {
    private boolean success;
    private String nombre;
    private String tipo_usuario;
    private int total_ejercicios;
    private int total_aciertos;
    private List<Object> historial; // Cambia Object por tu modelo de historial si es necesario

    // Getters
    public boolean isSuccess() { return success; }
    public String getNombre() { return nombre; }
    public String getTipoUsuario() { return tipo_usuario; }
    public int getTotalEjercicios() { return total_ejercicios; }
    public int getTotalAciertos() { return total_aciertos; }
    public List<Object> getHistorial() { return historial; }
}
