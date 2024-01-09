import graphene
from graphql import GraphQLError
from django.contrib.auth import get_user_model

from certificates.schema import CertificatesSchema, StudentCertificatesSchema
from .models import Notes

from django.db import transaction, DatabaseError
import sys
import os

# Create Certificate
class SendNote(graphene.Mutation):
    result = graphene.String()

    class Arguments:
        title = graphene.String(required=True)
        text = graphene.String(required=True)
        date_to_send = graphene.DateTime(required=True)
        receiver_user_ids = graphene.List(graphene.ID, required=True)

    def mutate(root, info, title, text, date_to_send, receiver_user_ids):
        try:
            with transaction.atomic():
                if not info.context.user.is_authenticated:
                    raise Exception("Authentication credentials were not provided")
                
                user = info.context.user
                role = user.profile.role
                print(role, user.id)

                if(not(role == "adminTeacher" or role == "subscriber" or role == "teacher")):
                    raise Exception("You don't have permission!")
                
                for receiver_id in receiver_user_ids:
                    
                    receiver = get_user_model().objects.get(pk = receiver_id)

                    note = Notes(
                        title = title,
                        text = text,
                        send_at = date_to_send,
                        user_from = user,
                        user_to = receiver,
                    )
                    note.save()

                return SendNote(result="Success")
        except (Exception, DatabaseError) as e:
            transaction.rollback()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return e

class Mutation(graphene.ObjectType):
    send_note = SendNote.Field()
