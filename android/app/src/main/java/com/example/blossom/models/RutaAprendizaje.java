package com.example.blossom.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class RutaAprendizaje {
    @SerializedName("success")
    public boolean success;

    @SerializedName("ruta")
    public RutaInfo ruta;

    @SerializedName("modulos")
    public List<Modulo> modulos;

    public static class RutaInfo {
        @SerializedName("reto")
        public String reto;

        @SerializedName("subtema")
        public String subtema;
    }

    public static class Modulo {
        @SerializedName("id")
        public int id;

        @SerializedName("nombre")
        public String nombre;

        @SerializedName("progreso")
        public int progreso;

        @SerializedName("status")
        public String status;

        @SerializedName("subtemas")
        public List<String> subtemas;
    }
}