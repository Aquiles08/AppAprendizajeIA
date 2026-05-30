let aciertos = 0;
let totalEjercicios;
const contenedor = document.getElementById('contenedor-ejercicios');

// --- NUEVO: Capturamos el momento exacto en que carga la práctica ---
const tiempoInicio = Date.now(); 

function renderizarEjercicios() {
    totalEjercicios = EJERCICIOS_DATA.length;
    const contenedor = document.getElementById('contenedor-ejercicios'); 
    
    if (!EJERCICIOS_DATA || EJERCICIOS_DATA.length === 0) {
        contenedor.innerHTML = "<p>No hay ejercicios disponibles para este tema.</p>";
        return;
    }
    contenedor.innerHTML = "";

    EJERCICIOS_DATA.forEach((ej, index) => {
        const i = index + 1;
        const div = document.createElement('div');
        div.className = 'ejercicio-item';
        div.innerHTML = `
            <p><strong>Pregunta ${i}:</strong> ${ej.pregunta}</p>
            <input type="text" name="respuesta_usuario_${i}" id="resp-${index}" placeholder="Tu respuesta">
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
    const cleanUser = input.value.replace(/\s+/g, '').toLowerCase();
    const cleanCorrect = String(solucion).replace(/\s+/g, '').toLowerCase();

    if (cleanUser === cleanCorrect) {
        aciertos++;
        boton.classList.add('saved');
        boton.innerText = "¡Correcto!";
        boton.disabled = true;
        input.readOnly = true;
    } else {
        boton.style.backgroundColor = "#e74c3c";
        boton.innerText = "Revisar";
    }
}

async function finalizarSesion() {
    const tiempoFinal = Date.now();
    const segundosTranscurridos = Math.floor((tiempoFinal - tiempoInicio) / 1000);

    // Mapeamos los resultados de cada ejercicio para la página de resultados
    const detallesRespuestas = EJERCICIOS_DATA.map((ej, index) => {
        const input = document.getElementById(`resp-${index}`);
        const userRes = input.value.trim();
        const correctRes = String(ej.solucion).trim();
        
        return {
            pregunta: ej.pregunta,
            tu_respuesta: userRes,
            correcta: ej.solucion,
            explicacion: ej.explicacion,
            es_correcta: (userRes.replace(/\s+/g, '').toLowerCase() === correctRes.replace(/\s+/g, '').toLowerCase())
        };
    });

    const data = {
        aciertos: Number(aciertos),
        total: Number(totalEjercicios),
        tema: String(TEMA_ACTUAL),
        tiempo: segundosTranscurridos,
        detalles: detallesRespuestas // <--- El paquete completo
    };

    try {
        const response = await fetch('/procesar_practica_json', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const resultado = await response.json();

        if (resultado.status === "success") {
            // Cambiamos el redireccionamiento a la ruta correcta
            window.location.href = "resultado_practica"; 
        } else {
            alert("Error: " + resultado.message);
        }
    } catch (error) {
        console.error("Error en fetch:", error);
    }
}

window.onload = renderizarEjercicios;