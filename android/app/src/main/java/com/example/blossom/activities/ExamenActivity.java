package com.example.blossom.activities; // O el paquete donde tengas tus actividades

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.blossom.R;
import com.example.blossom.models.PreguntaResponse;
import com.example.blossom.models.PreguntaResponse.Pregunta;
import com.example.blossom.network.ApiService;
import com.example.blossom.network.RetrofitClient;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ExamenActivity extends AppCompatActivity {

    private TextView tvNumeroPregunta, tvTagTema, tvTextoPregunta;
    private RadioGroup rgOpciones;
    private RadioButton rbOpcionA, rbOpcionB, rbOpcionC;
    private Button btnSiguiente;

    private List<Pregunta> listaPreguntas;
    private int indexActual = 0;
    private int usuarioId;

    // Aquí acumulamos las respuestas temporales: {"1":"B", "2":"A", ...}
    private Map<String, String> respuestasUsuario = new HashMap<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_examen);

        usuarioId = getIntent().getIntExtra("usuario_id", -1);
        if (usuarioId == -1) {
            Toast.makeText(this, "Sesión inválida", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        // Vincular componentes del XML
        tvNumeroPregunta = findViewById(R.id.tvNumeroPregunta);
        tvTagTema = findViewById(R.id.tvTagTema);
        tvTextoPregunta = findViewById(R.id.tvTextoPregunta);
        rgOpciones = findViewById(R.id.rgOpciones);
        rbOpcionA = findViewById(R.id.rbOpcionA);
        rbOpcionB = findViewById(R.id.rbOpcionB);
        rbOpcionC = findViewById(R.id.rbOpcionC);
        btnSiguiente = findViewById(R.id.btnSiguiente);

        // Bloquear el botón hasta que se descarguen las preguntas de la API
        btnSiguiente.setEnabled(false);

        // Cargar preguntas desde Flask
        obtenerPreguntasDeServidor();

        // Configurar clic del botón
        btnSiguiente.setOnClickListener(v -> procesarClickSiguiente());
    }

    private void obtenerPreguntasDeServidor() {
        ApiService apiService = RetrofitClient.getApiService();
        apiService.obtenerPreguntasExamen().enqueue(new Callback<PreguntaResponse>() {
            @Override
            public void onResponse(Call<PreguntaResponse> call, Response<PreguntaResponse> response) {
                if (response.isSuccessful() && response.body() != null && response.body().isSuccess()) {
                    listaPreguntas = response.body().getPreguntas();
                    if (listaPreguntas != null && !listaPreguntas.isEmpty()) {
                        btnSiguiente.setEnabled(true);
                        mostrarPreguntaActual();
                    }
                } else {
                    Toast.makeText(ExamenActivity.this, "Error al obtener el examen", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<PreguntaResponse> call, Throwable t) {
                Toast.makeText(ExamenActivity.this, "Error de red al conectar al examen", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void mostrarPreguntaActual() {
        Pregunta pregunta = listaPreguntas.get(indexActual);

        // Actualizar la UI dinámicamente con la data real de la API
        tvNumeroPregunta.setText(String.valueOf(pregunta.getId()));
        tvTagTema.setText(pregunta.getTema());
        tvTextoPregunta.setText(pregunta.getTexto());

        // Cargar los textos correspondientes de las opciones
        rbOpcionA.setText(pregunta.getOpciones().get(0));
        rbOpcionB.setText(pregunta.getOpciones().get(1));
        rbOpcionC.setText(pregunta.getOpciones().get(2));

        // Limpiar la selección anterior para la nueva pregunta
        rgOpciones.clearCheck();

        // Cambiar el texto del botón si es la última pregunta (la 12)
        if (indexActual == listaPreguntas.size() - 1) {
            btnSiguiente.setText("FINALIZAR Y VER MI RUTA");
        } else {
            btnSiguiente.setText("SIGUIENTE PREGUNTA");
        }
    }

    private void procesarClickSiguiente() {
        int checkedId = rgOpciones.getCheckedRadioButtonId();
        if (checkedId == -1) {
            Toast.makeText(this, "Por favor, selecciona una opción", Toast.LENGTH_SHORT).show();
            return;
        }

        // Mapear el ID seleccionado a su correspondiente letra estándar ("A", "B", "C")
        String letraRespuesta = "A";
        if (checkedId == R.id.rbOpcionB) {
            letraRespuesta = "B";
        } else if (checkedId == R.id.rbOpcionC) {
            letraRespuesta = "C";
        }

        Pregunta preguntaActual = listaPreguntas.get(indexActual);
        // Guardamos en el Map usando el ID de la pregunta como llave string
        respuestasUsuario.put(String.valueOf(preguntaActual.getId()), letraRespuesta);

        // Si hay más preguntas, avanzamos dinámicamente el índice
        if (indexActual < listaPreguntas.size() - 1) {
            indexActual++;
            mostrarPreguntaActual();
        } else {
            // Ya es la última pregunta, enviamos todo el paquete recopilado a Flask
            saltarAPantallaResultados();
        }
    }

    private void saltarAPantallaResultados() {
        // Deshabilitar botón para evitar clics dobles accidentales
        btnSiguiente.setEnabled(false);

        Intent intent = new Intent(ExamenActivity.this, ResultadoExamenActivity.class);
        intent.putExtra("usuario_id", usuarioId);

        // Serializamos temporalmente nuestro mapa de respuestas en un HashMap estándar para viajar por el Intent
        HashMap<String, String> respuestasMap = new HashMap<>(respuestasUsuario);
        intent.putExtra("respuestas_examen", respuestasMap);

        startActivity(intent);
        finish(); // Cerramos el examen para que no pueda regresar con el botón "Atrás"
    }
}