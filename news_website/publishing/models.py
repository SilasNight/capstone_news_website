from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Users(AbstractUser):

    # These are no longer used in favour of group permissions
    # I just left them in so that I don't have to change
    # to the base user everywhere
    publisher = models.BooleanField(default=False)
    editor = models.BooleanField(default=False)
    journalist = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Newsletter(models.Model):
    title = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Users, on_delete=models.CASCADE)


class Articles(models.Model):
    news_letter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name="newsletter_articles")
    title = models.CharField(max_length=20)
    content = models.CharField(max_length=200)
    author = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="author_articles")
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    publisher = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="publisher_articles")


class ArticlesEditors(models.Model):
    news_letter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name="approved_news_letter")
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, related_name="approved_article")
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="article_editor")


class Subscriptions(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="subscriber_subscriptions")
    news_letter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name="news_letter_subscription")
