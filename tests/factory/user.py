import factory
from django.contrib import auth


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = auth.get_user_model()

    username = factory.faker.Faker('name')
    password = "test"


