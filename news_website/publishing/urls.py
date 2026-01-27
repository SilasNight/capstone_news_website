from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_login, name="Login"),
    path("user/logout/", views.user_logout, name="Logout"),
    path("user/new/", views.user_registration, name="New_User"),
    path("user/delete/", views.user_delete, name="User_Delete"),

    path("landing_page/", views.landing_page, name="Landing_Page"),
    path("news_letter/create/", views.news_letter_create, name="News_Letter_Create"),
    path("news_letter/edit/<str:title>/", views.news_letter_edit, name="News_Letter_Edit"),
    path("news_letter/delete/<str:title>", views.news_letter_delete, name="News_Letter_Delete"),

    path("news_letter/<str:title>/", views.articles_view, name="Article_View"),
    path("news_letter/<str:title>/create/", views.article_create, name="Article_Create"),
    path("article_edit/<str:news_letter_title>/<str:title>/", views.article_edit, name="Article_Edit"),
    path("article_delete/<str:news_letter_title>/<str:title>/", views.article_delete, name="Article_Delete"),
    path("detailed_view/<str:news_letter_title>/<str:title>/", views.article_detailed_view, name="Article_Detailed"),

    path("news_letter/sub/<str:title>/", views.news_letter_subscribe, name="Subscribe"),
    path("news_letter/unsub/<str:title>/", views.news_letter_unsubscribe, name="Unsubscribe"),

    path("api/subscriptions/", views.api_view_subscriptions, name="Api_Subscriptions"),
    path("api/login/", views.api_login, name="Api_Login"),

    path("api/news_letter/", views.api_news_letter_view, name="Api_Newsletter_View"),
    path("api/news_letter/all/", views.api_news_letter_view_all, name="Api_Newsletter_View_All"),
    path("api/news_letter/create/", views.api_news_letter_create, name="Api_Newsletter_Create"),
    path("api/news_letter/edit/", views.api_news_letter_edit, name="Api_Newsletter_Edit"),
    path("api/news_letter/delete/", views.api_news_letter_delete, name="Api_Newsletter_Delete"),
    path("api/news_letter/subscribe/", views.api_news_letter_subscribe, name="Api_Newsletter_Sub"),
    path("api/news_letter/unsubscribe/", views.api_news_letter_unsubscribe, name="Api_Newsletter_Unsub"),

    path("api/article/", views.api_article, name="Api_Article"),
    path("api/article/create/", views.api_article_create, name="Api_Article_Create"),
    path("api/article/edit/", views.api_article_edit, name="Api_Article_Edit"),
    path("api/article/delete/", views.api_article_delete, name="Api_Article_Delete"),

]
