from django.contrib import admin
from .models import Avatar, StudentAvatar, FavoriteAvatarCollection, AvatarPurchaseTransaction
from .resources import AvatarResource
from import_export import admin as import_export_admin


@admin.register(Avatar)
class AvatarAdmin(import_export_admin.ImportExportModelAdmin):
    resource_class = AvatarResource
    list_display = ('id', 'name', 'type_of', 'price', 'image', 'is_active')
    search_fields = ('id', 'name')
    list_filter = ('type_of', 'price', 'is_active')


@admin.register(StudentAvatar)
class StudentAvatarAdmin(import_export_admin.ImportExportModelAdmin):
    resource_class = AvatarResource
    list_display = ('id', 'avatar', 'student', 'in_use')
    search_fields = ('id', 'avatar__name', 'student__full_name')
    list_filter = ('avatar__type_of', 'student__gender', 'in_use')


@admin.register(FavoriteAvatarCollection)
class FavoriteAvatarCollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'avatar_accessorie', 'avatar_head',
                    'avatar_clothes', 'avatar_pants', 'skin_tone')
    search_fields = ('id', 'student__full_name', 'avatar_accessorie__name', 'avatar_head__name',
                     'avatar_clothes__name', 'avatar_pants__name', 'skin_tone')
    list_filter = ('avatar_accessorie__type_of', 'skin_tone')


@admin.register(AvatarPurchaseTransaction)
class AvatarPurchaseTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'avatar')
    search_fields = ('id', 'avatar__name',)
    list_filter = ('avatar__type_of', 'avatar__price')
