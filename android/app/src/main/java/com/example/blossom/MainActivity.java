package com.example.blossom;

import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;

import com.example.blossom.activities.RutaActivity;
import com.example.blossom.models.DashboardRequest;
import com.example.blossom.models.DashboardResponse;
import com.example.blossom.activities.ExamenActivity;
import com.example.blossom.network.ApiService;
import com.example.blossom.network.RetrofitClient; // Tu cliente real
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {

    private TextView tvBienvenida, tvNivel;
    private CardView btnExamen, btnRutas, btnPractica, btnProgreso, btnTutor, btnPerfil;
    private int usuarioId;

    @Override
    protected void onCreate(Bundle savedInstanceState) { // Corregido el onCreate
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 1. Inicializar vistas de tu XML
        tvBienvenida = findViewById(R.id.tvBienvenida);
        tvNivel = findViewById(R.id.tvNivel);

        btnExamen = findViewById(R.id.btnExamen);
        btnRutas = findViewById(R.id.btnRutas);
        btnPractica = findViewById(R.id.btnPractica);
        btnProgreso = findViewById(R.id.btnProgresoDetalle);
        btnTutor = findViewById(R.id.btnTutor);
        btnPerfil = findViewById(R.id.btnPerfil);

        // 2. Recuperar el ID del usuario enviado desde tu LoginActivity
        usuarioId = getIntent().getIntExtra("usuario_id", -1);

        if (usuarioId == -1) {
            Toast.makeText(this, "Error de sesión", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        // 3. Cargar los datos del servidor de Flask
        cargarDatosDashboard();

        // 4. Configurar eventos de los botones
        configurarMenu();
    }

    private void cargarDatosDashboard() {
        // Usamos tu forma nativa de llamar a Retrofit
        ApiService apiService = RetrofitClient.getApiService();
        DashboardRequest request = new DashboardRequest(usuarioId);

        apiService.obtenerDashboard(request).enqueue(new Callback<DashboardResponse>() {
            @Override
            public void onResponse(Call<DashboardResponse> call, Response<DashboardResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    DashboardResponse res = response.body();
                    if (res.isSuccess()) {
                        // Cambiamos el texto dinámicamente con la data de la DB
                        tvBienvenida.setText("Bienvenido, ¡" + res.getNombre() + "!!");
                        tvNivel.setText(res.getTipoUsuario());
                    } else {
                        Toast.makeText(MainActivity.this, "Error al procesar datos", Toast.LENGTH_SHORT).show();
                    }
                }
            }

            @Override
            public void onFailure(Call<DashboardResponse> call, Throwable t) {
                Toast.makeText(MainActivity.this, "Error de conexión al dashboard", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void configurarMenu() {
        btnRutas.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, RutaActivity.class);
            // Si necesitas pasar el ID del usuario:
            intent.putExtra("usuario_id", usuarioId);
            startActivity(intent);
        });

        btnExamen.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, ExamenActivity.class);
            intent.putExtra("usuario_id", usuarioId);
            startActivity(intent);
        });
        btnPractica.setOnClickListener(v -> Toast.makeText(this, "Modo Práctica", Toast.LENGTH_SHORT).show());
        btnProgreso.setOnClickListener(v -> {
            // Importamos explícitamente ProgresoActivity desde su paquete de actividades
            Intent intent = new Intent(MainActivity.this, com.example.blossom.activities.ProgresoActivity.class);
            // Le inyectamos el ID real de la sesión para que Flask cargue sus datos correspondientes
            intent.putExtra("usuario_id", usuarioId);
            startActivity(intent);
        });
        btnTutor.setOnClickListener(v -> {
            // Asegúrate de importar la clase TutorActivity (si te sale error en el nombre, presiona Alt+Enter)
            Intent intent = new Intent(MainActivity.this, com.example.blossom.activities.TutorActivity.class);
            // Pasamos el ID por si más adelante quieres personalizar la IA según el nivel del usuario
            intent.putExtra("usuario_id", usuarioId);
            startActivity(intent);
        });
        btnPerfil.setOnClickListener(v -> {
            // Abrimos PerfilActivity pasando el ID del usuario
            Intent intent = new Intent(MainActivity.this, com.example.blossom.activities.PerfilActivity.class);
            intent.putExtra("usuario_id", usuarioId);
            startActivity(intent);
        });
    }
}