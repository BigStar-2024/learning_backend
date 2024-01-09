import factory
from .models import Student

class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student

    first_name = factory.Faker('first_name_female', locale='es_MX')
    last_name = factory.Faker('last_name', locale='es_MX')
    dob = factory.Faker('date_between', start_date='-50y', end_date='-20y')
    gender = factory.Iterator(['MALE', 'FEMALE', 'OTHER'])