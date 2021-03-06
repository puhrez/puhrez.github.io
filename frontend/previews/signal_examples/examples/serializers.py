from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth.models import User
from .models import Author, Book, AuthorBalance



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = dict(password=dict(write_only=True))


class AuthorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Author
        fields = ('user', 'pseudonym')

    def create(self, validated_data):
        user_data = validated_data.pop('user')

        with transaction.atomic():
            user = User.objects.create_user(**user_data)
            return Author.objects.create(user=user, **validated_data)


class AuthorSerializerFromManager(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Author
        fields = ('user', 'pseudonym')

    def create(self, validated_data):
        return Author.objects.create_with_user(
            pseudonym=validated_data['pseudonym'],
            **validated_data['user'])


class BookPurchaseSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=0)

    class Meta:
        model = Book
        fields = ('quantity',)

    def update(self, validated_data):
        due = validated_data['quantity'] * self.instance.value \
              * settings.EXAMPLE_SERVICE_CHARGE

        try:
            self.instance.royalties.value += due
        except AuthorBalance.DoesNotExist():
            AuthorBalance(author=self.author, book=self.instance, value=due)
