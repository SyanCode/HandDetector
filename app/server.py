import asyncio
import websockets
import base64
import numpy as np
import cv2
import json
from hand_detector import detect_hand_distance_with_overlay

async def handler(websocket, path):
    async for message in websocket:
        print("Requête reçue par le serveur.")
        try:
            # Décoder l'image reçue en Base64
            base64_image = message.split(",", 1)[1]
            image_data = base64.b64decode(base64_image)
            np_array = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

            if image is None:
                await websocket.send('{"error": "Unable to decode image"}')
                continue

            print("Image décodée avec succès.")

            # Détecter la distance entre le pouce et l'index, et dessiner les annotations
            distance, annotated_image = detect_hand_distance_with_overlay(image)
            print("Distance détectée :", distance)

            # Convertir l'image annotée en Base64 pour l'envoyer au client
            _, buffer = cv2.imencode('.jpg', annotated_image)
            encoded_image = base64.b64encode(buffer).decode('utf-8')

            # Envoyer l'image annotée et la distance au client
            response = {
                "distance": distance,
                "image": encoded_image
            }
            await websocket.send(json.dumps(response))

        except Exception as e:
            error_message = str(e)
            print("Erreur lors du traitement :", error_message)
            await websocket.send(f'{{"error": "{error_message}"}}')

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Serveur WebSocket lancé sur ws://localhost:8765")
        await asyncio.Future()  # Maintenir le serveur actif

if __name__ == "__main__":
    asyncio.run(main())
