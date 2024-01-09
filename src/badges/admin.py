from django.contrib import admin
from .models import Badge
from parler import admin as parler_admin
from parler.admin import TranslatableAdmin, TranslatableModelForm

from import_export.admin import ImportExportModelAdmin

# Register your models here.
@admin.register(Badge)
class BadgeAdmin(TranslatableAdmin):
    pass

