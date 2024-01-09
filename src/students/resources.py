from import_export.resources import ModelResource
from .models import Student


class StudentAdminResource(ModelResource):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name']