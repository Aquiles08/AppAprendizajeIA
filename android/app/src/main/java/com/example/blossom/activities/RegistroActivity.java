package com.example.blossom.activities;

import android.os.Bundle;
import android.util.Log;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.blossom.R;
import com.example.blossom.models.RegistroRequest;
import com.example.blossom.models.RegistroResponse;
import com.example.blossom.network.RetrofitClient;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class RegistroActivity extends AppCompatActivity {

    private TextInputEditText etNombre, etCorreo, etContrasena;
    private RadioGroup rgRol;
    private RadioButton rbEstudiante;
    private MaterialButton btnRegistrarse;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_registro);

        // Enlazar vistas
        etNombre = findViewById(R.id.etRegNombre);
        etCorreo = findViewById(R.id.etRegCorreo);
        etContrasena = findViewById(R.id.etRegContrasena);
        rgRol = findViewById(R.id.rgRol);
        rbEstudiante = findViewById(R.id.rbEstudiante);
        btnRegistrarse = findViewById(R.id.btnRegistrarse);

        // Acción al pulsar el botón registrar
        btnRegistrarse.setOnClickListener(v -> ejecutarRegistro());
    }

    private void ejecutarRegistro() {
        String nombre = etNombre.getText().toString().trim();
        String correo = etCorreo.getText().toString().trim();
        String contrasena = etContrasena.getText().toString().trim();

        // Validar cuál RadioButton está marcado para definir el texto del Rol
        String rol = rbEstudiante.isChecked() ? "estudiante" : "profesor";

        if (nombre.isEmpty() || correo.isEmpty() || contrasena.isEmpty()) {
            Toast.makeText(this, "Por favor completa todos los campos", Toast.LENGTH_SHORT).show();
            return;
        }

        RegistroRequest peticion = new RegistroRequest(nombre, correo, contrasena, rol);

        // Llamamos directamente usando tu método getApiService()
        RetrofitClient.getApiService().registrarUsuario(peticion).enqueue(new Callback<RegistroResponse>() {
            @Override
            public void onResponse(Call<RegistroResponse> call, Response<RegistroResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    RegistroResponse res = response.body();

                    if (res.isSuccess()) {
                        Toast.makeText(RegistroActivity.this, "¡Cuenta creada con éxito!", Toast.LENGTH_SHORT).show();
                        finish(); // Cierra el registro y regresa automáticamente al Login
                    } else {
                        Toast.makeText(RegistroActivity.this, res.getMensaje(), Toast.LENGTH_LONG).show();
                    }
                } else {
                    Toast.makeText(RegistroActivity.this, "Error al procesar el registro", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<RegistroResponse> call, Throwable t) {
                Log.e("REGISTRO_ERROR", "Fallo de red al registrar", t);
                Toast.makeText(RegistroActivity.this, "No se pudo conectar con el servidor", Toast.LENGTH_LONG).show();
            }
        });
    }
}