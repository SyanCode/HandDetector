import websockets
import asyncio
import json
from hand_detector import detect_hand_distance_with_overlay
import base64
import numpy as np
import cv2

async def handle_connection(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            if "image" in data:
                # Décoder l'image reçue en Base64
                base64_image = data["image"].split(",", 1)[1]
                image_data = base64.b64decode(base64_image)
                np_array = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                if image is None:
                    await websocket.send('{"error": "Unable to decode image"}')
                    continue

                # Détecter la distance entre le pouce et l'index, et dessiner les annotations
                distance, annotated_image = detect_hand_distance_with_overlay(image)

                # Convertir l'image annotée en Base64 pour l'envoyer au client
                _, buffer = cv2.imencode('.jpg', annotated_image)
                encoded_image = base64.b64encode(buffer).decode('utf-8')

                # Envoyer l'image annotée et la distance au client
                response = {
                    "distance": distance,
                    "image": encoded_image
                }
                await websocket.send(json.dumps(response))
    except websockets.ConnectionClosed:
        print("Connexion fermée")
    except Exception as e:
        print(f"Erreur lors du traitement: {e}")

start_server = websockets.serve(handle_connection, "0.0.0.0", 8000)

loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()
