package com.example.blossom.network;
import com.example.blossom.models.LoginRequest;
import com.example.blossom.models.LoginResponse;
import com.example.blossom.models.PerfilResponse;
import com.example.blossom.models.PerfilUpdateRequest;
import com.example.blossom.models.ProgresoResponse;
import com.example.blossom.models.RegistroRequest;
import com.example.blossom.models.RegistroResponse;
import com.example.blossom.models.DashboardResponse;
import com.example.blossom.models.DashboardRequest;
import com.example.blossom.models.PreguntaResponse;
import com.example.blossom.models.ProcesarExamenRequest;
import com.example.blossom.models.ProcesarExamenResponse;
import com.example.blossom.models.RutaAprendizaje;
import com.example.blossom.models.PracticaResponse;
import com.example.blossom.models.ProcesarPracticaRequest;
import com.example.blossom.models.ResultadoPracticaResponse;
import com.example.blossom.models.TutorRequest;
import com.example.blossom.models.TutorResponse;

import java.util.HashMap;
import retrofit2.Call;
import retrofit2.http.POST;
import retrofit2.http.GET;
import retrofit2.http.Body;
import retrofit2.http.Path;
import retrofit2.http.Query;


public interface ApiService {

    @POST("api/login")
    Call<LoginResponse> iniciarSesion(@Body LoginRequest request);

    @POST("/")
    Call<RegistroResponse> registrarUsuario(@Body RegistroRequest request);

    @POST("api/dashboard")
    Call<DashboardResponse> obtenerDashboard(@Body DashboardRequest request);

    @GET("api/examen")
    Call<PreguntaResponse> obtenerPreguntasExamen();

    @POST("api/procesar_examen")
    Call<ProcesarExamenResponse> procesarExamen(@Body ProcesarExamenRequest request);

    @POST("api/ruta")
    Call<RutaAprendizaje> obtenerRutaAprendizaje(@Body HashMap<String, Object> body);

    @POST("api/practica")
    Call<PracticaResponse> obtenerEjerciciosPractica(@Body HashMap<String, Object> body);

    @POST("/api/procesar_practica")
    Call<ResultadoPracticaResponse> enviarResultadosPractica(@Body com.google.gson.JsonObject body);

    @GET("/api/usuario/progreso/{usuario_id}")
    Call<ProgresoResponse> obtenerProgresoUsuario(@Path("usuario_id") int usuarioId);

    @POST("api/tutor")
    Call<TutorResponse> enviarMensajeTutor(@Body TutorRequest request);

    @POST("api/perfil")
    Call<PerfilResponse> obtenerPerfil(@Body int usuarioId);

    @POST("api/actualizar_perfil")
    Call<Void> actualizarPerfil(@Body PerfilUpdateRequest request);

}