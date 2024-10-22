import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def detect_hand_distance_with_overlay(image):
    with mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5) as hands:
        # Convertir l'image en RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if results.multi_hand_landmarks:
            annotated_image = image.copy()
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Calculer la distance entre le pouce et l'index
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                thumb_coords = (int(thumb_tip.x * image.shape[1]), int(thumb_tip.y * image.shape[0]))
                index_coords = (int(index_tip.x * image.shape[1]), int(index_tip.y * image.shape[0]))

                # Dessiner une ligne entre le pouce et l'index
                cv2.line(annotated_image, thumb_coords, index_coords, (0, 255, 0), 2)

                # Calculer la distance en pixels
                distance = int(((thumb_coords[0] - index_coords[0]) ** 2 + (thumb_coords[1] - index_coords[1]) ** 2) ** 0.5)
                return distance, annotated_image

        return 0, image  # Aucun main détectée, renvoyer l'image d'origine
