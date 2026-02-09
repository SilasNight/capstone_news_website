import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import Group

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .models import *
from django.contrib.auth.mixins import PermissionRequiredMixin

# Create your views here.


def user_logout(request):
    """
    This function is used to log a user out.
    """
    logout(request)

    # redirect to the login because a person needs to be logged in
    return redirect("Login")


def user_login(request):
    """
    This function is used to log a person in.
    """

    # I found that if a person used backspace you can be logged in
    # on the login page and that caused an error
    context = {}
    if request.user.is_authenticated:
        return redirect("Logout")

    # Getting relevant data
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Making sure the user exists.
        try:
            user = Users.objects.get(username=username)
        except Users.DoesNotExist:
            context = {
                "error": "That user does not exist"
            }
            return render(request, "user_login.html", context)

        # Authenticating the user and checking if the password was correct
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("Landing_Page")
        else:
            context = {
                "error": "Password incorrect"
            }
            return render(request, "user_login.html", context)

    return render(request, "user_login.html", context)


def user_registration(request):
    """
    This function is to create a new user
    """

    if request.method == "POST":

        # Getting all needed data from the page
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        email = request.POST.get("email")
        is_publisher = request.POST.get("publisher", False)
        is_editor = request.POST.get("editor", False)
        is_journalist = request.POST.get("journalist", False)

        # Making sure the username isn't taken
        try:
            user = Users.objects.get(username=username)
        except Users.DoesNotExist:
            pass
        else:
            context = {
                "error": "That username is taken"
            }
            return render(request, "user_registration.html", context)

        # Making sure the email is unique
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            pass
        else:
            context = {
                "error": "That email is taken"
            }
            return render(request, "user_registration.html", context)

        # Checking that passwords match
        if password != confirm_password:
            context = {
                "error": "Passwords do not match"
            }
            return render(request, "user_registration.html", context)

        # Getting role information
        role = ""
        if is_publisher:
            role += "Publisher"

        if is_editor:
            if role == "":
                role += "Editor"
            else:
                role += ", Editor"

        if is_journalist:
            if role == "":
                role += "Journalist"
            else:
                role += ", Journalist"

        # Creating the user
        user = Users.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=role,
        )

        user.set_password(password)
        user.save()

        # Everyone is a reader to someone right?
        reader = Group.objects.get_or_create(name="Reader")
        user.groups.add(reader.id)

        publisher_id = Group.objects.get(name="Publisher")
        editor_id = Group.objects.get(name="Editor")
        journalist_id = Group.objects.get(name="Journalist")

        if is_publisher:
            user.groups.add(publisher_id.id)

        if is_editor:
            user.groups.add(editor_id.id)

        if is_journalist:
            user.groups.add(journalist_id.id)

        # I don't want to do auth in two places,
        # so I redirect to the login
        return redirect("Login")
    return render(request, "user_registration.html")


@login_required
def user_delete(request):
    """
    This is used to delete a user
    """
    user = request.user
    user.delete()
    return redirect("Logout")


@login_required
def landing_page(request):
    """
    This is a function that shows all current newsletters to the user
    """

    # Making sure there are news_letters to display
    is_publisher = request.user.groups.filter(name="Publisher").exists()
    context = {
        "is_publisher": is_publisher
    }
    news_letters = Newsletter.objects.all()
    if len(news_letters) == 0:
        context["error"] = "There are no News Letters yet."

        return render(request, "news_letter_view.html", context)
    else:
        subscriptions = Subscriptions.objects.filter(user=request.user)
        subscriptions = [x.news_letter.title for x in subscriptions]
        context["subscriptions"] = subscriptions
        context["news_letters"] = news_letters
        return render(request, "news_letter_view.html", context)


@login_required
def news_letter_create(request):
    """
    This is used to make new newsletters
    """

    if request.method == "POST":

        # Getting relevant data
        title = request.POST.get("title")
        created_at = datetime.datetime.now()
        user = request.user

        # Make sure the newsletter title is available
        try:
            news_letter = Newsletter.objects.get(title=title)
        except Newsletter.DoesNotExist:
            pass
        else:
            context = {
                "error": "That title is taken"
            }
            return render(request, "news_letter_create.html", context)

        # make the newsletter
        news_letter = Newsletter.objects.create(
            title=title,
            created_at=created_at,
            author=user,
        )
        news_letter.save()

        return redirect("Landing_Page")

    return render(request, "news_letter_create.html")


def articles_view(request, title):
    """
    This is used to view all the articles for a newsletter
    """

    # Getting the newsletter that user wants to view
    news_letter = Newsletter.objects.get(title=title)
    is_editor = request.user.groups.filter(name="Editor").exists()
    is_journalist = request.user.groups.filter(name="Journalist").exists()
    context = {
        "news_letter": news_letter,
        "is_editor": is_editor,
        "is_journalist": is_journalist,
    }

    # Getting the articles for the newsletter
    # and making sure there are some
    articles = Articles.objects.filter(news_letter=news_letter)
    if len(articles) == 0:
        context["error"] = "There are no articles for this news letter yet."
    else:
        context["articles"] = articles

    return render(request, "article_view.html", context)


@login_required
def news_letter_edit(request, title):
    """
    Used to edit a newsletter
    """

    # Getting the newsletter to be edited
    news_letter = Newsletter.objects.get(title=title)
    context = {
        "news_letter": news_letter
    }

    if request.method == "POST":

        # Getting the new title
        new_title = request.POST.get("title")

        # Making sure the title has actually been changed
        # And returning an error if the title is already taken
        if news_letter.title != new_title:
            try:
                temp = Newsletter.objects.get(title=new_title)
            except Newsletter.DoesNotExist:
                news_letter.title = new_title
            else:
                context["error"] = f"{new_title} is already taken."

                return render(request, "news_letter_edit.html", context)

            # Changing the title and saving the newsletter
            news_letter.title = new_title
            news_letter.save()
        return redirect("Landing_Page")

    return render(request, "news_letter_edit.html", context)


@login_required
def news_letter_delete(request, title):
    """
    Used to delete a newsletter
    """

    news_letter = Newsletter.objects.get(title=title)
    news_letter.delete()

    return redirect("Landing_Page")


@login_required
def news_letter_subscribe(request, title):
    """
    Used by the webpage to subscribe to a newsletter
    """

    # Get the data needed
    news_letter = Newsletter.objects.get(title=title)
    user = request.user

    # Make sure the user isn't already subscribed
    try:
        temp = Subscriptions.objects.get(
            news_letter=news_letter,
            user=user,
        )
    except Subscriptions.DoesNotExist:

        # Subscribe the user if they weren't
        Subscriptions.objects.create(
            news_letter=news_letter,
            user=user,
        )

    return redirect("Landing_Page")


@login_required
def news_letter_unsubscribe(request, title):
    """
    Used to unsubscribe a user from a newsletter
    """

    # Get needed info
    news_letter = Newsletter.objects.get(title=title)
    user = request.user

    # Make sure the user is actually subscribed
    try:
        subscription = Subscriptions.objects.get(
            news_letter=news_letter,
            user=user,
        )
    except Subscriptions.DoesNotExist:
        pass
    else:
        # Remove the subscription if they were
        subscription.delete()

    return redirect("Landing_Page")


@login_required
def article_create(request, title):
    """
    Used to create a new article
    """

    # Get data
    news_letter_title = title
    news_letter = Newsletter.objects.get(title=news_letter_title)
    context = {
        "news_letter": news_letter
    }

    if request.method == "POST":

        # Getting data about the new article
        title = request.POST.get("title")
        content = request.POST.get("content")
        author = request.user
        publisher = news_letter.author

        # Making sure that an article with the current name
        # doesn't already exist for the newsletter
        try:
            article = Articles.objects.get(news_letter=news_letter, title=title)
        except Articles.DoesNotExist:
            pass
        else:
            context["error"] = f"That name is taken for {news_letter.title}"

            return render(request, "article_create.html", context)

        # If all checks are passed create the article
        article = Articles.objects.create(
            news_letter=news_letter,
            title=title,
            content=content,
            author=author,
            publisher=publisher,
        )

        return redirect('Article_View', title=news_letter.title)

    return render(request, "article_create.html", context)


@login_required
def article_edit(request, news_letter_title, title):
    """
    This is used to edit an article
    """

    # Getting data that is needed
    news_letter = Newsletter.objects.get(title=news_letter_title)
    article = Articles.objects.get(title=title, news_letter=news_letter)

    context = {
        "news_letter": news_letter,
        "article": article,
    }

    current_title = title
    if request.method == "POST":

        # Getting the new data to update the article with
        new_title = request.POST.get("title")
        content = request.POST.get("content")

        # Make sure the title was actually changed
        if new_title != current_title:
            try:

                # Check if there is an article with that
                # name already in the newsletter
                temp = Articles.objects.get(title=new_title, news_letter=news_letter)
            except Articles.DoesNotExist:

                # If not update
                article.title = new_title
            else:

                # If there is return error
                context["error"] = f"{new_title} is already used for {news_letter.title}"

                return render(request, "article_edit.html", context)

        # No need to check the content
        article.content = content
        article.approved = True
        article.save()

        # Find the user who approved the article and
        # save them as the articles editor
        try:
            temp = ArticlesEditors.objects.get(
                news_letter=news_letter,
                article=article,
            )
        except ArticlesEditors.DoesNotExist:
            pass
        else:

            # If there is already and editor for this article
            # Delete them and replace with new editor
            temp.delete()
        ArticlesEditors.objects.create(
            news_letter=news_letter,
            article=article,
            user=request.user,
        )

        # Make check to see if the news_letter has subscribers

        subscribers = Subscriptions.objects.filter(news_letter=news_letter)
        # if len(subscribers) != 0:
        #     message = (f"New article for {news_letter.title}\n"
        #                f"Title: {title}\n"
        #                f"Content:\n{content}")
        #     for subscriber in subscribers:
        #         output = (f"\n{subscriber.user.username}\nThere is a new article for you.\n"
        #                   f"{subscriber.user.email}\n")
        #         output += message + "\n"
        #         print(output)  # "emailing" the user
        emails = [subscriber.user.email for subscriber in subscribers]

        subject = f"New article posted to {news_letter.title}"
        from_email = settings.DEFAULT_FROM_EMAIL

        text_content = (f"{article.title}\n"
                        f"{article.created_at}"
                        f"{article.content}")

        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            emails,
        )
        email.send()

        return redirect("Article_View", title=news_letter_title)

    return render(request, "article_edit.html", context)


@login_required
def article_delete(request, news_letter_title, title):
    """
    Used to delete an article
    """

    # Getting the data and deleteing the article
    news_letter = Newsletter.objects.get(title=news_letter_title)
    article = Articles.objects.get(title=title, news_letter=news_letter)
    article.delete()

    return redirect("Article_View", title=news_letter_title)


def article_detailed_view(request, news_letter_title, title):
    """
    This details everything about an article
    """

    # Getting data that is needed
    news_letter = Newsletter.objects.get(title=news_letter_title)
    article = Articles.objects.get(news_letter=news_letter, title=title)
    context = {
        "article": article
    }

    # If the article as an editor add editor information
    if article.approved:
        editor = ArticlesEditors.objects.get(news_letter=news_letter, article=article)
        context["editor"] = editor.user

    return render(request, "article_detailed_view.html", context)


# API section


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    Used to login with an api
    """

    # Get data needed to login
    username = request.data.get("username")
    password = request.data.get("password")

    # Authentication and generate a token
    user = authenticate(request, username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "username": user.username,
        }, status=200)

    return Response({"error": "Invalid credentials"}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_view_subscriptions(request):
    """
    Used by api to see subscriptions
    """

    # Get the user making the request
    user = request.user

    # Get the subscriptions and make sure there are some
    subscriptions = Subscriptions.objects.filter(user=user)
    if len(subscriptions) == 0:
        return Response({
            "error": "Not subscribed to newsletters"
        }, status=200)

    # Get all the newsletters
    news_letters = []
    for subscription in subscriptions:
        news_letters.append(subscription.news_letter)

    # Format the data into json and return it
    data = {}
    for news_letter in news_letters:
        articles = Articles.objects.filter(news_letter=news_letter)
        data[news_letter.id] = {"news_letter": news_letter.title}
        for article in articles:
            data[news_letter.id][article.id] = {
                "title": article.title,
                "content": article.content,
                "author": article.author,
                "created_at": article.created_at.isoformat(),
                "approved": article.approved,
                "publisher": article.publisher
            }

    return Response(data, status=200)


@api_view(['GET'])
def api_news_letter_view(request):
    """
    This is used to look at the articles of a given newsletter
    """

    # Get the newsletter id
    news_letter_id = request.data.get("id")

    news_letter = get_object_or_404(Newsletter, id=news_letter_id)
    data = {}

    # Get the article data and send it
    articles = Articles.objects.filter(news_letter=news_letter)
    data[news_letter.id] = {"news_letter": news_letter.title}
    for article in articles:
        data[news_letter.id][article.id] = {
            "title": article.title,
            "content": article.content,
            "author": article.author.username,
            "created_at": article.created_at.isoformat(),
            "approved": article.approved,
            "publisher": article.publisher.username,
        }

    return Response(data, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_news_letter_subscribe(request):
    """
    This is used to subscribe to a newsletter
    """

    # Get data
    user = request.user
    news_letter_id = request.data.get("id")

    # Make sure there is a newsletter to subscribe to
    try:
        news_letter = Newsletter.objects.get(id=news_letter_id)
    except Newsletter.DoesNotExist:
        return Response({
            "error": "The newsletter does not exist"
        })

    # Make sure the user isn't already subscribed
    try:
        subscription = Subscriptions.objects.get(user=user, news_letter=news_letter)
    except Subscriptions.DoesNotExist:

        # Subscribe them if they weren't
        Subscriptions.objects.create(
            user=user,
            news_letter=news_letter
        )
        return Response({
            "success": "Subscribed successfully"
        }, status=200)
    else:
        return Response({
            "error": "Already subscribed"
        }, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_news_letter_unsubscribe(request):
    """
    Used to unsubscribe for a newsletter
    """

    # Get request data
    user = request.user
    news_letter_id = request.data.get("id")

    # Make sure there is a newsletter to unsubscribe from
    try:
        news_letter = Newsletter.objects.get(id=news_letter_id)
    except Newsletter.DoesNotExist:
        return Response({
            "error": "The newsletter does not exist"
        })

    # Make sure the user is subscribed
    try:
        subscription = Subscriptions.objects.get(user=user, news_letter=news_letter)
    except Subscriptions.DoesNotExist:
        return Response({
            "error": "not subscribed"
        })

    # If not then delete subscription
    else:
        subscription.delete()
        return Response({
            "success": "unsubscribed"
        })


@api_view(['GET'])
def api_news_letter_view_all(request):
    """
    This is used to view all available newsletters
    """

    # Make sure there are newsletters to show
    news_letters = Newsletter.objects.all()
    if not news_letters:
        return Response({
            "error": "There are no news letters"
        }, status=400)

    # Format all the data and send it
    data = {}
    for news_letter in news_letters:
        data[news_letter.id] = {
            "title": news_letter.title,
            "author": news_letter.author,
            "created_at": news_letter.created_at,
        }

    return Response(data, status=200)


@api_view(['GET'])
def api_article(request):
    """
    Get a detailed view of any given article by id
    """

    # Get all the data needed
    article_id = request.data.get("id")

    article = Articles.objects.get(id=article_id)

    news_letter = article.news_letter

    author = article.author
    publisher = article.publisher

    # Making it a list so that it can change later.
    # All depending on if there is an editor or not
    users = [author, publisher]

    # Add the editor to the user if the article was approved
    if article.approved:
        article_editors = ArticlesEditors.objects.get(news_letter=news_letter, article=article)
        editor = article_editors.editor
        users.append(editor)

    # format all the data
    user_data = {}
    user_titles = ["author_info", "publisher_info", "editor_info"]
    for index, user in enumerate(users):
        user_data[user_titles[index]] = {
            "username": user.username,
            "fullname": f"{user.first_name} {user.last_name}",
            "email": user.email,
        }

    data = {
        news_letter.id: {
            "news_letter_title": news_letter.title,
            "created_at": news_letter.created_at.isoformat(),
            article.id: {
                "title": article.title,
                "content": article.content,
                "create_at": article.created_at.isoformat(),
                "approved": article.approved,
                "users": user_data,
            }
        }
    }

    return Response(data, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_news_letter_create(request):
    """
    Used to create a new newsletter
    """

    user = request.user
    is_publisher = request.user.groups.filter(name="Publisher").exists()

    # Making sure the user is allowed to make a newsletter
    if not is_publisher:
        return Response({"error": "User invalid for news_letter_create"})

    news_letter_title = request.data.get("title")

    # Making sure the newsletter title isn't already taken
    try:
        temp = Newsletter.objects.get(title=news_letter_title)
    except Newsletter.DoesNotExist:

        # Create the newsletter
        news_letter = Newsletter.objects.create(
            title=news_letter_title,
            author=request.user,
            created_at=datetime.datetime.now(),
        )

        return Response({
            "id": news_letter.id
        }, status=200)

    else:

        return Response({"error": "That news letter title is in use"}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_article_create(request):
    """
    Used to create a new article
    """

    user = request.user
    is_journalist = request.user.groups.filter(name="Journalist").exists()
    # Make sure the user is allowed to create an article
    if not is_journalist:
        return Response({
            "error": "You don't have permission to create a article"
        })

    # Getting the id of the newsletter this article will belong to
    news_letter_id = request.data.get("news_letter_id")

    title = request.data.get("title")
    content = request.data.get("content")

    # Make sure the newsletter exists
    try:
        news_letter = Newsletter.objects.get(id=news_letter_id)
    except Newsletter.DoesNotExist:
        return Response({
            "error": "News letter does not exist"
        })

    # Making sure the articles name isn't taken
    try:
        temp = Articles.objects.get(news_letter=news_letter, title=title)
    except Articles.DoesNotExist:
        pass
    else:
        return Response({
            "error": f"{title}, already exists in {news_letter.title}"
        })

    # Getting the rest of the data to make the article
    publisher = news_letter.author
    author = user
    created_at = datetime.datetime.now()
    approved = False

    # Make the article
    article = Articles.objects.create(
        news_letter=news_letter,
        title=title,
        content=content,
        author=author,
        created_at=created_at,
        approved=approved,
        publisher=publisher,
    )
    article_id = article.id
    return Response({"id": article_id}, status=200)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_news_letter_edit(request):
    """
    used to edit a newsletter
    """

    # Getting data from request
    user = request.user
    news_letter_id = request.data.get("id")
    is_editor = request.user.groups.filter(name="Editor").exists()
    is_journalist = request.user.groups.filter(name="Journalist").exists()

    # Making sure the user is allowed to edit newsletters
    if not is_editor and not is_journalist:
        return Response({
            "error": "You are not allowed to edit anything"
        })

    # Making sure the newsletter exists
    try:
        news_letter = Newsletter.objects.get(id=news_letter_id)
    except Newsletter.DoesNotExist:
        return Response({
            "error": "News letter does not exist"
        })

    new_title = request.data.get("title")

    # Making sure the newsletters name has been changed
    # and if it is available
    if new_title != news_letter.title:
        try:
            temp = Newsletter.objects.get(title=new_title)
        except Newsletter.DoesNotExist:
            pass
        else:
            return Response({
                "error": "News letter name already taken"
            })

    # Updating the newsletter
    news_letter.title = new_title
    news_letter.save()

    return Response({
        news_letter_id: "News letter name changed successfully"
    }, status=200)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_article_edit(request):
    """
    Used to edit articles
    """

    user = request.user
    is_editor = request.user.groups.filter(name="Editor").exists()
    is_journalist = request.user.groups.filter(name="Journalist").exists()

    # Making sure the user is allowed to edit articles
    if not is_editor and not is_journalist:
        return Response({
            "error": "You are not allowed to edit anything"
        })

    # Getting the new data from request
    article_id = request.data.get("id")
    title = request.data.get("title")
    content = request.data.get("content")

    # Making sure the article exists
    try:
        article = Articles.objects.get(id=article_id)
    except Articles.DoesNotExist:
        return Response({
            "error": "article does not exist"
        })

    news_letter = article.news_letter

    # Checking if the article title is free
    if title != article.title:
        try:
            temp = Articles.objects.get(news_letter=news_letter, title=title)
        except Articles.DoesNotExist:
            pass
        else:
            return Response({
                "error": f"{title} already exists in {news_letter.title}"
            })

    # Updating the article information
    article.title = title
    article.content = content
    article.approved = True
    article.save()

    # Checking if the article has an editor and then changing it
    try:
        temp = ArticlesEditors.objects.get(article=article, editor=user)
    except ArticlesEditors.DoesNotExist:
        ArticlesEditors.objects.create(
            news_letter=news_letter,
            article=article,
            user=user,
        )
    else:
        temp.delete()
        ArticlesEditors.objects.create(
            news_letter=news_letter,
            article=article,
            user=user,
        )

    return Response({article_id: "Successfully edited"}, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_news_letter_delete(request):
    """
    Used to delete a newsletter
    """

    user = request.user
    is_editor = request.user.groups.filter(name="Editor").exists()
    is_journalist = request.user.groups.filter(name="Journalist").exists()

    # Making sure the user is allowed to delete newsletters
    if not is_editor and not is_journalist:
        return Response({
            "error": "You are not allowed to delete that"
        })

    news_letter_id = request.data.get("id")

    # Making sure the newsletter exists
    try:
        news_letter = Newsletter.objects.get(id=news_letter_id)
    except Newsletter.DoesNotExist:
        return Response({
            "error": "News letter does not exist"
        })

    # Getting the title for the reply and deleting the newsletter
    title = news_letter.title
    news_letter.delete()

    return Response({
        news_letter_id: f"successfully deleted {title}."
    }, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_article_delete(request):
    """
    Used to delete an article
    """

    user = request.user
    is_editor = request.user.groups.filter(name="Editor").exists()
    is_journalist = request.user.groups.filter(name="Journalist").exists()

    # Make sure the user is allowed to delete an article
    if not is_editor and not is_journalist:
        return Response({
            "error": "You are not allowed to delete that"
        })
    article_id = request.data.get("id")

    # Making sure the article exists
    try:
        article = Articles.objects.get(id=article_id)
    except Articles.DoesNotExist:
        return Response({
            "error": f"Article with id {article_id}"
        })

    # Deleting the article
    title = article.title
    article.delete()
    
    return Response({
        article_id: f"Successfully deleted {title}"
    }, status=200)
