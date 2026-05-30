package com.example.blossom.activities;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.blossom.MainActivity;
import com.example.blossom.R;
import com.example.blossom.models.LoginRequest;
import com.example.blossom.models.LoginResponse;
import com.example.blossom.network.ApiService;
import com.example.blossom.network.RetrofitClient;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginActivity extends AppCompatActivity {

    private TextInputEditText etCorreo, etContrasena;
    private MaterialButton btnIniciarSesion;
    private TextView tvIrARegistro;
    private ApiService apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        // Enlazar componentes de la interfaz
        etCorreo = findViewById(R.id.etCorreo);
        etContrasena = findViewById(R.id.etContrasena);
        btnIniciarSesion = findViewById(R.id.btnIniciarSesion);
        tvIrARegistro = findViewById(R.id.tvIrARegistro);

        // Inicializar servicio de red
        apiService = RetrofitClient.getApiService();

        // Botón Iniciar Sesión
        btnIniciarSesion.setOnClickListener(v -> ejecutarLogin());

        // Texto para ir a pantalla de Registro
        tvIrARegistro.setOnClickListener(v -> {
            Intent intent = new Intent(LoginActivity.this, RegistroActivity.class);
            startActivity(intent);
        });
    }

    private void ejecutarLogin() {
        String correo = etCorreo.getText().toString().trim();
        String contrasena = etContrasena.getText().toString().trim();

        if (correo.isEmpty() || contrasena.isEmpty()) {
            Toast.makeText(this, "Por favor llena todos los campos", Toast.LENGTH_SHORT).show();
            return;
        }

        LoginRequest peticion = new LoginRequest(correo, contrasena);

        apiService.iniciarSesion(peticion).enqueue(new Callback<LoginResponse>() {
            @Override
            public void onResponse(Call<LoginResponse> call, Response<LoginResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    LoginResponse res = response.body();

                    if (res.isSuccess()) {
                        Toast.makeText(LoginActivity.this, "¡Bienvenido " + res.getNombre() + "!", Toast.LENGTH_SHORT).show();

                        // Saltamos al Dashboard enviando el ID del usuario real usando tu variable "res"
                        Intent intent = new Intent(LoginActivity.this, MainActivity.class);
                        intent.putExtra("usuario_id", res.getUsuarioId());
                        startActivity(intent);
                        finish(); // Cerramos login para que no se regrese al dar "Atrás"
                    } else {
                        Toast.makeText(LoginActivity.this, res.getMensaje(), Toast.LENGTH_LONG).show();
                    }
                } else {
                    Toast.makeText(LoginActivity.this, "Error en credenciales", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<LoginResponse> call, Throwable t) {
                Log.e("LOGIN_ERROR", "Fallo de red", t);
                Toast.makeText(LoginActivity.this, "Fallo de conexión con el servidor", Toast.LENGTH_LONG).show();
            }
        });
    }
}