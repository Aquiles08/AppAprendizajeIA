package com.example.blossom.models;
import java.util.List;

public class RutaResponse {
    public RutaInfo ruta;
    public List<Modulo> modulos;

    public static class RutaInfo {
        public String proximo_reto;
        public String subtema;
        // Agrega configuración de práctica si la necesitas
    }

    public static class Modulo {
        public int id;
        public String nombre;
        public int progreso; // 0, 33, 66, 100
        public String status; // "completado", "disponible", "bloqueado"
        public List<String> subtemas;
    }
}