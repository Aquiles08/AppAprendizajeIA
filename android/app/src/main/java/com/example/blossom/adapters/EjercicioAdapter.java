package com.example.blossom.adapters;

import android.graphics.Color;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.blossom.R;
import com.example.blossom.models.PracticaResponse;
import com.example.blossom.models.ProcesarPracticaRequest.DetalleIntento;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class EjercicioAdapter extends RecyclerView.Adapter<EjercicioAdapter.EjercicioViewHolder> {

    private List<PracticaResponse.Ejercicio> listaEjercicios;
    // Mapas para recordar qué contestó el usuario y cuáles ya validó como buenas o malas
    private HashMap<Integer, String> respuestasUsuario = new HashMap<>();
    private HashMap<Integer, Boolean> estadoValidacion = new HashMap<>(); // true = correcto, false = revisar

    public EjercicioAdapter(List<PracticaResponse.Ejercicio> listaEjercicios) {
        this.listaEjercicios = listaEjercicios;
    }

    @NonNull
    @Override
    public EjercicioViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_ejercicio, parent, false);
        return new EjercicioViewHolder(v);
    }

    // 🔥 CON ESTO OBLIGAMOS A LINT A IGNORAR LA ADVERTENCIA DE LA POSICIÓN FIJA
    @SuppressWarnings("RecyclerView")
    @Override
    public void onBindViewHolder(@NonNull EjercicioViewHolder holder, int position) {
        // Obtenemos la posición real del adaptador desde el inicio
        int posReal = holder.getAdapterPosition();
        if (posReal == RecyclerView.NO_POSITION) {
            posReal = position; // Respaldo inicial seguro por si la vista no se ha acoplado
        }

        PracticaResponse.Ejercicio ej = listaEjercicios.get(posReal);

        // 1. Asignar el enunciado de la ecuación
        holder.tvNumeroYPregunta.setText("Pregunta " + ej.getId() + ": " + ej.getPregunta());

        // Remover TextWatchers viejos para evitar que al reciclar escriba en posiciones incorrectas
        if (holder.textWatcher != null) {
            holder.etRespuesta.removeTextChangedListener(holder.textWatcher);
        }

        // Evitar que el RecyclerView duplique o borre textos al hacer scroll
        holder.etRespuesta.setText(respuestasUsuario.getOrDefault(posReal, ""));

        // 🔥 RESPALDO EN TIEMPO REAL: Guardado dinámico sin usar la variable 'position' del método
        holder.textWatcher = new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                int posActual = holder.getAdapterPosition();
                if (posActual != RecyclerView.NO_POSITION) {
                    respuestasUsuario.put(posActual, s.toString().trim());
                }
            }

            @Override
            public void afterTextChanged(Editable s) {}
        };
        holder.etRespuesta.addTextChangedListener(holder.textWatcher);

        // 2. RESTAURAR ESTADOS VISUALES BLINDADO
        if (estadoValidacion.containsKey(posReal)) {
            boolean esCorrecto = estadoValidacion.get(posReal);
            if (esCorrecto) {
                holder.btnValidar.setText("¡Correcto!");
                holder.btnValidar.setBackgroundColor(Color.parseColor("#2ECC71")); // Verde

                // Si ya es correcta, se queda congelada de verdad
                holder.btnValidar.setEnabled(false);
                holder.etRespuesta.setEnabled(false);
            } else {
                holder.btnValidar.setText("Revisar");
                holder.btnValidar.setBackgroundColor(Color.parseColor("#E74C3C")); // Rojo

                // Si está en revisar, el usuario DEBE poder corregir
                holder.btnValidar.setEnabled(true);
                holder.etRespuesta.setEnabled(true);
            }
        } else {
            // Estado por defecto: Pregunta limpia / No validada aún
            holder.btnValidar.setText("Validar");
            holder.btnValidar.setBackgroundColor(Color.parseColor("#6D2BCE")); // Morado

            // Forzamos a liberar los controles para las nuevas preguntas reciclándose
            holder.btnValidar.setEnabled(true);
            holder.etRespuesta.setEnabled(true);
        }

        // 3. EVENTO DEL BOTÓN VALIDAR OPTIMIZADO
        holder.btnValidar.setOnClickListener(v -> {
            int posActual = holder.getAdapterPosition();
            if (posActual == RecyclerView.NO_POSITION) return;

            String textoIngresado = holder.etRespuesta.getText().toString();

            if (textoIngresado.trim().isEmpty()) {
                Toast.makeText(v.getContext(), "Por favor, escribe una respuesta primero", Toast.LENGTH_SHORT).show();
                return;
            }

            // Guardamos en el mapa global usando la posición dinámica calculada al momento
            respuestasUsuario.put(posActual, textoIngresado.trim());

            PracticaResponse.Ejercicio ejercicioActual = listaEjercicios.get(posActual);

            // Limpieza matemática: sin espacios y en minúsculas
            String cleanUser = textoIngresado.replaceAll("\\s+", "").toLowerCase();
            String solucionIA = ejercicioActual.getRespuestaCorrecta() != null ? ejercicioActual.getRespuestaCorrecta() : "";
            String cleanCorrect = solucionIA.replaceAll("\\s+", "").toLowerCase();

            // Logs de control
            Log.d("DEBUG_BLOSSOM_COMPARA", "Boton pulsado en Posicion: " + posActual);
            Log.d("DEBUG_BLOSSOM_COMPARA", "USUARIO ESCRITO: [" + cleanUser + "]");
            Log.d("DEBUG_BLOSSOM_COMPARA", "BACKEND SOLUCION: [" + cleanCorrect + "]");

            // Comparación
            if (cleanUser.equals(cleanCorrect)) {
                estadoValidacion.put(posActual, true);
                holder.btnValidar.setText("¡Correcto!");
                holder.btnValidar.setBackgroundColor(Color.parseColor("#2ECC71"));

                holder.btnValidar.setEnabled(false);
                holder.etRespuesta.setEnabled(false);
            } else {
                estadoValidacion.put(posActual, false);
                holder.btnValidar.setText("Revisar");
                holder.btnValidar.setBackgroundColor(Color.parseColor("#E74C3C"));
            }
        });
    }

    @Override
    public int getItemCount() {
        return listaEjercicios != null ? listaEjercicios.size() : 0;
    }

    // --- MÉTODOS PÚBLICOS PARA RETORNAR LOS RESULTADOS A LA ACTIVITY ---

    public int obtenerCantidadAciertos() {
        int aciertos = 0;
        for (Boolean correcto : estadoValidacion.values()) {
            if (correcto) aciertos++;
        }
        return aciertos;
    }

    public List<DetalleIntento> obtenerDetallesParaBackend() {
        List<DetalleIntento> detalles = new ArrayList<>();
        for (int i = 0; i < listaEjercicios.size(); i++) {
            PracticaResponse.Ejercicio ej = listaEjercicios.get(i);
            String respuestaDelChavo = respuestasUsuario.getOrDefault(i, "");

            String cleanUser = respuestaDelChavo.replaceAll("\\s+", "").toLowerCase();
            String cleanCorrect = (ej.getRespuestaCorrecta() != null ? ej.getRespuestaCorrecta() : "").replaceAll("\\s+", "").toLowerCase();
            boolean esCorrecta = cleanUser.equals(cleanCorrect);

            detalles.add(new DetalleIntento(
                    ej.getPregunta(),
                    respuestaDelChavo,
                    ej.getRespuestaCorrecta(),
                    ej.getExplicacion() != null ? ej.getExplicacion() : "Sin explicación",
                    esCorrecta
            ));
        }
        return detalles;
    }

    public List<PracticaResponse.Ejercicio> getListaEjercicios() {
        return listaEjercicios;
    }

    public String getRespuestaEnPosicion(int posicion) {
        if (respuestasUsuario != null && respuestasUsuario.containsKey(posicion)) {
            return respuestasUsuario.get(posicion);
        }
        return "";
    }

    static class EjercicioViewHolder extends RecyclerView.ViewHolder {
        TextView tvNumeroYPregunta;
        EditText etRespuesta;
        Button btnValidar;
        TextWatcher textWatcher;

        EjercicioViewHolder(View v) {
            super(v);
            tvNumeroYPregunta = v.findViewById(R.id.tvNumeroYPregunta);
            etRespuesta = v.findViewById(R.id.etRespuestaUsuario);
            btnValidar = v.findViewById(R.id.btnValidarIndividual);
        }
    }
}