package com.example.blossom.activities;

import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.blossom.R;
import com.example.blossom.adapters.ModuloAdapter;
import com.example.blossom.models.RutaAprendizaje;
import com.example.blossom.network.RetrofitClient;
import java.util.HashMap;

public class RutaActivity extends AppCompatActivity {
    private static final String TAG = "DEBUG_BLOSSOM";
    private RecyclerView rvModulos;
    private TextView tvProximoReto;
    private int usuarioIdLogueado;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ruta);

        // 1. Vincular los componentes del XML
        rvModulos = findViewById(R.id.rvModulos);
        tvProximoReto = findViewById(R.id.tvProximoReto);

        // 2. Configurar obligatoriamente el LayoutManager para el RecyclerView
        rvModulos.setLayoutManager(new LinearLayoutManager(this));

        // 3. OBTENER EL ID DINÁMICO: Recuperamos el ID real enviado desde la pantalla anterior.
        // Si no se encuentra, por defecto usará el ID 1 como respaldo.
        usuarioIdLogueado = getIntent().getIntExtra("usuario_id", 1);
        Log.d(TAG, "RutaActivity iniciada para el usuario_id: " + usuarioIdLogueado);

        // 4. Consumir la API de Flask
        cargarDatosRuta();
    }

    private void cargarDatosRuta() {
        // Preparar los parámetros en formato JSON para la petición POST
        HashMap<String, Object> params = new HashMap<>();
        params.put("usuario_id", usuarioIdLogueado);

        RetrofitClient.getApiService().obtenerRutaAprendizaje(params).enqueue(new retrofit2.Callback<RutaAprendizaje>() {
            @Override
            public void onResponse(retrofit2.Call<RutaAprendizaje> call, retrofit2.Response<RutaAprendizaje> response) {
                if (response.isSuccessful() && response.body() != null) {
                    RutaAprendizaje data = response.body();

                    // Imprimir en consola el estado de la respuesta para monitoreo
                    if (data.modulos != null) {
                        Log.d(TAG, "API Exitosa. Módulos recibidos del servidor: " + data.modulos.size());
                    } else {
                        Log.d(TAG, "API Exitosa pero la lista de módulos llegó NULL");
                    }

                    // 1. Actualizar de forma segura el banner del próximo reto
                    if (data.ruta != null && data.ruta.reto != null && !data.ruta.reto.isEmpty()) {
                        tvProximoReto.setText("¡Vas por excelente camino! Tu próximo reto es: " + data.ruta.reto);
                    } else {
                        tvProximoReto.setText("¡Vas por excelente camino! Sigue avanzando en tus módulos.");
                    }

                    // 2. Validar, enlazar e inflar los datos en el RecyclerView
                    if (data.modulos != null && !data.modulos.isEmpty()) {
                        ModuloAdapter adapter = new ModuloAdapter(data.modulos, usuarioIdLogueado);
                        rvModulos.setAdapter(adapter);
                    } else {
                        Log.w(TAG, "La lista de módulos está vacía en el JSON de respuesta.");
                        Toast.makeText(RutaActivity.this, "No se encontraron temas asignados para tu usuario.", Toast.LENGTH_LONG).show();
                    }

                } else {
                    Log.e(TAG, "Error en la respuesta. Código del servidor: " + response.code());
                    Toast.makeText(RutaActivity.this, "Error en la respuesta del servidor", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(retrofit2.Call<RutaAprendizaje> call, Throwable t) {
                Log.e(TAG, "Falla de red crítica al conectar con /api/ruta", t);
                Toast.makeText(RutaActivity.this, "Error de red: No se pudo conectar con el servidor", Toast.LENGTH_SHORT).show();
            }
        });
    }
}