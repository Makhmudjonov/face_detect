from ultralytics import YOLO
import cv2
import torch
import time

# Modelni yuklaymiz
model = YOLO("yolov8x-face-lindevs.pt")  # o'zingdagi model nomi
device = "cuda" if torch.cuda.is_available() else "cpu"

# Kamera
cap = cv2.VideoCapture(0)

prev_time = 0
face_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Model yordamida aniqlash
    results = model.predict(
        source=frame,
        device=device,
        imgsz=320,
        conf=0.5,
        stream=False,
        verbose=False
    )

    # Yuzlarni chizish va nom chiqarish
    boxes = results[0].boxes.xyxy.cpu().numpy()
    for (x1, y1, x2, y2) in boxes:
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        
        # Fayl nomini hosil qilamiz (lekin saqlamaymiz)
        timestamp = int(time.time() * 1000)
        filename = f"face_{timestamp}_{face_count}.jpg"
        face_count += 1

        # Yuzni chizish
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, filename, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,255,0), 1)

    # FPS hisoblash
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if prev_time else 0
    prev_time = current_time
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

    # Kamera oynasini ko'rsatish
    cv2.imshow("YOLOv8 Face Detection (No Save)", frame)

    # ESC bosilsa chiqish
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
