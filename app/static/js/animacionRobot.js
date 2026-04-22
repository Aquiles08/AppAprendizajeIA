// --- Configuración de Imágenes de Estados (Cada uno tiene 3 poses) ---
const poseImages = {
    'NORMAL': [
        '/static/img/estadoNormal1.png', 
        '/static/img/estadoNormal2.png', 
        '/static/img/estadoNormal3.png'
    ],
    'PROCESANDO': [
        '/static/img/estadoProcesando1.png', 
        '/static/img/estadoProcesando2.png', 
        '/static/img/estadoProcesando3.png'
    ],
    'RESOLUCION': [
        '/static/img/estadoResolucion1.png', 
        '/static/img/estadoResolucion2.png', 
        '/static/img/estadoResolucion3.png'
    ]
};

// --- Estado Inicial ---
let currentState = 'NORMAL';
let animationInterval; // Bucle de tiempo

// --- Elementos del DOM ---
const robotImage = document.getElementById('robotAnimated');
const chatForm = document.getElementById('chatForm');

// --- Función para cambiar a un estado y reiniciar la animación ---
function setRobotState(newState) {
    if (!poseImages[newState]) return; // Validación de estado
    
    console.log(`Cambiando estado robot a: ${newState}`);
    currentState = newState;
    
    // 1. Limpiamos el bucle de tiempo anterior
    clearInterval(animationInterval);
    
    // 2. Iniciamos el nuevo bucle (Cambia imagen cada 2 segundos)
    animationInterval = setInterval(updateRandomPose, 2000);
    
    // 3. Forzamos un cambio de pose inmediato
    updateRandomPose();
}

// --- Función para elegir una pose aleatoria de las 3 del estado actual ---
function updateRandomPose() {
    const currentPoses = poseImages[currentState];
    const randomIndex = Math.floor(Math.random() * currentPoses.length);
    const newPoseSrc = currentPoses[randomIndex];
    
    // Actualizamos el src de la imagen con una transición suave
    robotImage.style.opacity = 0; // Se desvanece
    setTimeout(() => {
        robotImage.src = newPoseSrc;
        robotImage.style.opacity = 1; // Reaparece
    }, 150);
}

// --- Lógica del Chat para cambiar estados ---
chatForm.addEventListener('submit', function(e) {
    e.preventDefault(); // No recargar la página

    // 1. El usuario pregunta -> Robot empieza a PENSAR
    setRobotState('PROCESANDO');

    // 2. Simulamos el tiempo que tarda la IA en contestar (3 segundos)
    setTimeout(() => {
        // 3. IA contesta -> Robot empieza a HABLAR/RESOLVER
        setRobotState('RESOLUCION');
        
        // (Opcional) 4. Después de 6 segundos hablando, vuelve a NORMAL
        setTimeout(() => setRobotState('NORMAL'), 6000);

    }, 3000); // Tarda 3 segundos en pensar
});

// --- Iniciamos la animación al cargar la página ---
setRobotState('NORMAL');

//CHAT 
// --- Lógica del Chat del Tutor ---
document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatWindow = document.getElementById('chatWindow');

    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault(); // CRUCIAL: evita que la página se recargue

            const mensaje = userInput.value.trim();
            if (mensaje === "") return;

            // 1. Pintar tu mensaje en el chat
            chatWindow.innerHTML += `
                <div class="chat-message-user">
                    <div class="message-text">${mensaje}</div>
                </div>
            `;
            userInput.value = ""; // Limpiar input
            chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll al fondo

            // 2. Enviar a Flask
            fetch('/tutor', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensaje: mensaje })
            })
            .then(response => response.json())
            // ... dentro de tu fetch donde recibes la respuesta
            .then(data => {
                const chatWindow = document.getElementById('chatWindow');
    
                // Crear el contenedor del mensaje de la IA
                const aiMessageDiv = document.createElement('div');
                aiMessageDiv.className = 'chat-message-ai';
    
                // Parsear el Markdown a HTML
                const contenidoLimpio = marked.parse(data.respuesta);
    
                aiMessageDiv.innerHTML = `
                    <img src="/static/img/avatar_robot.png" class="chat-avatar">
                    <div class="message-text">${contenidoLimpio}</div>
                `;
    
                chatWindow.appendChild(aiMessageDiv);
    
                // IMPORTANTE: Decirle a MathJax que renderice las nuevas fórmulas
                MathJax.typesetPromise(); 
    
                chatWindow.scrollTop = chatWindow.scrollHeight;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});

function activarSimulador() {
    const input = document.getElementById('userInput');
    const form = document.getElementById('chatForm');

    // 1. Ponemos el "comando" en el input
    input.value = "Activa el Modo Simulador: Ponme un ejercicio de Ecuaciones Diferenciales o Java y califica mi respuesta paso a paso.";

    // 2. Disparamos el evento de envío (submit) del formulario
    // Esto hará que se ejecute tu función de fetch que ya tienes programada
    form.dispatchEvent(new Event('submit'));
    
    // 3. Opcional: Cambiamos algo visual para que Gael sepa que está en examen
    document.querySelector('.chat-main-column').style.boxShadow = "0 0 15px rgba(140, 82, 255, 0.5)";
}
