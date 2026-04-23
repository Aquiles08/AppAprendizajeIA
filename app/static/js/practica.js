let aciertos = 0;
let totalEjercicios;
const contenedor = document.getElementById('contenedor-ejercicios');

function renderizarEjercicios() {
    totalEjercicios = EJERCICIOS_DATA.length;
    const contenedor = document.getElementById('contenedor-ejercicios'); // Ajusta al ID de tu HTML
    
    // Si no hay ejercicios, mostramos el mensaje de carga o error
    if (!EJERCICIOS_DATA || EJERCICIOS_DATA.length === 0) {
        contenedor.innerHTML = "<p>No hay ejercicios disponibles para este tema.</p>";
        return;
    }

    // Limpiamos el mensaje de "Cargando..."
    contenedor.innerHTML = "";

    // Dibujamos cada ejercicio usando EJERCICIOS_DATA
    EJERCICIOS_DATA.forEach((ej, index) => {
    const i = index + 1; // Para manejar base 1 en el controlador
    const div = document.createElement('div');
    div.className = 'ejercicio-item';
    div.innerHTML = `
        <p><strong>Pregunta ${i}:</strong> ${ej.pregunta}</p>
        
        <input type="text" name="respuesta_usuario_${i}" id="resp-${index}" placeholder="Tu respuesta">
        
        <input type="hidden" name="pregunta_${i}" value="${ej.pregunta}">
        <input type="hidden" name="respuesta_correcta_${i}" value="${ej.solucion}">
        <input type="hidden" name="explicacion_${i}" value="${ej.explicacion}">

        <button type="button" class="btn-validar" onclick="validarIndividual(${index}, '${ej.solucion}', this)">
            Validar
        </button>
    `;
    contenedor.appendChild(div);
});
    if (window.MathJax) {
        window.MathJax.typesetPromise();
    }
}

function validarIndividual(index, solucion, boton) {
    const input = document.getElementById(`resp-${index}`);
    // Comparamos strings para evitar problemas con decimales o formatos
    if (input.value.trim() == solucion.trim()) {
        aciertos++;
        boton.classList.add('saved');
        boton.innerText = "¡Correcto!";
        boton.disabled = true; // Desactivamos el botón para no sumar aciertos dobles
        input.readOnly = true; // Mantiene el valor para el POST
    } else {
        boton.style.backgroundColor = "#e74c3c";
        boton.innerText = "Revisar";
    }
}

async function finalizarSesion() {
    const data = {
        aciertos: aciertos,
        total: totalEjercicios,
        tema: TEMA_ACTUAL
    };

    try {
        // CAMBIO AQUÍ: Asegúrate de que la ruta incluya /usuario/ si así registraste tu Blueprint
        const response = await fetch('/usuario/finalizar_practica', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Error en el servidor');

        const resultado = await response.json();
        if (resultado.status === "success") {
            window.location.href = "/dashboard"; // Redirige al éxito
        }
    } catch (error) {
        console.error("Error:", error);
        alert("¡Ups! Hubo un problema de conexión.");
    }
}

window.onload = renderizarEjercicios;