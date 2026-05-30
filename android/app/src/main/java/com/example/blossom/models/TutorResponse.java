package com.example.blossom.models;
import com.google.gson.annotations.SerializedName;

public class TutorResponse {
    @SerializedName("success")
    private boolean success;

    @SerializedName("respuesta")
    private String respuesta;

    public String getRespuesta() { return respuesta; }
    public boolean isSuccess() { return success; }
}