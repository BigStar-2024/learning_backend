from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableModelForm
from mptt.admin import DraggableMPTTAdmin
from mptt.forms import MPTTAdminForm
from .models import CollectibleCategory, Collectible, CollectiblePurchaseTransaction, StudentCollectible, \
    CollectiblePackPurchaseTransaction
from .models import Description, CollectibleDescription
from import_export import admin as import_export_admin
from .resources import CollectibleResource, DescriptionResource, CollectibleDescriptionResource


@admin.action(description='Hard delete objects')
def hard_delete_selected(modeladmin, request, queryset):
    for obj in queryset:
        obj.hard_delete()


class CollectibleCategoryForm(MPTTAdminForm, TranslatableModelForm):
    pass


@admin.register(CollectibleCategory)
class CollectibleCategoryAdmin(TranslatableAdmin, DraggableMPTTAdmin):
    form = CollectibleCategoryForm
    list_display = ('indented_title', 'description', 'parent', 'front_image', 'back_image', 'price', 'firebase_name')
    search_fields = ('id', 'translations__name', 'translations__description',
                     'front_image', 'back_image', 'firebase_name', 'random_slug')
    list_filter = ('price', 'is_active', 'create_timestamp', 'update_timestamp')

    def get_prepopulated_fields(self, request, obj=None):
        return {'name': ('description',)}


@admin.register(Collectible)
class CollectibleAdmin(TranslatableAdmin, import_export_admin.ImportExportModelAdmin):
    resource_class = CollectibleResource
    list_display = ('id', 'name', 'image', 'category', 'tier')
    search_fields = ('id', 'translations__name', 'description__translations__key', 'description__translations__value')
    list_filter = ('category', 'tier', 'is_active', 'create_timestamp', 'update_timestamp')


@admin.register(Description)
class DescriptionAdmin(TranslatableAdmin, import_export_admin.ImportExportModelAdmin):
    resource_class = DescriptionResource
    list_display = ('id', 'key', 'value')
    search_fields = ('id', 'translations__key', 'translations__value')


@admin.register(CollectibleDescription)
class CollectibleDescriptionAdmin(import_export_admin.ImportExportModelAdmin):
    resource_class = CollectibleDescriptionResource
    list_display = ('id', 'collectible', 'description')
    search_fields = ('id', 'collectible__translations__name', 'description__translations__key',
                     'description__translations__value')
    list_filter = ('collectible__category', 'collectible__tier')


@admin.register(CollectiblePurchaseTransaction)
class CollectiblePurchaseTransactionAdmin(admin.ModelAdmin):
    exclude = ('amount',)
    list_display = ('id', 'collectible')
    search_fields = ('id', 'collectible__translations__name')
    list_filter = ('side', 'collectible__category', 'collectible__tier', 'collectible__is_active', 'date')


@admin.register(StudentCollectible)
class StudentCollectibleAdmin(admin.ModelAdmin):
    list_display = ('id', 'collectible', 'student', 'amount', 'is_active')
    search_fields = ('id', 'collectible__translations__name', 'collectible__description__translations__key',
                     'collectible__description__translations__value', 'student__first_name',
                     'student__last_name', 'student__full_name', 'amount')
    list_filter = ('collectible__category', 'collectible__tier', 'amount', 'is_active',)
    actions = [hard_delete_selected]


@admin.register(CollectiblePackPurchaseTransaction)
class CollectiblePackPurchaseTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'collectible_category')
    search_fields = ('id', 'collectibles__translations__name', 'collectible_category__translations__name',
                     'collectible_category__translations__name')
    list_filter = ('collectible_category__translations__name', 'collectibles__category', 'collectibles__tier')
