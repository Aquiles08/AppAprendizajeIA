let aciertos = 0;
// Usamos la longitud de listaEjercicios (que viene del HTML)
const totalEjercicios = listaEjercicios.length; 
const contenedor = document.getElementById('contenedor-ejercicios');

function renderizarEjercicios() {
    if (!contenedor) return;
    contenedor.innerHTML = ''; 

    listaEjercicios.forEach((ejercicio, index) => {
        const card = document.createElement('div');
        card.className = 'ejercicio-card';
        card.innerHTML = `
            <div class="ejercicio-header">
                <span class="ejercicio-numero">Ejercicio ${index + 1}.</span>
                <p class="ejercicio-enunciado">${ejercicio.pregunta}</p>
            </div>
            <input type="text" 
                   id="resp-${index}" 
                   class="input-respuesta" 
                   placeholder="Tu respuesta">
            
            <button type="button" 
                    class="btn-guardar-local" 
                    onclick="validarIndividual(${index}, '${ejercicio.solucion}', this)">
                Guardar respuesta
            </button>
        `;
        contenedor.appendChild(card);
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

function finalizarSesion() {
    console.log("Enviando resultados...", { total: totalEjercicios, aciertos: aciertos });

    fetch('/finalizar_practica', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            total: totalEjercicios,
            aciertos: aciertos
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Error en la respuesta del servidor');
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            window.location.href = "/resultados"; 
        } else {
            alert("Error: " + (data.message || "No se pudo guardar el progreso"));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Ocurrió un error al conectar con el servidor.");
    });
}

window.onload = renderizarEjercicios;