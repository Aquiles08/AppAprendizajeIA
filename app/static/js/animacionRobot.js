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