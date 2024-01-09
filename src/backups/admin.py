
from django.contrib import admin
from django.conf.urls import url
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from django.core.management import call_command
from django.utils import timezone
from pathlib import Path
import io
from .models import DatabaseBackup
import threading
import os
from django.contrib import messages
from django.conf import settings

@admin.register(DatabaseBackup)
class DatabaseBackupAdmin(admin.ModelAdmin):
    list_display = ('id', 'backup_name', "description", 'backup_filename', 'backup_date', 'status', 'download_link', 'restore_link')
    search_fields = ('id', 'backup_name', 'backup_filename')
    readonly_fields = ('download_link','restore_link', 'backup_date',  'status')
    list_filter = ('backup_date',)
    actions = None      # Remove default delete action in the table

    def excute_dbbackup(self, backup_name):
        """
        Execute database backup django command for working in another thread.
        """
        call_command('dbbackup', '--output-filename', backup_name)
        current_backup = DatabaseBackup.objects.get(backup_filename = backup_name)
        current_backup.status = DatabaseBackup.STATUS_READY
        current_backup.save()
    
    def save_model(self, request, obj, form, change):
        """
        When create a backup model data in the db, make database backup file
        in other thread.
        """
        if not change and not obj.backup_filename:
            current_datetime = timezone.now().strftime('%Y%m%d_%H%M%S')
            if not obj.backup_name : obj.backup_name = f'db-backup_${current_datetime}'
            obj.backup_filename=f'db-backup_${current_datetime}.psql'
            if obj.description is None : obj.description = "Manual Backup"
            th = threading.Thread(target=self.excute_dbbackup, args=[obj.backup_filename])
            th.start()
            super().save_model(request, obj, form, change)
        else : 
            obj.status = DatabaseBackup.STATUS_READY
            super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        When delete a backup model data from the db, 
        check if db backup filed exists.
        If file exists, remove db backup file from local storage too.
        """
        filename = obj.backup_filename
        file_path = os.path.abspath(os.getcwd()) + f'\\backups\\database_backup\\{filename}'
        if os.path.isfile(file_path) :
            os.remove(file_path)
            print(" this file exists")
        else:
            print(" this file not exists")
        return super().delete_model(request, obj)

    def get_urls(self):
        """
        Add custome defined urls for download and restore a database backup file
        """
        urls = super(DatabaseBackupAdmin, self).get_urls()
        urls += [
            url(r'^download/(?P<pk>\d+)$', self.download_file,
                name='backups_databasebackup_download'),
            url(r'^restore/(?P<pk>\d+)$', self.restore_db,
                name='backups_databasebackup_restore'),
        ]
        return urls

    def download_link(self, obj):
        """
        Add the button to django admin list table to download db backup file.
        When a user press this button, visit .../download/pk url.
        """
        if obj.id is not None:
            return format_html(
                '<a class = "download" href="{}" style="visibility: {};">Download</a>',
                reverse('admin:backups_databasebackup_download', args=[obj.pk]) , 
                "hidden" if obj.status != DatabaseBackup.STATUS_READY else "unset"
            )
        return "-"
    download_link.short_description = "Backup download"

    def download_file(self, request, pk):
        """
        Download a db backupfile indentified by databaseBackup model pk.
        """
        database_backup = DatabaseBackup.objects.get(pk=pk)
        output_filename = database_backup.backup_filename
        backup_filepath = f'{Path(__file__).resolve().parent.parent}/backups/database_backup/{output_filename}'

        output_filesource = ''
        
        with io.open(backup_filepath, 'r', encoding='utf-8') as f:
            output_filesource = f.read()

        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename={output_filename}'
        response.write(output_filesource.encode("utf-8"))
        return response

    def restore_link(self, obj):
        """
        Add the button to django admin list table to restore a db backup file.
        When a user press this button, visit .../restore/pk url.
        """
        if obj.id is not None:
            return format_html(
                '<a class = "restore" href="{}" style="visibility: {};">Restore</a>',
                reverse('admin:backups_databasebackup_restore', args=[obj.pk]),
                "hidden" if obj.status != DatabaseBackup.STATUS_READY else "unset"
            )
        return "-"
    restore_link.short_description = "Restore DB"

    def restore_db(self, request, pk):
        """
        Restore a db backupfile indentified by databaseBackup model pk.
        """
        database_backup = DatabaseBackup.objects.get(pk=pk)
        input_filename = database_backup.backup_filename
        call_command('dbrestore', '--quiet', '--noinput', '--input-filename', input_filename)
        messages.success(request, 'Successfully Restore our DB')
        data = DatabaseBackup.objects.order_by("-backup_date").all()
        if len(data) > 0 : 
            data[0].status = DatabaseBackup.STATUS_READY
            data[0].save()
        response = HttpResponseRedirect("/admin/backups/databasebackup/")
        return response