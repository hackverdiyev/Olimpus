from django.urls import path
from . import views

urlpatterns = [
    path('',views.base,name='base'),
    path('contact/',views.contact,name='contact'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('register/',views.register,name='register'),
    path('restore_password/',views.restore_password,name='restore_password'),
    path('verification/<str:username>/<str:request_type>/',views.verification,name='verification'),
    path('verification/<str:username>/<str:request_type>/again/',views.verification_again,name='verification_again'),
    path('select_password/<str:username>/',views.select_password,name='select_password'),
    path('profile/<str:username>/',views.profile,name='profile'),
    path("news/", views.news, name="news"),
    path("news/<int:id>/", views.news_view, name="news_view"),
    path("versions/<str:version>/", views.versions, name="versions"),
    path("verify/", views.verify, name="verify"),
]
