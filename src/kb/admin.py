from django.contrib import admin
from .models import Topic, AreaOfKnowledge, Grade, TopicGrade, Prerequisite, GradePrerequisite
from .models.content import Question, QuestionImageAsset, QuestionVideoAsset, QuestionAudioAsset, QuestionTTSAsset
from .models.content import (
    AnswerTTSAsset,
    AnswerOption,
    MultipleChoiceAnswerOption,
    MultipleSelectAnswerOption,
    OrderAnswerOption,
    RelateAnswerOption,
    TypeInAnswerOption,
)
from . import resources

from parler import admin as parler_admin
from import_export import admin as import_export_admin
from polymorphic import admin as polymorphic_admin
from mptt.admin import DraggableMPTTAdmin


class AnswerOptionInline(
    # parler_admin.TranslatableStackedInline,
    polymorphic_admin.StackedPolymorphicInline,
):
    model = AnswerOption

    class MultipleChoiceAnswerOptionInline(
            parler_admin.TranslatableStackedInline,
            polymorphic_admin.StackedPolymorphicInline.Child,
    ):
        model = MultipleChoiceAnswerOption

    class MultipleSelectAnswerOptionInline(
            parler_admin.TranslatableStackedInline,
            polymorphic_admin.StackedPolymorphicInline.Child,
    ):
        model = MultipleSelectAnswerOption

    class TypeInAnswerOptionInline(
            parler_admin.TranslatableStackedInline,
            polymorphic_admin.StackedPolymorphicInline.Child,
    ):
        model = TypeInAnswerOption

    class OrderAnswerOptionInline(
        parler_admin.TranslatableStackedInline,
        polymorphic_admin.StackedPolymorphicInline.Child,
    ):
        model = OrderAnswerOption

    class RelateAnswerOptionInline(
        parler_admin.TranslatableStackedInline,
        polymorphic_admin.StackedPolymorphicInline.Child,
    ):
        model = RelateAnswerOption

    child_inlines = (
        MultipleChoiceAnswerOptionInline,
        MultipleSelectAnswerOptionInline,
        TypeInAnswerOptionInline,
        OrderAnswerOptionInline,
        RelateAnswerOptionInline,
    )



class AnswerTTSAssetInline(admin.TabularInline):
    model = AnswerTTSAsset
    extra = 0

class QuestionImageAssetInline(admin.TabularInline):
    model = QuestionImageAsset
    extra = 0


class QuestionVideoAssetInline(admin.TabularInline):
    model = QuestionVideoAsset
    extra = 0


class QuestionAudioAssetInline(admin.TabularInline):
    model = QuestionAudioAsset
    extra = 0


class QuestionTTSAssetInline(admin.TabularInline):
    model = QuestionTTSAsset
    extra = 0


@admin.action(description='Hard delete objects')
def hard_delete_selected(modeladmin, request, queryset):
    for obj in queryset:
        obj.hard_delete()


@admin.register(Topic)
class TopicAdmin(parler_admin.TranslatableAdmin, import_export_admin.ImportExportModelAdmin, DraggableMPTTAdmin):
    resource_class = resources.TopicResource
    list_display = ('id', 'tree_actions', 'indented_title', 'area_of_knowledge', 'standard_topic',)
    search_fields = ('id', 'translations__name')
    list_filter = ('area_of_knowledge', 'topicgrade__grade' ,'is_active', 'create_timestamp', 'update_timestamp', )
    actions = [hard_delete_selected]



@admin.register(Prerequisite)
class PrerequisiteAdmin(
        import_export_admin.ImportExportModelAdmin,
):
    resource_class = resources.PrerequisiteResource
    list_display = ('id', 'topic', 'information')
    search_fields = ('id', 'topic__translations__name', 'prerequisites__translations__name',
                     'information', 'topic__area_of_knowledge')
    list_filter = ('topic__area_of_knowledge__universal_area_knowledge', 'topic__area_of_knowledge', 'topic__topicgrade__grade' ,)
    autocomplete_fields = ['topic', 'prerequisites']


@admin.register(GradePrerequisite)
class GradePrerequisiteAdmin(
        import_export_admin.ImportExportModelAdmin,
):
    resource_class = resources.GradePrerequisiteResource
    list_display = (
        'area_of_knowledge',
        'grade',
        'id',
    )
    search_fields = ('id', 'area_of_knowledge__translations__name', 'area_of_knowledge__audience__translations__name')
    list_filter = (
        'grade',
        'area_of_knowledge__universal_area_knowledge',
        'area_of_knowledge__audience',
    )
    autocomplete_fields = [
        'grade',
        'mastery',
        'competence'
    ]


@admin.register(AreaOfKnowledge)
class AreaOfKnowledgeAdmin(
        import_export_admin.ImportExportModelAdmin,
        parler_admin.TranslatableAdmin):
    resource_class = resources.AreaOfKnowledgeResource
    list_display = (
        'name',
        'id',
        'audience',
        'universal_area_knowledge',
        'is_active',
    )
    search_fields = ('id', 'translations__name', 'audience__translations__name')
    list_filter = (
        'is_active',
        'audience',
        'universal_area_knowledge',
    )


@admin.register(Grade)
class GradeAdmin(
        parler_admin.TranslatableAdmin,
        import_export_admin.ImportExportModelAdmin):
    resource_class = resources.GradeResource
    list_display = ('name', 'id', 'audience')
    search_fields = ('id', 'translations__name', 'slug', 'audience__translations__name')
    list_filter = ('translations__name', 'audience', 'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(TopicGrade)
class TopicGradeAdmin(
        import_export_admin.ImportExportModelAdmin):
    resource_class = resources.TopicGradeResource
    list_display = ('id', 'topic', 'grade', 'grade_audience', 'standard_code')
    search_fields = ('id', 'topic__translations__name', 'grade__translations__name', 'standard_code')
    list_filter = ('grade', 'grade__audience', 'is_active', 'topic__area_of_knowledge__translations__name',
    'topic__area_of_knowledge__universal_area_knowledge', 'create_timestamp', 'update_timestamp')
    autocomplete_fields = ['topic']


@admin.register(MultipleChoiceAnswerOption)
class MultipleChoiceAnswerOptionAdmin(
    parler_admin.TranslatableAdmin,
    import_export_admin.ImportExportModelAdmin,
    polymorphic_admin.PolymorphicChildModelAdmin,
):
    # Import-Export settings
    resource_class = resources.MultipleChoiceAnswerOptionResource

    #Inline
    inlines = [AnswerTTSAssetInline]

    # Polymorphic settings
    base_model = MultipleChoiceAnswerOption
    show_in_index = True

    autocomplete_fields = ['question']
    list_display = ('id', 'question', 'answer_text', 'explanation', 'is_correct')
    search_fields = ('id', 'question__translations__question_text', 'translations__answer_text',
                     'translations__explanation')
    list_filter = ('question__question_type', 'question__topic__area_of_knowledge',
                   'question__grade', 'is_correct', 'create_timestamp', 'update_timestamp')


@admin.register(MultipleSelectAnswerOption)
class MultipleSelectAnswerOptionAdmin(
    parler_admin.TranslatableAdmin,
    import_export_admin.ImportExportModelAdmin,
    polymorphic_admin.PolymorphicChildModelAdmin,
    polymorphic_admin.PolymorphicInlineSupportMixin,

):
    # Import-Export settings
    resource_class = resources.MultipleSelectAnswerOptionResource

    #Inline
    inlines = [AnswerTTSAssetInline]

    # Polymorphic settings
    base_model = MultipleSelectAnswerOption
    show_in_index = True

    autocomplete_fields = ['question']
    list_display = ('id', 'question', 'answer_text', 'explanation', 'is_correct')
    search_fields = ('id', 'question__translations__question_text', 'translations__answer_text',
                     'translations__explanation')
    list_filter = ('question__question_type', 'question__topic__area_of_knowledge',
                   'question__grade', 'is_correct', 'create_timestamp', 'update_timestamp')


@admin.register(TypeInAnswerOption)
class TypeInAnswerOptionAdmin(
    parler_admin.TranslatableAdmin,
    import_export_admin.ImportExportModelAdmin,
    polymorphic_admin.PolymorphicChildModelAdmin,
):
    # Import-Export settings
    resource_class = resources.TypeInAnswerOptionResource

    # Polymorphic settings
    base_model = TypeInAnswerOption
    show_in_index = True

    autocomplete_fields = ['question']
    list_display = ('id', 'question', 'answer_text', 'explanation', 'is_correct')
    search_fields = ('id', 'translations__answer_text', 'translations__explanation',
                     'question__translations__question_text')
    list_filter = ('question__question_type', 'question__topic__area_of_knowledge',
                   'question__grade', 'is_correct', 'create_timestamp', 'update_timestamp')

@admin.register(OrderAnswerOption)
class OrderAnswerOptionAdmin(
    parler_admin.TranslatableAdmin,
    import_export_admin.ImportExportModelAdmin,
    polymorphic_admin.PolymorphicChildModelAdmin,
):
    # Import-Export settings
    resource_class = resources.OrderAnswerOptionResource

    # Polymorphic settings
    base_model = OrderAnswerOption
    show_in_index = True

    autocomplete_fields = ['question']
    list_display = ('id', 'question', 'answer_text', 'order', 'is_correct')
    search_fields = ('id', 'question__translations__question_text', 'order')
    list_filter = ('question__question_type', 'question__topic__area_of_knowledge',
                   'question__grade', 'is_correct', 'create_timestamp', 'update_timestamp')


@admin.register(RelateAnswerOption)
class RelateAnswerOptionAdmin(
    parler_admin.TranslatableAdmin,
    import_export_admin.ImportExportModelAdmin,
    polymorphic_admin.PolymorphicChildModelAdmin,
):
    # Import-Export settings
    resource_class = resources.RelateAnswerOptionResource

    # Polymorphic settings
    base_model = RelateAnswerOption
    show_in_index = True

    autocomplete_fields = ['question']
    list_display = ('id', 'question', 'key', 'value', 'key_image', 'value_image', 'is_correct')
    search_fields = ('id', 'translations__key', 'translations__value', 'question__translations__question_text')
    list_filter = ('question__question_type', 'question__topic__area_of_knowledge',
                   'question__grade', 'is_correct', 'create_timestamp', 'update_timestamp')


@admin.register(AnswerOption)
class AnswerOptionAdmin(import_export_admin.ImportExportModelAdmin, polymorphic_admin.PolymorphicParentModelAdmin):
    list_display = ('id', '__str__', 'question', 'question_type')
    # list_display = ('id', 'key', 'value', 'is_correct', 'question')
    search_fields = ('key', 'value', 'question',)
    list_filter = ('question_type', 'is_correct', 'topic__area_of_knowledge', 'grade', 'grade_audience')

    # Import-Export settings
    resource_class = resources.AnswerOptionResource
    
    #Inline
    inlines = [AnswerTTSAssetInline]
    
    # Polymorphic settings
    polymorphic_list = True
    base_model = AnswerOption
    child_models = (
        MultipleChoiceAnswerOption,
        MultipleSelectAnswerOption,
        TypeInAnswerOption,
        OrderAnswerOption,
        RelateAnswerOption,
    )
    list_filter = (
        'question__topic__area_of_knowledge',
        'question__question_type',
    )
    autocomplete_fields = ['question']
    search_fields = ('id',)


@admin.register(Question)
class QuestionAdmin(
    polymorphic_admin.PolymorphicInlineSupportMixin,
    parler_admin.TranslatableAdmin,
    import_export_admin.ImportExportModelAdmin,
):
    resource_class = resources.QuestionResource
    inlines = [
        AnswerOptionInline,
        QuestionImageAssetInline,
        QuestionVideoAssetInline,
        QuestionTTSAssetInline,
        QuestionAudioAssetInline
    ]
    fields = ('question_text', 'topic', 'grade', 'question_type')
    list_display = ('id', 'question', 'question_type', 'topic', 'grade', 'grade_audience')
    search_fields = ('id', 'translations__question_text')
    list_filter = ('question_type', 'topic__area_of_knowledge', 'grade', 'grade__audience')
    autocomplete_fields = ['topic']


@admin.register(QuestionImageAsset)
class QuestionImageAssetAdmin(import_export_admin.ImportExportModelAdmin):
    resource_class = resources.QuestionImageAssetResource
    list_display = ('id', 'question', 'image')
    search_fields = ('id', 'image', 'order', )
    list_filter = ('question__grade', 'question__topic__area_of_knowledge', 'question__topic__area_of_knowledge__universal_area_knowledge', 'question__question_type')
    autocomplete_fields = ['question']


@admin.register(QuestionAudioAsset)
class QuestionAudioAssetAdmin(import_export_admin.ImportExportModelAdmin):
    resource_class = resources.QuestionAudioAssetResource
    list_display = ('id', 'question', 'audio_file')
    search_fields = ('id', 'audio_file', 'order')
    list_filter = ('question__grade', 'question__topic__area_of_knowledge', 'question__topic__area_of_knowledge__universal_area_knowledge', 'question__question_type')
    autocomplete_fields = ['question']


@admin.register(QuestionTTSAsset)
class QuestionTTSAssetAdmin(import_export_admin.ImportExportModelAdmin):
    list_display = ('id', 'question', 'tts_file')
    search_fields = ('id', 'tts_file', 'order', 'random_slug')
    list_filter = ('question__grade', 'question__topic__area_of_knowledge', 'question__topic__area_of_knowledge__universal_area_knowledge', 'question__question_type')


@admin.register(QuestionVideoAsset)
class QuestionVideoAssetAdmin(import_export_admin.ImportExportModelAdmin):
    list_display = ('id', 'question', 'url')
    search_fields = ('id', 'url', 'order', 'random_slug')
    list_filter = ('question__grade', 'question__topic__area_of_knowledge', 'question__topic__area_of_knowledge__universal_area_knowledge', 'question__question_type')
