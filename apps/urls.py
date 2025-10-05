from django.urls import path
from .views import EmployeeExcelUploadView

urlpatterns = [
    path('api/employee/upload/', EmployeeExcelUploadView.as_view(), name='employee_excel_upload'),
]
