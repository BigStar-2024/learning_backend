import random
from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import(
    BlockType,
    BlockAssignment,
    Block,
    BlockQuestionPresentation,
    StudentBlockQuestionPresentationHistory,
    BlockConfiguration,
    BlockConfigurationKeyword,
    BlockTypeConfiguration,
    BlockPresentation,
    BlockTransaction
)
from kb.models.content import Question
from parler import admin as parler_admin
from django.forms import ModelForm


# Register your models here.
@admin.register(BlockType)
class BlockTypeAdmin(parler_admin.TranslatableAdmin):
    list_display = ('id', 'name', 'is_active')
    search_fields = ('translations__name',)
    list_filter = ('is_active', 'create_timestamp', 'update_timestamp')


@admin.register(BlockAssignment)
class BlockAssignmentAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'student', 'block_identifier', 'block_topic_grade', 'block_modality', 'order')
    search_fields = ('id', 'student__full_name', 'order')
    list_filter = ('student__gender', 'block__modality', 'block__topic_grade')

    @admin.display(description='Block identifier')
    def block_identifier(self, obj):
        return ("%s" % (obj.block.random_slug))

    @admin.display(description='Block topic grade')
    def block_topic_grade(self, obj):
        return ("%s" % (obj.block.topic_grade))

    @admin.display(description='Block modality')
    def block_modality(self, obj):
        return ("%s" % (obj.block.modality))

    @admin.display(description='Order')
    def order_number(self, obj):
        return ("%s" % (obj.order))


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_of', 'topic_grade', 'modality', 'block_size', 'random_slug')
    search_fields = ('id', 'random_slug')
    list_filter = ('modality', 'type_of', 'topic_grade', 'block_size', 'random_slug')
    autocomplete_fields = ['questions', 'topic_grade']

    def save_related(self, request, form, formsets, change):
        super(BlockAdmin, self).save_related(request, form, formsets, change)

        if form.instance.questions.name is None:
            available_questions = list(
                Question.objects.filter(
                    topic=form.instance.topic_grade.topic).filter(
                    grade=form.instance.topic_grade.grade))
            if len(available_questions) < form.instance.block_size:
                for question in available_questions:
                    form.instance.questions.add(question)
            else:
                random_questions = random.sample(
                    available_questions, form.instance.block_size)
                for question in random_questions:
                    form.instance.questions.add(question)

        for student in form.instance.students.all():
            BlockAssignment.objects.get_or_create(
                block=form.instance, student=student)

class BlockQuestionPresentationAdminForm(ModelForm):
    #    email_users = forms.ModelMultipleChoiceField(queryset=User.objects.order_by('username'))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # test = self.instance.chosen_answer.order_by(self.instance.chosen_answer.through._meta.db_table+'.id').all()
        # self.initial['chosen_answer'] = (test[0], test[1], test[2])

@admin.register(BlockQuestionPresentation)
class BlockQuestionPresentationAdmin(admin.ModelAdmin):
    list_display = ('id', 'block_presentation', 'question', 'typed_answer', 'topic', 'status')
    search_fields = ('id', 'typed_answer')
    list_filter = ('question__question_type', 'question__grade', 'topic__area_of_knowledge',
                   'status', 'chosen_answer__is_correct', 'create_timestamp', 'update_timestamp')
    autocomplete_fields = ['question', 'topic', 'chosen_answer']
    form = BlockQuestionPresentationAdminForm



@admin.register(BlockConfiguration)
class BlockConfigurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'block', 'key', 'value', 'create_timestamp', 'update_timestamp')
    search_fields = ('key__name', 'value')
    list_filter = ('block__type_of', 'block__topic_grade', 'block__modality', 'create_timestamp', 'update_timestamp')


@admin.register(BlockConfigurationKeyword)
class BlockConfigurationKeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'create_timestamp', 'update_timestamp')
    search_fields = ('name',)
    list_filter = ('is_active', 'create_timestamp', 'update_timestamp')


@admin.register(BlockTypeConfiguration)
class BlockTypeConfigurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'block_type', 'key', 'value', 'is_active')
    search_fields = ('block_type__translations__name', 'key__name', 'value')
    list_filter = ('is_active', 'create_timestamp', 'update_timestamp')


@admin.register(BlockPresentation)
class BlockPresentationAdmin(admin.ModelAdmin):
    list_display = ('id', 'block', 'student', 'hits', 'errors', 'total', 'points', 'bonusCoins',
                    'coins', 'start_timestamp', 'end_timestamp', 'is_active')
    search_fields = ('id', 'student__full_name')
    list_filter = ('block__type_of', 'block__topic_grade', 'is_active', 'start_timestamp', 'end_timestamp')


@admin.register(StudentBlockQuestionPresentationHistory)
class StudentBlockQuestionPresentationHistory(admin.ModelAdmin):
    list_display = ('id', 'student')
    search_fields = ('id', 'student__first_name', 'student__last_name', 'student__full_name',
                     'block_question_presentation__topic__translations__name',
                     'block_question_presentation__topic__standard_topic')
    list_filter = ('block_question_presentation__topic__area_of_knowledge', 'block_question_presentation__status',
                   'create_timestamp', 'update_timestamp')


@admin.register(BlockTransaction)
class BlockTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'blockPresentation')
    search_fields = ('id',)
    list_filter = ('blockPresentation__block__type_of', 'blockPresentation__block__topic_grade',
                   'blockPresentation__block__modality', 'blockPresentation__start_timestamp',
                   'blockPresentation__end_timestamp')
