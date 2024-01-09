from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilter
from .models import Student, StudentTopicStatus, StudentTopicMastery, StudentAchievement, StudentGrade


class StudentFilter(AutocompleteFilter):
    title = 'Student'
    field_name = 'student'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'dob', 'gender')
    search_fields = ('id', 'user__username', 'first_name', 'last_name')
    list_filter = ('gender', 'student_plan', 'group', 'points', 'level',
                   'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(StudentTopicStatus)
class StudentTopicStatus(admin.ModelAdmin):
    list_display = ('id', 'student', 'topic', 'status')
    search_fields = ('id', 'topic__translations__name', 'student__user__username')
    list_filter = ('student__first_name', 'topic__area_of_knowledge__universal_area_knowledge',
                   'create_timestamp', 'update_timestamp')

@admin.register(StudentTopicMastery)
class StudentTopicMastery(admin.ModelAdmin):
    list_display = ('id', 'student', 'topic','topic_prerequsite_str', 'grade', 'mastery_level', 'status')
    search_fields = ('id', 'topic__translations__name', 'student__user__username',
                     'student__first_name', 'student__last_name', 'student__full_name')
    list_filter = ('topic__area_of_knowledge__universal_area_knowledge',
                   'mastery_level', 'create_timestamp', 'update_timestamp',)


@admin.register(StudentAchievement)
class StudentAchievementAdmin(admin.ModelAdmin):
    list_display = ('id', 'achivement', 'student', 'is_liberate', 'liberation_date')
    search_fields = ('id', 'student__user__username', 'achivement__translations__name')
    list_filter = ('achivement', 'is_liberate', 'liberation_date',
                   'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(StudentGrade)
class StudentGrade(admin.ModelAdmin):
    list_display = ('id', 'grade', 'student', 'is_finished', 'percentage', 'complete_date')
    search_fields = ('id', 'student__user__username', 'student__first_name', 'student__last_name',
                     'student__full_name', 'grade__translations__name')
    list_filter = ('grade', 'is_finished', 'percentage', 'complete_date',
                   'is_active', 'create_timestamp', 'update_timestamp')
