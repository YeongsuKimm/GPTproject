"""
URL configuration for projectGPT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='to-index'),
    path('generate/', views.GenerateView.as_view(), name="generate_storybook"),
    path('login/', views.LoginView.as_view(), name="to-login"),
    path('signup/', views.SignupView.as_view(), name="to-signup"),
    path('history/',views.HistoryView.as_view(), name="to-history"),
    path('get-story/<int:id>/', views.StoryGetView.as_view(), name="to-get-story"),
    path('story/<int:id>/', views.StoryView.as_view(), name="to-story")
]
