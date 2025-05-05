from django.urls import path
from .import views
from .views import reviewpage
from .views import create_payment, payment_page
from .views import create_payment 
urlpatterns = [
    path('', views.home, name='home'), 
    path('home/', views.home, name='home'),
    path('faqs/', views.faqs, name='faqs'),
    path('menu/', views.menu, name='menu'),
    path('products/', views.product_list, name='product_list'),

    path("pay/", payment_page, name="payment_page"),
    path("create-payment/", create_payment, name="create_payment"),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
      path('thank_you/', views.thank_you, name='thank_you'),
      path('submit_review/', views.submit_review, name='submit_review'),
     path('review/', reviewpage, name='review'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('update_info/', views.update_info, name='update_info'),
    path('about/', views.about, name='about'),
    path('category/<str:food>', views.category, name='category'),
]
