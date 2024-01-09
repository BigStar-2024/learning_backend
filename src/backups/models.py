from django.conf import settings
from django.db import models
from django.http.response import HttpResponse
from django.utils.html import mark_safe
from pathlib import Path
import mimetypes
import os

class DatabaseBackup(models.Model):
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_READY = 'READY'

    STATUS_CHOICES = (
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_READY, 'Ready'),

    )
    id = models.AutoField(primary_key=True)
    backup_name = models.CharField(max_length=64, null = True, blank = True,)
    backup_filename = models.CharField(max_length=255, null = True, blank = True,)
    backup_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, null = True, blank = True,)
    status = models.CharField(
        max_length=128,
        choices=STATUS_CHOICES,
        default=STATUS_PROCESSING
    )

    def __str__(self):
        return self.backup_name

    @property
    def filename(self):
        return os.path.basename(self.backup_name)
        