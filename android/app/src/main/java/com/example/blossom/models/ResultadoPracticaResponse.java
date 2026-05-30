package com.example.blossom.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class ResultadoPracticaResponse {
    private boolean success;
    private String mensaje;

    @SerializedName("decision_ia")
    private String decisionIa;

    @SerializedName("error_identificado")
    private String errorIdentificado;

    // Recibimos el desglose de lo que el backend guardó
    @SerializedName("detalles")
    private List<DetalleReporte> detalles;

    public boolean isSuccess() { return success; }
    public String getMensaje() { return mensaje; }
    public String getDecisionIa() { return decisionIa; }
    public String getErrorIdentificado() { return errorIdentificado; }
    public List<DetalleReporte> getDetalles() { return detalles; }

    public static class DetalleReporte {
        private String pregunta;
        @SerializedName("respuesta_usuario")
        private String respuestaUsuario;
        @SerializedName("respuesta_correcta")
        private String respuestaCorrecta;
        private String explicacion;
        private boolean correcta;

        public String getPregunta() { return pregunta; }
        public String getRespuestaUsuario() { return respuestaUsuario; }
        public String getRespuestaCorrecta() { return respuestaCorrecta; }
        public String getExplicacion() { return explicacion; }
        public boolean isCorrecta() { return correcta; }
    }
}