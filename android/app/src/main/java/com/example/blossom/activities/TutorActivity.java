package com.example.blossom.activities;

import android.os.Bundle;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import com.example.blossom.R;
import com.example.blossom.models.*;
import com.example.blossom.network.RetrofitClient;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class TutorActivity extends AppCompatActivity {

    private EditText etMensaje;
    private Button btnEnviar;
    private TextView tvChatHistorial;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tutor);

        etMensaje = findViewById(R.id.etMensaje);
        btnEnviar = findViewById(R.id.btnEnviar);
        tvChatHistorial = findViewById(R.id.tvChatHistorial);

        btnEnviar.setOnClickListener(v -> enviarPregunta());
    }

    private void enviarPregunta() {
        String pregunta = etMensaje.getText().toString();
        if (pregunta.isEmpty()) return;

        // Añadir tu pregunta a la pantalla
        tvChatHistorial.append("\n\nTú: " + pregunta);
        etMensaje.setText("");

        // Llamar a la API
        TutorRequest request = new TutorRequest(pregunta, "paciente");

        RetrofitClient.getApiService().enviarMensajeTutor(request).enqueue(new Callback<TutorResponse>() {
            @Override
            public void onResponse(Call<TutorResponse> call, Response<TutorResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    tvChatHistorial.append("\n\nTutor: " + response.body().getRespuesta());
                } else {
                    tvChatHistorial.append("\n\nError: No pude obtener respuesta.");
                }
            }
            @Override
            public void onFailure(Call<TutorResponse> call, Throwable t) {
                tvChatHistorial.append("\n\nFallo de conexión.");
            }
        });
    }
}