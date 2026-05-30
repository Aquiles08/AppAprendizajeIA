package com.example.blossom.activities;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.blossom.R;
import com.example.blossom.adapters.ResultadoAdapter;
import com.example.blossom.models.ResultadoPracticaResponse.DetalleReporte;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import java.lang.reflect.Type;
import java.util.List;

public class ResultadoActivity extends AppCompatActivity {

    private TextView tvTituloResumen, tvDecisionIa, tvDiagnosticoIa;
    private RecyclerView rvDetalles;
    private Button btnVolverInicio;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_resultado);

        // 1. Inicializar Vistas
        tvTituloResumen = findViewById(R.id.tvTituloResumen);
        tvDecisionIa = findViewById(R.id.tvDecisionIa);
        tvDiagnosticoIa = findViewById(R.id.tvDiagnosticoIa);
        rvDetalles = findViewById(R.id.rvDetallesResultado);
        btnVolverInicio = findViewById(R.id.btnVolverInicio);

        rvDetalles.setLayoutManager(new LinearLayoutManager(this));

        // 2. Recuperar Datos del Intent
        String scoreTexto = getIntent().getStringExtra("score_texto"); // Ejemplo: "0/10"
        String decisionIa = getIntent().getStringExtra("decision_ia");   // Ejemplo: "¡Falta práctica!"
        String errorIa = getIntent().getStringExtra("error_ia");         // Ejemplo: "Un poco más..."
        String detallesJson = getIntent().getStringExtra("detalles_json");

        // 3. Inyectar Textos en la UI
        if (scoreTexto != null) {
            tvTituloResumen.setText("Resumen de tu practica " + scoreTexto);
        }
        if (decisionIa != null && !decisionIa.trim().isEmpty()) {
            tvDecisionIa.setText(decisionIa);
        }
        if (errorIa != null && !errorIa.trim().isEmpty()) {
            tvDiagnosticoIa.setText(errorIa);
        }

        // 4. Reconstruir la lista de detalles y enlazar el adaptador
        if (detallesJson != null) {
            Gson gson = new Gson();
            Type listType = new TypeToken<List<DetalleReporte>>(){}.getType();
            List<DetalleReporte> listaDetalles = gson.fromJson(detallesJson, listType);

            ResultadoAdapter adapter = new ResultadoAdapter(listaDetalles);
            rvDetalles.setAdapter(adapter);
        }

        // 5. Botón de retorno al flujo principal de Blossom
        btnVolverInicio.setOnClickListener(v -> {
            // Cerramos esta pantalla para regresar al menú principal
            finish();
        });
    }
}