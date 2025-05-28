from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from app import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question_detail, name='question'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
    path('profile/edit/', views.settings, name='edit'),
    path('logout/', views.logout_view, name='logout'),
    path('benchmark/', views.benchmark_view),
    path('question/like/', views.question_like, name='question_like'),
    path('answer/like/', views.answer_like, name='answer_like'),
    path('answer/mark_correct/', views.mark_correct_answer, name='mark_correct'),
    path('search/', views.search_suggestions, name='search'),
]
