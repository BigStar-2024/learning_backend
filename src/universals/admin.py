from django.contrib import admin
from .models.topics import UniversalTopic
from .models.areas_of_knowledge import UniversalAreaOfKnowledge


@admin.register(UniversalTopic)
class UniversalTopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'area_of_knowledge', 'parent', 'standard_code')
    search_fields = ('id', 'name', 'standard_code')
    list_filter = ('area_of_knowledge', 'slug', 'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(UniversalAreaOfKnowledge)
class UniversalAreaOfKnowledgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('id', 'name', 'slug')
    list_filter = ('slug', 'is_active', 'create_timestamp', 'update_timestamp')
