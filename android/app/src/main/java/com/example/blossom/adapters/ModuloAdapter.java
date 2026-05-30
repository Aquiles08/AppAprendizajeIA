package com.example.blossom.adapters;

import android.content.Intent;
import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.blossom.R;
import com.example.blossom.models.RutaAprendizaje;
import java.util.List;

public class ModuloAdapter extends RecyclerView.Adapter<ModuloAdapter.ModuloViewHolder> {
    private List<RutaAprendizaje.Modulo> listaModulos;
    private int usuarioId;

    public ModuloAdapter(List<RutaAprendizaje.Modulo> lista, int usuarioId) {
        this.listaModulos = lista;
        this.usuarioId = usuarioId;
    }

    @NonNull
    @Override
    public ModuloViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_modulo, parent, false);
        return new ModuloViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull ModuloViewHolder holder, int position) {
        RutaAprendizaje.Modulo m = listaModulos.get(position);

        holder.tvNombre.setText(m.nombre);
        holder.tvPorcentaje.setText(m.progreso + " %");
        holder.progressBar.setProgress(m.progreso);

        // Lógica de estados
        if (m.status.equals("completado")) {
            holder.btnAccion.setText("Repasar");
            holder.btnAccion.setBackgroundColor(Color.parseColor("#6D2BCE")); // Morado
        } else if (m.status.equals("disponible")) {
            holder.btnAccion.setText("Iniciar");
            holder.btnAccion.setBackgroundColor(Color.parseColor("#6D2BCE"));
        } else {
            holder.btnAccion.setText("Bloqueado");
            holder.btnAccion.setBackgroundColor(Color.parseColor("#CCCCCC")); // Gris
            holder.btnAccion.setEnabled(false);
        }
        holder.btnAccion.setOnClickListener(v -> {
            // Creamos el Intent apuntando a tu nueva PracticaActivity
            Intent intent = new Intent(v.getContext(), com.example.blossom.activities.PracticaActivity.class);

            // Pasamos las variables dinámicas que capturamos del adaptador
            intent.putExtra("usuario_id", usuarioId); // El ID del usuario logueado (que le inyectamos al constructor)
            intent.putExtra("tema_id", m.id);         // El ID del módulo/tema seleccionado

            // Lanzamos la pantalla
            v.getContext().startActivity(intent);
        });
    }

    @Override
    public int getItemCount() { return listaModulos.size(); }

    static class ModuloViewHolder extends RecyclerView.ViewHolder {
        TextView tvNombre, tvPorcentaje;
        ProgressBar progressBar;
        Button btnAccion;

        ModuloViewHolder(View v) {
            super(v);
            tvNombre = v.findViewById(R.id.tvNombreTema);
            tvPorcentaje = v.findViewById(R.id.tvPorcentaje);
            progressBar = v.findViewById(R.id.progressBarTema);
            btnAccion = v.findViewById(R.id.btnAccion);
        }
    }
}