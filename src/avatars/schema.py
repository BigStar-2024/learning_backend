import graphene
from graphene_django import DjangoObjectType
from avatars.models import Avatar, StudentAvatar, AvatarPurchaseTransaction, FavoriteAvatarCollection


class AvatarSchema(DjangoObjectType):
    class Meta:
        model = Avatar
        fields = "__all__"


class AvatarPurchaseTransactionSchema(DjangoObjectType):
    class Meta:
        model = AvatarPurchaseTransaction
        fields = "__all__"


class StudentAvatarSchema(DjangoObjectType):
    class Meta:
        model = StudentAvatar
        fields = "__all__"


class FavoriteAvatarCollectionSchema(DjangoObjectType):
    class Meta:
        model = FavoriteAvatarCollection
        fields = "__all__"


class Query(graphene.ObjectType):
    # ----------------- Avatar ----------------- #

    avatars = graphene.List(AvatarSchema)
    avatar_by_id = graphene.Field(AvatarSchema, id=graphene.ID())

    def resolve_avatars(root, info, **kwargs):
        # Querying a list
        return Avatar.objects.all()

    def resolve_avatar_by_id(root, info, id):
        # Querying a single question
        return Avatar.objects.get(pk=id)

    # ----------------- StudentTransactionAvatar ----------------- #

    students_transaction_avatar = graphene.List(
        AvatarPurchaseTransactionSchema)
    student_transaction_avatar_by_id = graphene.Field(
        AvatarPurchaseTransactionSchema, id=graphene.String())

    def resolve_students_transaction_avatar(root, info, **kwargs):
        # Querying a list
        return AvatarPurchaseTransaction.objects.all()

    def resolve_student_transaction_avatar_by_id(root, info, id):
        # Querying a single question
        return AvatarPurchaseTransaction.objects.get(pk=id)

    # ----------------- StudentAvatar ----------------- #

    students_avatar = graphene.List(
        StudentAvatarSchema)
    student_avatar_by_id = graphene.Field(
        StudentAvatarSchema, id=graphene.ID())

    avatars_by_student_id = graphene.List(
        StudentAvatarSchema, student_id=graphene.ID())

    def resolve_students_avatar(root, info, **kwargs):
        # Querying all avatars
        return StudentAvatar.objects.all()

    def resolve_student_avatar_by_id(root, info, id):
        # Querying a student avatar
        return StudentAvatar.objects.get(pk=id)

    def resolve_avatars_by_student_id(root, info, student_id):
        # Querying all student avatars
        return StudentAvatar.objects.filter(student=student_id)

    # ----------------- FavoriteAvatarCollection ----------------- #

    favorite_avatar_collections = graphene.List(
        FavoriteAvatarCollectionSchema)
    favorite_avatar_collection_by_id = graphene.Field(
        FavoriteAvatarCollectionSchema, id=graphene.String())

    def resolve_favorite_avatar_collections(root, info, **kwargs):
        # Querying a list
        return FavoriteAvatarCollection.objects.all()

    def resolve_favorite_avatar_collection_by_id(root, info, id):
        # Querying a single question
        return FavoriteAvatarCollection.objects.get(pk=id)
