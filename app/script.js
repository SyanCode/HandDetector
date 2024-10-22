const video = document.getElementById('video');
const distanceElement = document.getElementById('distance');
const captureButton = document.getElementById('captureButton');
const overlayImage = document.getElementById('overlayImage');

// Connexion WebSocket
let socket = new WebSocket("ws://handdetector.onrender.com");

// Accéder à la caméra de l'utilisateur
navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
        video.srcObject = stream;
    })
    .catch((error) => {
        console.error('Erreur lors de l\'accès à la caméra:', error);
    });

// Fonction pour capturer une image depuis la vidéo
function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
}

// Ajouter un écouteur d'événement pour capturer l'image et l'envoyer au serveur via WebSocket
captureButton.addEventListener('click', () => {
    const dataURL = captureImage();
    if (!dataURL) {
        console.error('Erreur lors de la capture de l\'image.');
        return;
    }

    if (socket.readyState === WebSocket.OPEN) {
        console.log("Envoi de l'image via WebSocket.");
        socket.send(dataURL);
    } else {
        console.error("WebSocket non connecté.");
    }
});

// Gérer les messages reçus du serveur
socket.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data);
        if (data.error) {
            console.error("Erreur serveur:", data.error);
        } else if (data.distance !== undefined && data.image !== undefined) {
            distanceElement.textContent = `Distance: ${data.distance} pixels`;

            // Mettre à jour l'image avec l'overlay
            overlayImage.src = `data:image/jpeg;base64,${data.image}`;
        }
    } catch (error) {
        console.error("Erreur lors du traitement du message serveur:", error);
    }
};

socket.onopen = () => {
    console.log("WebSocket connecté.");
};

socket.onerror = (error) => {
    console.error("WebSocket erreur:", error);
};

socket.onclose = () => {
    console.log("WebSocket fermé.");
};
