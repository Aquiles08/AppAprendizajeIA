package com.example.blossom.activities;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.blossom.R;
import com.example.blossom.adapters.EjercicioAdapter;
import com.example.blossom.models.PracticaResponse;
import com.example.blossom.models.ProcesarPracticaRequest;
import com.example.blossom.models.ResultadoPracticaResponse;
import com.example.blossom.network.RetrofitClient;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import java.util.HashMap;
import java.util.List;

public class PracticaActivity extends AppCompatActivity {
    private static final String TAG = "DEBUG_BLOSSOM";

    private TextView tvSubtituloTema;
    private RecyclerView rvEjercicios;
    private Button btnEnviarRespuestas;

    private EjercicioAdapter adapter;
    private int usuarioId;
    private int temaId;
    private int subtemaId; // Se llena dinámicamente con la respuesta de Flask
    private String nombreTema;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_practica);

        // 1. Vincular componentes del XML
        tvSubtituloTema = findViewById(R.id.tvSubtituloTema);
        rvEjercicios = findViewById(R.id.rvEjercicios);
        btnEnviarRespuestas = findViewById(R.id.btnEnviarRespuestas);

        rvEjercicios.setLayoutManager(new LinearLayoutManager(this));

        // 2. Recuperar IDs dinámicos enviados desde la pantalla anterior
        usuarioId = getIntent().getIntExtra("usuario_id", -1);
        temaId = getIntent().getIntExtra("tema_id", -1);

        if (usuarioId == -1 || temaId == -1) {
            Toast.makeText(this, "Error al cargar la sesión de práctica", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        // 3. Cargar las preguntas desde Flask
        cargarEjerciciosServidor();

        // 4. Configurar el botón gigante de Enviar respuestas
        btnEnviarRespuestas.setOnClickListener(v -> enviarResultadosAlServidor());
    }

    private void cargarEjerciciosServidor() {
        HashMap<String, Object> body = new HashMap<>();
        body.put("usuario_id", usuarioId);
        body.put("tema_id", temaId);

        RetrofitClient.getApiService().obtenerEjerciciosPractica(body).enqueue(new retrofit2.Callback<PracticaResponse>() {
            @Override
            public void onResponse(retrofit2.Call<PracticaResponse> call, retrofit2.Response<PracticaResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    PracticaResponse data = response.body();

                    if (data.isSuccess()) {
                        // Guardamos los datos de control del backend
                        subtemaId = data.getSubtemaId();
                        nombreTema = data.getTemaNombre();

                        // Modificamos el encabezado igual que en la web
                        if (data.getTemaNombre() != null && data.getSubtemaNombre() != null) {
                            tvSubtituloTema.setText(data.getTemaNombre() + " ➔ " + data.getSubtemaNombre());
                        } else {
                            tvSubtituloTema.setText("Práctica del Módulo");
                        }

                        // Enlazamos las preguntas generadas al RecyclerView de forma segura
                        if (data.getEjercicios() != null && !data.getEjercicios().isEmpty()) {
                            adapter = new EjercicioAdapter(data.getEjercicios());
                            rvEjercicios.setAdapter(adapter);
                            Log.d(TAG, "Ejercicios cargados con éxito para subtema_id: " + subtemaId);
                        } else {
                            Log.w(TAG, "La lista de ejercicios llegó vacía o nula");
                            Toast.makeText(PracticaActivity.this, "La IA no generó preguntas. Intenta de nuevo.", Toast.LENGTH_LONG).show();
                        }

                    } else {
                        Toast.makeText(PracticaActivity.this, "Error: " + data.getMensaje(), Toast.LENGTH_LONG).show();
                    }
                } else {
                    Toast.makeText(PracticaActivity.this, "Error de respuesta del servidor: " + response.code(), Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(retrofit2.Call<PracticaResponse> call, Throwable t) {
                Log.e(TAG, "Error crítico de serialización o red en la práctica", t);
                Toast.makeText(PracticaActivity.this, "Falla de parseo/red: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private void enviarResultadosAlServidor() {
        if (adapter == null) return;

        btnEnviarRespuestas.setEnabled(false);
        btnEnviarRespuestas.setText("PROCESANDO CON IA...");

        // 1. Obtenemos la lista original limpia que guardó el adapter al inicio
        List<PracticaResponse.Ejercicio> listaEjercicios = adapter.getListaEjercicios();
        if (listaEjercicios == null || listaEjercicios.isEmpty()) {
            btnEnviarRespuestas.setEnabled(true);
            btnEnviarRespuestas.setText("ENVIAR RESPUESTAS");
            return;
        }

        int totalPreguntas = listaEjercicios.size();
        int aciertosCalculados = 0;
        JsonArray detallesArray = new JsonArray();

        // 2. Construimos manualmente el Array de detalles cruzando la persistencia
        for (int i = 0; i < totalPreguntas; i++) {
            PracticaResponse.Ejercicio ej = listaEjercicios.get(i);

            // Jalamos lo que escribió el chavo usando el método de memoria del adapter
            String respuestaUsuario = adapter.getRespuestaEnPosicion(i).trim();
            String respuestaCorrecta = ej.getRespuestaCorrecta() != null ? ej.getRespuestaCorrecta().trim() : "";
            String explicacionTxt = ej.getExplicacion() != null ? ej.getExplicacion().trim() : "Sin explicación";

            JsonObject detalleObj = new JsonObject();
            detalleObj.addProperty("pregunta", ej.getPregunta());
            detalleObj.addProperty("tu_respuesta", respuestaUsuario.isEmpty() ? "Sin respuesta" : respuestaUsuario);
            detalleObj.addProperty("correcta", respuestaCorrecta);
            detalleObj.addProperty("explicacion", explicacionTxt);

            // Limpieza matemática estándar para calcular el puntaje real aquí mismo
            String cleanUser = respuestaUsuario.replaceAll("\\s+", "").toLowerCase();
            String cleanCorrect = respuestaCorrecta.replaceAll("\\s+", "").toLowerCase();

            if (!cleanUser.isEmpty() && cleanUser.equals(cleanCorrect)) {
                aciertosCalculados++;
            }

            detallesArray.add(detalleObj);
        }

        // 3. Empaquetamos el Payload completo exacto que espera tu Flask
        JsonObject requestPayload = new JsonObject();
        requestPayload.addProperty("usuario_id", usuarioId);
        requestPayload.addProperty("tema_id", temaId);
        requestPayload.addProperty("subtema_id", subtemaId);
        requestPayload.addProperty("tema_nombre", nombreTema);
        requestPayload.addProperty("aciertos", aciertosCalculados);
        requestPayload.addProperty("total", totalPreguntas);
        requestPayload.add("detalles", detallesArray);

        // 🔥 IMPRIMIR LOG EN CONSOLA PARA VERIFICAR ANTES DE MANDAR
        Log.d("DEBUG_BLOSSOM_JSON", "MANDANDO PAYLOAD: " + new Gson().toJson(requestPayload));

        final int aciertosFinales = aciertosCalculados;

        // 4. Petición directa mandando el JsonObject empaquetado
        RetrofitClient.getApiService().enviarResultadosPractica(requestPayload).enqueue(new retrofit2.Callback<ResultadoPracticaResponse>() {
            @Override
            public void onResponse(retrofit2.Call<ResultadoPracticaResponse> call, retrofit2.Response<ResultadoPracticaResponse> response) {
                btnEnviarRespuestas.setEnabled(true);
                btnEnviarRespuestas.setText("ENVIAR RESPUESTAS");

                if (response.isSuccessful() && response.body() != null) {
                    ResultadoPracticaResponse res = response.body();

                    if (res.isSuccess()) {
                        Log.d(TAG, "Acción del Motor IA: " + res.getDecisionIa());
                        Log.d(TAG, "Diagnóstico pedagógico: " + res.getErrorIdentificado());

                        Intent intent = new Intent(PracticaActivity.this, ResultadoActivity.class);
                        intent.putExtra("score_texto", aciertosFinales + "/" + totalPreguntas);
                        intent.putExtra("decision_ia", res.getDecisionIa());
                        intent.putExtra("error_ia", res.getErrorIdentificado());

                        // Pasamos los detalles procesados que devolvió Flask a la pantalla final
                        String detallesJson = new Gson().toJson(res.getDetalles());
                        intent.putExtra("detalles_json", detallesJson);

                        startActivity(intent);
                        finish();
                    } else {
                        Toast.makeText(PracticaActivity.this, "Error al guardar: " + res.getMensaje(), Toast.LENGTH_LONG).show();
                    }
                } else {
                    Toast.makeText(PracticaActivity.this, "Error al procesar con el servidor", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(retrofit2.Call<ResultadoPracticaResponse> call, Throwable t) {
                btnEnviarRespuestas.setEnabled(true);
                btnEnviarRespuestas.setText("ENVIAR RESPUESTAS");
                Log.e(TAG, "Error de red crítico", t);
                Toast.makeText(PracticaActivity.this, "Falla de red crítica al enviar", Toast.LENGTH_SHORT).show();
            }
        });
    }
}