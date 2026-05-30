package com.example.blossom.models;

public class ProcesarExamenResponse {
    private boolean success;
    private double puntaje;
    private String nivel;
    private int aciertos;
    private int total;
    private String mensaje;

    public boolean isSuccess() { return success; }
    public double getPuntaje() { return puntaje; }
    public String getNivel() { return nivel; }
    public int getAciertos() { return aciertos; }
    public int getTotal() { return total; }
    public String getMensaje() { return mensaje; }
}