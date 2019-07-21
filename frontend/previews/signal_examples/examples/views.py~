from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.generics import CreateAPIView, UpdateAPIView
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from .models import Author, Book
from .serializers import (AuthorSerializer,
                          AuthorSerializerFromManager,
                          BookPurchaseSerializer)


class ViewLogicExample(APIView):
    def post(self, request):
        try:
            user_data = dict(
                username=request.data['user']['username'],
                password=request.data['user']['password'])
        except KeyError:
            raise ParseError('user data misformed')

        try:
            author_data = dict(
                pseudonym=request.data['pseudonym']
            )
        except KeyError:
            raise ParseError('author data misformed')

        try:
            with transaction.atomic():
                user = User.objects.create_user(**user_data)
                author = Author.objects.create(user=user, **author_data)
        except IntegrityError:
            raise ParseError('author already exists')

        return Response(dict(user=dict(username=user.username,
                                       pseudonym=author.pseudonym)),
                        status=status.HTTP_201_CREATED)


class SerializerLogicExample(CreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class SerializerFromManagerExample(CreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializerFromManager


class PurchaseBook(UpdateAPIView):
    queryset = Book.objects.all()
    serialzer_class = BookPurchaseSerializer
