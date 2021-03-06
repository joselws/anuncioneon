from django.urls import path
from ads import views

urlpatterns = [
    path('', views.index, name='index'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('category/<str:category_name>', views.category, name="category"),
    path('filtered', views.filtered, name="filtered"),
]