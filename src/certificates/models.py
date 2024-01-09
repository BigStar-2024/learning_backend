from django.db import models
from app.models import RandomSlugModel, TimestampModel, IsActiveModel

class Certificates(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'notes_'
    image = models.URLField(null=True)
    pos_title = models.FloatField(null=True)
    pos_editable_text = models.FloatField(null=True)
    pos_student_name = models.FloatField(null=True)
    pos_text = models.FloatField(null=True)
    pos_name = models.FloatField(null=True)
    pos_from_who = models.FloatField(null=True)

class StudentCertificates(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'student_certificates'
    title = models.CharField(max_length=128, null=True, blank=True)
    editableText = models.TextField(null=True)
    text = models.TextField(null=True)
    certificate = models.ForeignKey(
        'certificates.Certificates', on_delete=models.CASCADE, null=True, blank=True)
    fromWho = models.ForeignKey(
        'organization.Teacher', on_delete=models.CASCADE, null=True, blank=True)
    toWho = models.ForeignKey(
        'students.Student', on_delete=models.CASCADE, null=True, blank=True)
