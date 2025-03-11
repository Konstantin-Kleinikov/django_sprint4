from django.db import models

from .constants import TITLE_DISPLAY_LENGTH


class CreatedPublishedModel(models.Model):
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class TitleModel(CreatedPublishedModel):
    title = models.CharField(
        'Заголовок',
        max_length=256
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title[:TITLE_DISPLAY_LENGTH]
