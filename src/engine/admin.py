from django.contrib import admin
from .models import AreaOfKnowledgeStudentReport, TopicMasterySettings, TopicStudentReport
from admin_auto_filters.filters import AutocompleteFilter


class TopicFilter(AutocompleteFilter):
    title = 'Topic'
    field_name = 'topic'


@admin.register(AreaOfKnowledgeStudentReport)
class AreaOfKnowledgeStudentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'area_of_knowledge', 'student', 'questions_answered', 'correct_question', 'accuracy')
    search_fields = ('id', 'student__first_name', 'student__last_name',
                     'student__full_name', 'questions_answered', 'correct_question')
    list_filter = ('area_of_knowledge__translations__name', 'questions_answered', 'correct_question', 'accuracy',)


@admin.register(TopicMasterySettings)
class TopicMasterySettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'sample_size', 'mastery_percentage', 'competence_percentage')
    search_fields = ('id', 'sample_size', 'mastery_percentage', 'competence_percentage')
    list_filter = ('topic__area_of_knowledge__universal_area_knowledge__name',)


@admin.register(TopicStudentReport)
class TopicStudentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'student', 'questions_answered', 'correct_question', 'accuracy')
    search_fields = ('id', 'topic__translations__name', 'student__first_name', 'student__last_name',
                     'student__full_name', 'questions_answered', 'correct_question', 'accuracy')
    list_filter = ('topic__area_of_knowledge__universal_area_knowledge__name',
                   'questions_answered', 'correct_question', 'accuracy',)

