from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarDealer, CarMake, CarModel, DealerReview
# from .restapis import related methods
from.restapis import get_request, get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            messages.warning(request, 'Invalid username or password')
            return redirect('djangoapp:index')


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect("djangoapp:index")

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        password = request.POST['psw']
        user_exists = False
        try:
            User.objects.get(username=username)
            user_exists = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exists:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("/djangoapp/")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/0364ce86-d18b-454f-9020-55730873902d/dealership-package/get-dealership"
        # Get dealerships from the database
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        context = {}
        context["dealerships"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/0364ce86-d18b-454f-9020-55730873902d/dealership-package/get-dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        #print(context)
        context["dealer"] = dealer
        review_url = "https://us-south.functions.appdomain.cloud/api/v1/web/0364ce86-d18b-454f-9020-55730873902d/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(review_url, id=id)
        #print(reviews)
        context["reviews"] = reviews
        context["current_page"] = "dealer_reviews"
        print('context for dealer_details', context)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

def add_review(request, id):
    if request.user.is_authenticated:
        context = {}
        dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/0364ce86-d18b-454f-9020-55730873902d/dealership-package/get-dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        context["dealer"] = dealer
        if request.method == 'GET':
            cars = CarModel.objects.all()
            context["cars"] = cars
            #print(context)
            return render(request, 'djangoapp/add_review.html', context)
        
        elif request.method == 'POST':
            if request.user.is_authenticated:
                username = request.user.username
                print('POST method with: ',request.POST)
                payload = dict()
                car_id = request.POST["car"]
                car = CarModel.objects.get(pk=car_id)
                payload["time"] = datetime.utcnow().isoformat()
                payload["name"] = request.POST["name"]
                payload["dealership"] = id
                payload["id"] = id
                payload["review"] = request.POST["content"]
                payload["purchase"] = False
                if "purchasecheck" in request.POST:
                    if request.POST["purchasecheck"] == 'on':
                        payload["purchase"] = True
                        payload["purchase_date"] = request.POST["purchase_date"]
                        payload["car_make"] = car.make.name
                        payload["car_model"] = car.name
                        payload["car_year"] = int(car.year.strftime("%Y"))

                new_payload = {}
                new_payload["review"] = payload
                review_post_url = "https://us-south.functions.appdomain.cloud/api/v1/web/0364ce86-d18b-454f-9020-55730873902d/dealership-package/post-review"
                post_request(review_post_url, new_payload, id=id)
            return redirect("djangoapp:dealer_details", id=id)
