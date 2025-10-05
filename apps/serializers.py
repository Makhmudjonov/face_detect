from rest_framework import serializers
from .models import Employee, FaceLog


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class FaceLogSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = FaceLog
        fields = '__all__'
