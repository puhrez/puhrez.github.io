from django.db import models
from django.contrib.auth.models import User


class AuthorManager(models.Manager):
    def create_with_user(self, username, password, pseudonym, **kwargs):
        user = User.objects.create_user(username, password=password, **kwargs)
        return super().create(user=user, pseudonym=pseudonym)


class Author(models.Model):
    objects = AuthorManager()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pseudonym = models.CharField(max_length=50)


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    value = models.IntegerField()


class AuthorBalance(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='dues')
    book = models.ForeignKey(Book, on_delete=models.CASCADE,
                             related_name='royalties')
    value = models.FloatField(default=0)
