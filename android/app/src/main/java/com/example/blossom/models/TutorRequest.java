package com.example.blossom.models;
import com.google.gson.annotations.SerializedName;

public class TutorRequest {
    @SerializedName("pregunta")
    private String pregunta;

    @SerializedName("modo")
    private String modo;

    public TutorRequest(String pregunta, String modo) {
        this.pregunta = pregunta;
        this.modo = modo;
    }
}