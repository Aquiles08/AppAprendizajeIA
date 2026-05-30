package com.example.blossom.activities;

import android.content.Intent;
import android.os.Bundle;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import com.example.blossom.R;
import com.example.blossom.models.PerfilResponse;
import com.example.blossom.models.PerfilUpdateRequest; // Asegúrate de tener este modelo
import com.example.blossom.network.RetrofitClient;
import java.util.*;
import retrofit2.*;

public class PerfilActivity extends AppCompatActivity {

    private Spinner spinnerModo;
    private Button btnGuardar, btnCerrarSesion;
    private CheckBox cb1, cb2, cb3, cb4;
    private int usuarioId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_perfil);

        usuarioId = getIntent().getIntExtra("usuario_id", -1);

        // Inicializar vistas
        spinnerModo = findViewById(R.id.spinnerModo);
        btnGuardar = findViewById(R.id.btnGuardar);
        btnCerrarSesion = findViewById(R.id.btnCerrarSesion);
        cb1 = findViewById(R.id.cb1);
        cb2 = findViewById(R.id.cb2);
        cb3 = findViewById(R.id.cb3);
        cb4 = findViewById(R.id.cb4);

        // Configurar Spinner
        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
                R.array.modos_tutor, android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerModo.setAdapter(adapter);

        // Acciones
        cargarDatos();
        btnGuardar.setOnClickListener(v -> guardarDatos());
        btnCerrarSesion.setOnClickListener(v -> cerrarSesion());
    }

    private void cargarDatos() {
        // Debes tener definido este método en tu ApiService
        RetrofitClient.getApiService().obtenerPerfil(usuarioId).enqueue(new Callback<PerfilResponse>() {
            @Override
            public void onResponse(Call<PerfilResponse> call, Response<PerfilResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    PerfilResponse res = response.body();

                    // Seleccionar Spinner
                    ArrayAdapter<CharSequence> adapter = (ArrayAdapter) spinnerModo.getAdapter();
                    int pos = adapter.getPosition(res.tutor_mode);
                    spinnerModo.setSelection(pos);

                    // Marcar Checkboxes basándose en el string recibido (ej: "Fundamentos,Polinomios")
                    String temas = res.enfoque_temas;
                    cb1.setChecked(temas.contains("Fundamentos"));
                    cb2.setChecked(temas.contains("Lenguaje Algebraico"));
                    cb3.setChecked(temas.contains("Polinomios"));
                    cb4.setChecked(temas.contains("Factorización"));
                }
            }
            @Override
            public void onFailure(Call<PerfilResponse> call, Throwable t) {
                Toast.makeText(PerfilActivity.this, "Error cargando perfil", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void guardarDatos() {
        String modo = spinnerModo.getSelectedItem().toString();
        StringBuilder temas = new StringBuilder();

        if (cb1.isChecked()) temas.append("Fundamentos,");
        if (cb2.isChecked()) temas.append("Lenguaje Algebraico,");
        if (cb3.isChecked()) temas.append("Polinomios,");
        if (cb4.isChecked()) temas.append("Factorización,");

        PerfilUpdateRequest request = new PerfilUpdateRequest(usuarioId, modo, temas.toString());

        RetrofitClient.getApiService().actualizarPerfil(request).enqueue(new Callback<Void>() {
            @Override
            public void onResponse(Call<Void> call, Response<Void> response) {
                if (response.isSuccessful()) {
                    Toast.makeText(PerfilActivity.this, "Preferencias guardadas", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(PerfilActivity.this, "Error al guardar", Toast.LENGTH_SHORT).show();
                }
            }
            @Override
            public void onFailure(Call<Void> call, Throwable t) {
                Toast.makeText(PerfilActivity.this, "Fallo de conexión", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void cerrarSesion() {
        // Fíjate bien en el paquete: .activities.LoginActivity
        Intent intent = new Intent(PerfilActivity.this, com.example.blossom.activities.LoginActivity.class);

        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }
}