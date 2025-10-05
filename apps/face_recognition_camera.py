# # apps/face_recognition_camera.py
# import cv2
# import numpy as np
# import face_recognition
# from .models import Employee, FaceLog
# from django.core.files.base import ContentFile
# import os

# def load_embeddings():
#     embeddings = {}
#     for emp in Employee.objects.exclude(face_image=''):
#         if emp.face_image and os.path.exists(emp.face_image.path):
#             npy_path = emp.face_image.path.replace('.jpg', '.npy').replace('.png', '.npy')
#             if os.path.exists(npy_path):
#                 emb = np.load(npy_path)
#             else:
#                 image = face_recognition.load_image_file(emp.face_image.path)
#                 enc = face_recognition.face_encodings(image)
#                 if enc:
#                     emb = enc[0]
#                     np.save(npy_path, emb)
#                 else:
#                     continue
#             embeddings[emp.hemis_id] = (emp.full_name, emb)
#     return embeddings

# employee_embeddings = load_embeddings()

# def match_face(face_crop, embeddings_dict, tolerance=0.5):
#     encodings = face_recognition.face_encodings(face_crop)
#     if not encodings:
#         return None
#     face_vector = encodings[0]

#     for hemis_id, (full_name, emb) in embeddings_dict.items():
#         match = face_recognition.compare_faces([emb], face_vector, tolerance=tolerance)
#         if match[0]:
#             return hemis_id, full_name
#     return None

# def start_camera():
#     cap = cv2.VideoCapture(0)
#     print("Press 'q' to exit")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         rgb_frame = frame[:, :, ::-1]  # BGR -> RGB
#         face_locations = face_recognition.face_locations(rgb_frame)

#         for (top, right, bottom, left) in face_locations:
#             face_crop = rgb_frame[top:bottom, left:right]
#             match = match_face(face_crop, employee_embeddings)
#             if match:
#                 hemis_id, full_name = match
#                 try:
#                     emp = Employee.objects.get(hemis_id=hemis_id)
#                     FaceLog.objects.create(
#                         employee=emp,
#                         image=ContentFile(cv2.imencode('.jpg', frame[top:bottom, left:right])[1].tobytes()),
#                         status='IN'
#                     )
#                 except Exception as e:
#                     print(f"FaceLog save error: {e}")

#                 cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
#                 cv2.putText(frame, full_name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
#             else:
#                 cv2.rectangle(frame, (left, top), (right, bottom), (0,0,255), 2)
#                 cv2.putText(frame, "Unknown", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

#         cv2.imshow("Face Recognition", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     start_camera()
