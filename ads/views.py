from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from ads.models import *
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.


def index(request):
    """
    Redirects to /login if the user is not registered 
    otherwise shows the home page
    """
    if request.user.is_authenticated:
        categories = MainCategory.objects.all()
        return render(request, "ads/index.html", {
            'categories': categories
        })

    else:
        return HttpResponseRedirect(reverse('login'))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "ads/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "ads/login.html")


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse('login'))


def register(request):
    if request.method == "POST":

        if not request.user.is_authenticated:
            username = request.POST["username"]

            # Ensure password matches confirmation
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]

            if len(password) == 0:
                return render(request, "ads/register.html", {
                    "message": 'Password must be at least 1 character long.'
                }) 

            if password != confirmation:
                return render(request, "ads/register.html", {
                    "message": "Passwords must match."
                })

            # Attempt to create new user
            try:
                # empty email field necessary or authenticate() wont work
                user = User.objects.create_user(username, '', password)
                user.save()
            except IntegrityError:
                return render(request, "ads/register.html", {
                    "message": "Username already taken."
                })
            except ValueError:
                return render(request, 'ads/register.html', {
                    'message': 'Username must contain at least 1 letter.'
                })
            else:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))

        # user is authenticated
        else:
            return HttpResponseRedirect(reverse('index'))

    # Get request
    else:
        return render(request, "ads/register.html")
