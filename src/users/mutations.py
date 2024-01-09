import graphene
from users.schema import UserSchema


class UpdateUserLanguage(graphene.Mutation):
    user = graphene.Field(UserSchema)

    class Arguments:
        language = graphene.String()

    def mutate(self, info, language):
        user = info.context.user

        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")

        user.language = language
        user.save()

        return UpdateUserLanguage(user=user)


class Mutation(graphene.ObjectType):
    update_user_language = UpdateUserLanguage.Field()
