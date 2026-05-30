package com.example.blossom.models;

import com.google.gson.annotations.SerializedName;

public class ProgresoResponse {

    @SerializedName("success")
    private boolean success;

    @SerializedName("mensaje")
    private String mensaje;

    @SerializedName("nivel")
    private String nivel;

    @SerializedName("efectividad")
    private int efectividad;

    // Aquí le decimos a Android: "Cuando veas 'ejercicios_resueltos' en el JSON, mételo en esta variable"
    @SerializedName("ejercicios_resueltos")
    private int ejercicios_resueltos;

    @SerializedName("aciertos_totales")
    private int aciertos_totales;

    // Getters
    public boolean isSuccess() { return success; }
    public String getMensaje() { return mensaje; }
    public String getNivel() { return nivel; }
    public int getEfectividad() { return efectividad; }
    public int getEjerciciosResueltos() { return ejercicios_resueltos; }
    public int getAciertosTotales() { return aciertos_totales; }
}