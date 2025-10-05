# apps/admin.py
from django.contrib import admin
from .models import Employee, FaceLog
import numpy as np

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('hemis_id', 'full_name', 'department', 'position', 'is_kengash', 'show_embedding')
    readonly_fields = ('image_embedding',)

    def show_embedding(self, obj):
        """Embeddingni qisqacha ko‘rsatish"""
        if obj.image_embedding and obj.image_embedding.endswith('.npy'):
            try:
                data = np.load(obj.image_embedding)
                # faqat 10 birinchi elementni ko‘rsatish
                snippet = ", ".join([str(round(x, 2)) for x in data[:10]])
                return f"[{snippet}, ...] ({data.shape})"
            except Exception as e:
                return f"Xatolik: {e}"
        return "Yo‘q"

    show_embedding.short_description = "Embedding"

@admin.register(FaceLog)
class FaceLogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'status', 'detected_at')
