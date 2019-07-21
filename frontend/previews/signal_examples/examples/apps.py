from django.apps import AppConfig


class ExamplesConfig(AppConfig):
    name = 'examples'

    def ready(self):
        from . import signals  # noqa
