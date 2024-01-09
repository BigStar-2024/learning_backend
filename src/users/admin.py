from django.contrib import admin
from django.apps import apps
from django.contrib.auth.admin import UserAdmin
from api.admin import AdminProfileInline
from .models import User
from collectibles.models import CollectibleCategory
from collectibles.admin import CollectibleCategoryForm
from parler.admin import TranslatableAdmin
from mptt.admin import DraggableMPTTAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'username', 'email', 'is_staff', 'is_active', 'language')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'language')}),
        ('Permissions', {'fields': ('is_staff', 'is_active',
         'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    inlines = (AdminProfileInline,)


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)


models = apps.get_models()
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass


class HiddenAdminSite(admin.AdminSite):
    index_title = 'This is the hidden admin'


hidden_admin = HiddenAdminSite(name='hidden_admin')


class CollectibleCategoryHiddenProxyModel(CollectibleCategory):
    class Meta:
        proxy = True


@admin.action(description="Hard delete")
def hard_delete(modeladmin, request, queryset):
    for obj in queryset:
        obj.hard_delete()


class HiddenCollectibleCategoryAdmin(TranslatableAdmin, DraggableMPTTAdmin):
    form = CollectibleCategoryForm
    actions = [hard_delete]

    def get_queryset(self, *args, **kwargs):
        return CollectibleCategory.all_objects.all()

    def get_prepopulated_fields(self, request, obj=None):
        return {'name': ('description',)}


hidden_admin.register(CollectibleCategoryHiddenProxyModel,
                      HiddenCollectibleCategoryAdmin)
