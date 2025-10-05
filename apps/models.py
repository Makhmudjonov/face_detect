from django.db import models
from django.contrib.auth.models import User

class FaceLog(models.Model):
    employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name='logs', null=True,)
    image = models.ImageField(upload_to='faces/')
    detected_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=(
        ('IN', 'Kirdi'),
        ('OUT', 'Chiqdi')
    ))

    def __str__(self):
        return f"{self.employee.full_name} - {self.status} - {self.detected_at.strftime('%Y-%m-%d %H:%M:%S')}"


# apps/models.py
class Employee(models.Model):
    hemis_id = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=150)
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    face_image = models.ImageField(upload_to='employee_faces/', blank=True, null=True)
    is_kengash = models.BooleanField(default=False)
    image_embedding = models.CharField(max_length=255, blank=True, null=True)  # <-- qo‘shildi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.hemis_id})"

