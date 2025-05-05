from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product, Category, Profile, review  # Ensure `Review` model is imported
from django.http import HttpResponse
import json
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def create_payment(request):
    if request.method == "POST":
        amount = int(request.POST.get("amount")) * 100  # Convert to paisa
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
        return JsonResponse(payment)

from cart.cart import Cart
from django.shortcuts import get_object_or_404
from django.shortcuts import render
def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query)
    return render(request, 'product_list.html', {
        'products': products,
        'query': query
    })

def payment_page(request):
    return render(request, 'payment.html')

def delete_review(request, review_id):
    obj = get_object_or_404(review, id=review_id)
    if request.method == "POST":
        obj.delete()
        return redirect('reviewpage')  # Use your review page's URL name
    return redirect('reviewpage')
def submit_review(request):
    if request.method == 'POST':
        # Get the review form data
        name = request.POST.get('name')
        review_text = request.POST.get('review')
        rating = request.POST.get('rating')

        # Save the review to the database
        new_review = review(name=name, review_text=review_text, rating=rating)
        new_review.save()

        # Redirect to a thank-you page or back to the reviews
        return redirect('thank_you')  # Make sure 'thank_you' is a valid URL name

    return redirect('reviewpage')  # This should match the name in your urls.py

def thank_you(request):
    return render(request, 'thank_you.html')

def reviewpage(request):
    if request.method == 'POST':
        # Handle review submission
        name = request.POST.get('name')
        review_text = request.POST.get('review')
        rating = request.POST.get('rating')

        # Save review to database
        new_review = review(name=name, review_text=review_text, rating=rating)
        new_review.save()

        return redirect('thank_you')  # Redirect to a thank you page or confirmation
        
    reviews = review.objects.all()  # Fetch all reviews from the database
    return render(request, 'review.html', {'reviews': reviews})  # Pass reviews to template

# Other views (e.g., for user profiles, categories, etc.)
def update_info(request):
    if request.user.is_authenticated:
        try:
            current_user = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            current_user = Profile(user=request.user)

        if request.method == 'POST':
            current_user.phone = request.POST.get('phone')
            current_user.address1 = request.POST.get('address1')
            current_user.address2 = request.POST.get('address2')
            current_user.city = request.POST.get('city')
            current_user.state = request.POST.get('state')
            current_user.zipcode = request.POST.get('zipcode')
            current_user.country = request.POST.get('country')
            current_user.save()
            request.session['my_shipping'] = {
                'shipping_full_name': request.POST.get('full_name', request.user.get_full_name()),
                'shipping_email': request.POST.get('email', request.user.email),
                'shipping_address1': request.POST.get('address1'),
                'shipping_address2': request.POST.get('address2'),
                'shipping_city': request.POST.get('city'),
                'shipping_state': request.POST.get('state'),
                'shipping_zipcode': request.POST.get('zipcode'),
                'shipping_country': request.POST.get('country'),
            }
            messages.success(request, "Your info has been updated")
            return redirect('home')

        return redirect('home')
    else:
        messages.error(request, "You must be logged in")
        return redirect('home')

# Other views like category, menu, faqs, etc.
def category(request, food):
    try:
        category = Category.objects.get(name=food)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except Category.DoesNotExist:
        messages.success(request, "The category doesn't exist.")
        return redirect('menu')

def menu(request):
    products = Product.objects.all()
    return render(request, 'menu.html', {'products': products})

def home(request):
    return render(request, 'home.html', {})

def faqs(request):
    return render(request, 'faqs.html', {})

def about(request):
    return render(request, 'about.html', {})

def logout_view(request):
    if request.user.is_authenticated:
        cart = Cart(request)

        # Ensure Profile exists
        profile, created = Profile.objects.get_or_create(user=request.user)

        # Save the cart to Profile
        profile.old_cart = json.dumps(cart.cart)  # assuming cart.cart returns a dict
        profile.save()

        logout(request)

    return redirect('/')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Username does not exist')
            return render(request, 'home.html', {'show_login': True})

        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid password')
            return render(request, 'home.html', {'show_login': True})

        login(request, user)

        # Ensure Profile exists
        profile, created = Profile.objects.get_or_create(user=user)

        # Restore cart from saved data
        saved_cart = profile.old_cart
        if saved_cart:
            converted_cart = json.loads(saved_cart)
            cart = Cart(request)
            for key, value in converted_cart.items():
                cart.db_add(product=key, quantity=value)

        return redirect('/home/')

    return redirect('/home/')

def register_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already in use')
            return redirect('/')

        # Create user and save
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Ensure Profile is created if it doesn't exist
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user, old_cart=json.dumps({}))

        # Auto login
        login(request, user)
        return redirect('/')

    return render(request, 'register.html')
