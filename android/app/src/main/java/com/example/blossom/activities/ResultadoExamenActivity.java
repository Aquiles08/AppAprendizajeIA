package com.example.blossom.activities;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.blossom.MainActivity;
import com.example.blossom.R;
import com.example.blossom.models.ProcesarExamenRequest;
import com.example.blossom.models.ProcesarExamenResponse;
import com.example.blossom.network.ApiService;
import com.example.blossom.network.RetrofitClient;
import java.util.HashMap;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ResultadoExamenActivity extends AppCompatActivity {

    private TextView tvPuntajePorcentaje, tvResumenPreguntas, tvNivelAsignado;
    private Button btnRegresarInicio, btnIrRuta;
    private int usuarioId;
    private HashMap<String, String> respuestasExamen;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_resultado_examen);

        // Vincular componentes del XML
        tvPuntajePorcentaje = findViewById(R.id.tvPuntajePorcentaje);
        tvResumenPreguntas = findViewById(R.id.tvResumenPreguntas);
        tvNivelAsignado = findViewById(R.id.tvNivelAsignado);
        btnRegresarInicio = findViewById(R.id.btnRegresarInicio);
        btnIrRuta = findViewById(R.id.btnIrRuta);

        // Recuperar parámetros de navegación
        usuarioId = getIntent().getIntExtra("usuario_id", -1);
        respuestasExamen = (HashMap<String, String>) getIntent().getSerializableExtra("respuestas_examen");

        if (usuarioId == -1 || respuestasExamen == null) {
            Toast.makeText(this, "Error de datos al procesar resultados", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        // Mandar respuestas al servidor
        enviarResultadosAlServidor();

        // Configurar botones de redirección
        btnRegresarInicio.setOnClickListener(v -> {
            Intent intent = new Intent(ResultadoExamenActivity.this, MainActivity.class);
            intent.putExtra("usuario_id", usuarioId);
            startActivity(intent);
            finish();
        });

        btnIrRuta.setOnClickListener(v -> {
            Toast.makeText(ResultadoExamenActivity.this, "Navegando a Ruta de Aprendizaje...", Toast.LENGTH_SHORT).show();
            // Próximamente: Redirigir directamente a RutasAprendizajeActivity
        });
    }

    private void enviarResultadosAlServidor() {
        ApiService apiService = RetrofitClient.getApiService();
        ProcesarExamenRequest request = new ProcesarExamenRequest(usuarioId, respuestasExamen);

        apiService.procesarExamen(request).enqueue(new Callback<ProcesarExamenResponse>() {
            @Override
            public void onResponse(Call<ProcesarExamenResponse> call, Response<ProcesarExamenResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    ProcesarExamenResponse res = response.body();
                    if (res.isSuccess()) {
                        // Pintamos dinámicamente los valores reales que regresó Flask
                        tvPuntajePorcentaje.setText(String.format("%.2f%%", res.getPuntaje()));
                        tvResumenPreguntas.setText("Has acertado " + res.getAciertos() + " de " + res.getTotal() + " preguntas.");
                        tvNivelAsignado.setText(res.getNivel().toUpperCase());
                    } else {
                        Toast.makeText(ResultadoExamenActivity.this, "Error: " + res.getMensaje(), Toast.LENGTH_SHORT).show();
                    }
                } else {
                    Toast.makeText(ResultadoExamenActivity.this, "Error en procesamiento", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<ProcesarExamenResponse> call, Throwable t) {
                Toast.makeText(ResultadoExamenActivity.this, "Fallo de comunicación con la base de datos", Toast.LENGTH_SHORT).show();
            }
        });
    }
}