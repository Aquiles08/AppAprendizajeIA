package com.example.blossom.adapters;

import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.blossom.R;
import com.example.blossom.models.ResultadoPracticaResponse.DetalleReporte;
import java.util.List;

public class ResultadoAdapter extends RecyclerView.Adapter<ResultadoAdapter.ResultadoViewHolder> {

    private List<DetalleReporte> listaDetalles;

    public ResultadoAdapter(List<DetalleReporte> listaDetalles) {
        this.listaDetalles = listaDetalles;
    }

    @NonNull
    @Override
    public ResultadoViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_resultado, parent, false);
        return new ResultadoViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull ResultadoViewHolder holder, int position) {
        DetalleReporte item = listaDetalles.get(position);

        holder.tvPregunta.setText("Pregunta " + (position + 1) + ". \"" + item.getPregunta() + "\"");

        // Manejo de respuesta vacía o nula
        String usrResp = item.getRespuestaUsuario();
        if (usrResp == null || usrResp.trim().isEmpty()) {
            holder.tvRespuestaUsuario.setText("Sin respuesta");
            holder.tvRespuestaUsuario.setTextColor(Color.GRAY);
        } else {
            holder.tvRespuestaUsuario.setText(usrResp);
            holder.tvRespuestaUsuario.setTextColor(Color.BLACK);
        }

        holder.tvSolucionCorrecta.setText("La respuesta correcta era: " + item.getRespuestaCorrecta());

        // Configuración de Íconos de Éxito / Error
        if (item.isCorrecta()) {
            holder.ivStatus.setImageResource(android.R.drawable.checkbox_on_background); // Cambiar por tus vectores nativos
            holder.ivStatus.setColorFilter(Color.parseColor("#2ECC71"));
        } else {
            holder.ivStatus.setImageResource(android.R.drawable.ic_delete); // Cruz o tacha
            holder.ivStatus.setColorFilter(Color.parseColor("#E74C3C"));
        }

        // Lógica de Renderizado de la Explicación de la IA (Clave de tus capturas)
        if (item.getExplicacion() == null ||
                item.getExplicacion().trim().isEmpty() ||
                item.getExplicacion().equalsIgnoreCase("Sin explicación")) {
            holder.layoutExplicacion.setVisibility(View.GONE);
        } else {
            holder.layoutExplicacion.setVisibility(View.VISIBLE);
            holder.tvExplicacion.setText(item.getExplicacion());
        }
    }

    @Override
    public int getItemCount() {
        return listaDetalles != null ? listaDetalles.size() : 0;
    }

    static class ResultadoViewHolder extends RecyclerView.ViewHolder {
        TextView tvPregunta, tvRespuestaUsuario, tvExplicacion, tvSolucionCorrecta;
        ImageView ivStatus;
        LinearLayout layoutExplicacion;

        ResultadoViewHolder(View v) {
            super(v);
            tvPregunta = v.findViewById(R.id.tvResultadoPregunta);
            tvRespuestaUsuario = v.findViewById(R.id.tvRespuestaUsuario);
            tvExplicacion = v.findViewById(R.id.tvExplicacionIa);
            tvSolucionCorrecta = v.findViewById(R.id.tvSolucionCorrecta);
            ivStatus = v.findViewById(R.id.ivStatusIcon);
            layoutExplicacion = v.findViewById(R.id.layoutExplicacionIa);
        }
    }
}