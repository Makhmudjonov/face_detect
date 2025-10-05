import os
import cv2
import numpy as np
import pandas as pd
import torch
import requests
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ultralytics import YOLO
from .models import Employee

device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO("yolov8x-face-lindevs.pt")
model.to(device)

class EmployeeExcelUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Excel fayl orqali xodimlar ma’lumotlarini yuklash va embedding yaratish",
        manual_parameters=[
            openapi.Parameter(
                name='file',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="Excel fayl (.xlsx yoki .xls formatda)",
                required=True
            )
        ],
        responses={
            200: openapi.Response("Yuklash muvaffaqiyatli"),
            400: openapi.Response("Xatolik")
        }
    )
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "Excel fayl yuborilmadi"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({"error": f"Excel o‘qishda xatolik: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = ['hemis_id', 'full_name']
        for col in required_columns:
            if col not in df.columns:
                return Response({"error": f"{col} ustuni yo‘q"}, status=status.HTTP_400_BAD_REQUEST)

        created_count, updated_count = 0, 0

        for _, row in df.iterrows():
            hemis_id = str(row['hemis_id']).strip()
            if not hemis_id:
                continue

            defaults = {
                'full_name': row.get('full_name', ''),
                'department': row.get('department', ''),
                'position': row.get('position', ''),
                'is_kengash': bool(row.get('is_kengash', False))
            }

            obj, created = Employee.objects.update_or_create(
                hemis_id=hemis_id,
                defaults=defaults
            )

            # Excelda rasm URL bo‘lsa yuklash
            face_image_url = row.get('face_image', None)
            if pd.notna(face_image_url):
                try:
                    response = requests.get(face_image_url)
                    if response.status_code == 200:
                        filename = f"{hemis_id}.jpg"
                        obj.face_image.save(filename, ContentFile(response.content), save=True)
                except Exception as e:
                    print(f"{obj.full_name} rasm yuklashda xatolik: {e}")

            # Face detection + embedding
            if obj.face_image and os.path.exists(obj.face_image.path):
                try:
                    results = model.predict(
                        source=obj.face_image.path,
                        imgsz=320,
                        conf=0.5,
                        verbose=False
                    )

                    boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes is not None else []

                    if len(boxes) > 0:
                        x1, y1, x2, y2 = map(int, boxes[0])
                        img = cv2.imread(obj.face_image.path)
                        face_crop = img[y1:y2, x1:x2]

                        embedding = face_crop.flatten()
                        npy_path = obj.face_image.path.replace('.jpg', '.npy').replace('.png', '.npy')
                        np.save(npy_path, embedding)

                        obj.image_embedding = npy_path
                        obj.save()
                except Exception as e:
                    print(f"{obj.full_name} embedding yaratishda xatolik: {e}")

            if created:
                created_count += 1
            else:
                updated_count += 1

        return Response({
            "message": "Ma’lumotlar yuklandi, rasm saqlandi va embeddinglar yaratildi",
            "yaratilganlar": created_count,
            "yangilanganlar": updated_count,
            "jami": len(df)
        }, status=status.HTTP_200_OK)
