import graphene
from .schema import AvatarSchema, AvatarPurchaseTransactionSchema, StudentAvatarSchema, FavoriteAvatarCollectionSchema
from .models import Avatar, StudentAvatar, AvatarPurchaseTransaction, FavoriteAvatarCollection
from students.models import Student
from students.schema import StudentSchema
from wallets.models import CoinWallet
from graphql import GraphQLError


class PurchaseAvatar(graphene.Mutation):
    """ Purchase a single avatar """
    avatar_purchase_transaction = graphene.Field(
        AvatarPurchaseTransactionSchema)
    student = graphene.Field(StudentSchema)
    avatar = graphene.Field(AvatarSchema)

    class Arguments:
        student = graphene.ID(required=True)
        avatar = graphene.ID(required=True)

    def mutate(self, info, student, avatar):
        student = Student.objects.get(id=student)
        avatar = Avatar.objects.get(id=avatar)
        student_avatar = StudentAvatar.objects.filter(
            student=student, avatar=avatar)
        if not student_avatar:
            account, new = CoinWallet.objects.get_or_create(student=student)
            if avatar.price > account.balance:
                raise Exception('Your coin is not enough')

            avatar_purchase_transaction = AvatarPurchaseTransaction(
                avatar=avatar,
                account=account,
            )
            avatar_purchase_transaction.save()

            return PurchaseAvatar(
                avatar_purchase_transaction=avatar_purchase_transaction,
                student=student,
                avatar=avatar,
            )
        raise GraphQLError('Avatar already purchased')


class SetCurrentAvatar(graphene.Mutation):
    """ set student_avatars current avatar """
    student_avatar = graphene.Field(StudentAvatarSchema)

    class Arguments:
        student_id = graphene.ID(required=True)
        avatar_id = graphene.ID(required=True)

    def mutate(self, info, student_id, avatar_id):
        student_avatar = StudentAvatar.objects.get(
            student=student_id, avatar=avatar_id)
        avatar_type = student_avatar.avatar.type_of
        StudentAvatar.objects.filter(
            student=student_id,
            avatar__type_of=avatar_type,
            in_use=True).update(
            in_use=False)
        student_avatar.in_use = True
        student_avatar.save()

        return SetCurrentAvatar(
            student_avatar=student_avatar
        )


class SetCurrentFavoriteAvatarCollection(graphene.Mutation):
    favorite_avatar_collection = graphene.Field(
        FavoriteAvatarCollectionSchema
    )
    student = graphene.Field(StudentSchema)

    class Arguments:
        student_id = graphene.ID()
        favorite_avatar_collection_id = graphene.ID(required=True)

    def mutate(self, info, favorite_avatar_collection_id, student_id=None):
        if student_id:
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                raise Exception("Student does not exist")
        else:
            user = info.context.user
            if user.is_anonymous:
                raise Exception("User is anonymous")
            elif user.student:
                student = user.student
            else:
                raise Exception("User has no student")

        try:
            favorite_avatar_collection = FavoriteAvatarCollection.objects.get(
                id=favorite_avatar_collection_id)
        except FavoriteAvatarCollection.DoesNotExist:
            raise Exception("FavoriteAvatarCollection does not exist")

        StudentAvatar.objects.filter(
            student=student_id,
            in_use=True,
        ).update(in_use=False)

        favorite_avatar_collection.set_in_use()

        return SetCurrentFavoriteAvatarCollection(
            favorite_avatar_collection=favorite_avatar_collection,
            student=student
        )


class SetFavoriteAvatarCollection(graphene.Mutation):
    favorite_avatar_collection = graphene.Field(
        FavoriteAvatarCollectionSchema
    )

    class Arguments:
        student_id = graphene.ID(required=True)
        avatar_accessorie = graphene.ID()
        avatar_head = graphene.ID(required=True)
        avatar_clothes = graphene.ID(required=True)
        avatar_pants = graphene.ID(required=True)
        skin_tone = graphene.ID()

    def mutate(
            self,
            info,
            student_id,
            avatar_head,
            avatar_clothes,
            avatar_pants,
            avatar_accessorie=None,
            skin_tone=None):
        current_favorites = FavoriteAvatarCollection.objects.filter(
            student=student_id
        ).order_by('create_timestamp')
        if current_favorites.count() >= 4:
            current_favorites.first().delete()
        student = Student.objects.get(pk=student_id)
        avatar_head = Avatar.objects.get(pk=avatar_head)
        avatar_clothes = Avatar.objects.get(pk=avatar_clothes)
        avatar_pants = Avatar.objects.get(pk=avatar_pants)
        if avatar_accessorie:
            avatar_accessorie = Avatar.objects.get(pk=avatar_accessorie)
        new_favorite = FavoriteAvatarCollection.objects.create(
            student=student,
            avatar_accessorie=avatar_accessorie,
            avatar_head=avatar_head,
            avatar_clothes=avatar_clothes,
            avatar_pants=avatar_pants,
            skin_tone=skin_tone
        )
        return SetFavoriteAvatarCollection(
            favorite_avatar_collection=new_favorite)


class SetAvatarSkinTone(graphene.Mutation):
    favorite_avatar_collection = graphene.Field(
        FavoriteAvatarCollectionSchema
    )

    class Arguments:
        skin_tone = graphene.String(required=True)
        favorite_avatar_collection_id = graphene.ID(required=True)

    def mutate(self, info, skin_tone, favorite_avatar_collection):
        avatar_collection = FavoriteAvatarCollection.objects.get(
            id=favorite_avatar_collection
        )
        avatar_collection.skin_tone = skin_tone
        avatar_collection.save()
        return avatar_collection


class Mutation(graphene.ObjectType):
    purchase_avatar = PurchaseAvatar.Field()
    current_avatar = SetCurrentAvatar.Field()
    set_favorite_avatar_collection = SetFavoriteAvatarCollection.Field()
    set_avatar_skin_tone = SetAvatarSkinTone.Field()
    set_current_favorite_avatar_collection = SetCurrentFavoriteAvatarCollection.Field()
