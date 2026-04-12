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
    const div = document.createElement('div');
    div.className = 'ejercicio-item'; // Asegúrate que esta clase tenga estilo en style.css
    div.innerHTML = `
        <p><strong>Pregunta ${index + 1}:</strong> ${ej.pregunta}</p>
        <input type="text" id="resp-${index}" placeholder="Tu respuesta">
        <button type="button" class="btn-validar" onclick="validarIndividual(${index}, '${ej.solucion}', this)">
            Validar
        </button>
    `;
    contenedor.appendChild(div);
});
}

function validarIndividual(index, solucion, boton) {
    const input = document.getElementById(`resp-${index}`);
    // Comparamos strings para evitar problemas con decimales o formatos
    if (input.value.trim() == solucion.trim()) {
        aciertos++;
        boton.classList.add('saved');
        boton.innerText = "¡Correcto!";
        boton.disabled = true; // Desactivamos el botón para no sumar aciertos dobles
        input.disabled = true;
    } else {
        boton.style.backgroundColor = "#e74c3c";
        boton.innerText = "Revisar";
    }
}

async function finalizarSesion() {
    console.log("Enviando resultados...", { total: totalEjercicios, aciertos: aciertos, tema: TEMA_ACTUAL });

    // 1. Preparamos los datos
    const data = {
        aciertos: aciertos,
        total: totalEjercicios,
        tema: TEMA_ACTUAL
    };

    try {
        // 2. Intentamos enviar la petición
        const response = await fetch('/finalizar_practica', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        // 3. Verificamos si el servidor respondió bien (status 200)
        if (!response.ok) {
            throw new Error('No se pudo guardar el progreso en el servidor');
        }

        const resultado = await response.json();

        // 4. Si el servidor dice que todo ok, redirigimos
        if (resultado.status === "success") {
            alert("¡Progreso guardado con éxito!");
            window.location.href = "/resultados"; // O "/progreso", según prefieras
        } else {
            alert("Error: " + (resultado.message || "Error desconocido"));
        }

    } catch (error) {
        // 5. Si no hay internet o el servidor falló, avisamos
        console.error("Error al enviar datos:", error);
        alert("¡Ups! Hubo un problema de conexión. No cierres la página e intenta de nuevo.");
        
        // Si tienes un botón de reintentar en tu HTML, aquí se muestra
        const btnReintentar = document.getElementById('btn-reintentar');
        if (btnReintentar) {
            btnReintentar.style.display = 'block';
        }
    }
}

window.onload = renderizarEjercicios;