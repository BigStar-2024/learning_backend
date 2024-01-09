from django.contrib import admin

from students.models import Student
from .models.org import Organization, OrganizationPersonnel
from .models.schools import Group, School, SchoolAdministrativePersonnel, SchoolPersonnel, AdministrativePersonnel, SchoolTeacher, SchoolSubscriber, Subscriber, Teacher, Classroom, TeacherClassroom
# from widgets import ImproveRawIdFieldsForm
class SchoolTeacherInline(admin.StackedInline):
    model = SchoolTeacher
    extra = 0

class AssignSchoolToTeacherInline(admin.StackedInline):
    model = SchoolTeacher
    extra = 0
    verbose_name = "Assign School With Plan"
    verbose_name_plural = "Assign Schools With Plan"

class AssingClassroomToTeacherInline(admin.StackedInline):
    model = TeacherClassroom
    extra = 0
    verbose_name = "Assign Clasroom With Plan"
    verbose_name_plural = "Assign Clasrooms With Plan"

class AssignTeacherToClassroomInline(admin.StackedInline):
    model = TeacherClassroom
    extra = 0
    verbose_name = "Assign Teacher With Plan"
    verbose_name_plural = "Assign Teacher With Plan"

class AssingStudentsToClassroomInline(admin.StackedInline):
    model = Student
    raw_id_fields=('classroom',)
    extra = 0
    verbose_name = "Assign Students To Classroom"
    verbose_name_plural = "Assign Student To Classroom"


class SchoolSubscriberInline(admin.StackedInline):
    model = SchoolSubscriber
    extra = 0

class SchoolAdministrativePersonnelInline(admin.StackedInline):
    model = SchoolAdministrativePersonnel
    extra = 0

class StudentInline(admin.StackedInline):
    model = Student

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type_of', 'slug', 'parent')
    search_fields = ('id', 'name', 'slug')
    list_filter = ('type_of', 'slug', 'student_plan', 'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(OrganizationPersonnel)
class OrganizationPersonnelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'organization', 'name', 'last_name',
                    'gender', 'date_of_birth', 'identification_number', 'position')
    search_fields = ('id', 'user__username', 'organization__name', 'name', 'last_name', 'identification_number')
    list_filter = ('organization', 'position', 'gender', 'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'classroom')
    search_fields = ('id', 'name', 'classroom__name' )
    list_filter = ('is_active', 'create_timestamp', 'update_timestamp')

@admin.register(SchoolAdministrativePersonnel)
class SchoolAdministrativePersonnelAdmin(admin.ModelAdmin):
    list_display = ('id', 'school', 'administrative_personnel', 'is_paid', 'is_cancel', 'plan', 'order_detail', 'expired_at', 'period', 'price')
    search_fields = ('id', 'school__name', 'administrative_personnel__user__username', 'plan__id', 'order_detail__id', 'expired_at', 'period', 'price' )
    list_filter = ('period', 'expired_at', 'is_active', 'create_timestamp', 'update_timestamp')

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type_of',)
    search_fields = ('id', 'name',)
    list_filter = ('type_of', 'is_active', 'create_timestamp', 'update_timestamp')
    inlines = [
        SchoolTeacherInline,
        SchoolSubscriberInline,
        SchoolAdministrativePersonnelInline,
    ]

@admin.register(SchoolTeacher)
class SchoolTeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'school', 'teacher')
    search_fields = ('id', 'school', 'teacher')
    list_filter = ('is_active', 'create_timestamp', 'update_timestamp')

@admin.register(SchoolPersonnel)
class SchoolPersonnelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'has_order', 'zip', 'country')
    search_fields = ('id', 'user__username', 'last_name', 'first_name', 'zip', 'country'
                     )
    list_filter = ('gender', 'has_order', 'country', 'create_timestamp', 'update_timestamp', 'is_active')


@admin.register(AdministrativePersonnel)
class AdministrativePersonnelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name',
                    'country')
    search_fields = ('id', 'user__username', 'last_name', 'first_name'
                    )
    list_filter = ('is_active', 'create_timestamp', 'update_timestamp')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'last_name',
                    'gender', 
                    )
    search_fields = ('id', 'user__username', 'name', 'last_name',
                     'position', )
    list_filter = ('gender', 
                   'is_active', 'create_timestamp', 'update_timestamp')
    inlines = [
        AssignSchoolToTeacherInline,
        AssingClassroomToTeacherInline,
    ]

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'language', 'audience', 'enable_games', 'game_cost_percentage', 'time_zone_value',
                    'monday_start', 'monday_end', 'tuesday_start', 'tuesday_end', 'wednesday_start', 'wednesday_end',
                    'thursday_start', 'thursday_end', 'friday_start', 'friday_end', 'saturday_start', 'saturday_end',
                    'sunday_start', 'sunday_end')
    search_fields = ('id', 'name', 'audience__translations__name',
                     'school__name', 'teacher__name', 'teacher__last_name', 'time_zone_value')
    list_filter = ('grade', 'language', 'audience', 'game_cost_percentage',
                   'time_zone_value', 'is_active', 'create_timestamp', 'update_timestamp', 'time_zone_value', 'enable_games')
    inlines = [
        AssignTeacherToClassroomInline,
        AssingStudentsToClassroomInline
    ]

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'has_order', 'zip', 'country')
    search_fields = ('id', 'user__username', 'last_name', 'first_name', 'zip', 'country'
                     )
    list_filter = ('gender', 'has_order', 'country', 'create_timestamp', 'update_timestamp', 'is_active')

@admin.register(SchoolSubscriber)
class SchoolubSubscriberAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'school')
    search_fields = ('id', 'subscriber__user__username', 'school__name')
    list_filter = ('create_timestamp', 'update_timestamp', 'is_active')
