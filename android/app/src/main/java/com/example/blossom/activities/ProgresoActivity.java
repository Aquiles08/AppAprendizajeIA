package com.example.blossom.activities;

import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.blossom.R;
import com.example.blossom.models.ProgresoResponse;
import com.example.blossom.network.RetrofitClient;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ProgresoActivity extends AppCompatActivity {

    private TextView tvNivel, tvEfectividad, tvEjerciciosResueltos, tvAciertosTotales;
    private Button btnVolver;
    private int usuarioId = 1; // Sustituye por tu SharedPreferences u origen real del ID

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_progreso);

        // Inicializar Vistas
        tvNivel = findViewById(R.id.tvNivel);
        tvEfectividad = findViewById(R.id.tvEfectividad);
        tvEjerciciosResueltos = findViewById(R.id.tvEjerciciosResueltos);
        tvAciertosTotales = findViewById(R.id.tvAciertosTotales);
        btnVolver = findViewById(R.id.btnVolverInicio);

        btnVolver.setOnClickListener(v -> finish());

        usuarioId = getIntent().getIntExtra("usuario_id", -1);

        // Si por alguna razón no llega el ID, puedes manejarlo aquí:
        if (usuarioId == -1) {
            Toast.makeText(this, "Error: No se recibió el ID de usuario", Toast.LENGTH_SHORT).show();
            finish(); // Cierra la pantalla si no tiene ID
            return;
        }

        // Cargar datos desde la API de Flask
        cargarProgresoDesdeServidor();
    }

    private void cargarProgresoDesdeServidor() {
        RetrofitClient.getApiService().obtenerProgresoUsuario(usuarioId).enqueue(new Callback<ProgresoResponse>() {
            @Override
            public void onResponse(Call<ProgresoResponse> call, Response<ProgresoResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    ProgresoResponse prog = response.body();

                    // --- DEBUG: ESTO NOS DIRÁ LA VERDAD EN EL LOGCAT ---
                    android.util.Log.d("DEBUG_DATOS", "Nivel: " + prog.getNivel());
                    android.util.Log.d("DEBUG_DATOS", "Ejercicios (int): " + prog.getEjerciciosResueltos());

                    if (prog.isSuccess()) {
                        // Actualizamos con toString() para asegurar que no haya error de tipo
                        tvNivel.setText(prog.getNivel() != null ? prog.getNivel() : "N/A");
                        tvEfectividad.setText(String.valueOf(prog.getEfectividad()) + "%");

                        // Asignamos directamente la conversión a String
                        String ejercStr = String.valueOf(prog.getEjerciciosResueltos());
                        String aciertosStr = String.valueOf(prog.getAciertosTotales());

                        tvEjerciciosResueltos.setText(ejercStr);
                        tvAciertosTotales.setText(aciertosStr);
                    } else {
                        Toast.makeText(ProgresoActivity.this, "Error: " + prog.getMensaje(), Toast.LENGTH_SHORT).show();
                    }
                } else {
                    Toast.makeText(ProgresoActivity.this, "Respuesta vacía o error HTTP", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<ProgresoResponse> call, Throwable t) {
                Toast.makeText(ProgresoActivity.this, "Falla: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}