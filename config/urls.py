"""
URL configuration for config project.

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
from django.urls import path, include
from config.accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('config.accounts.urls')), # API auth routes

    # Site page routes
    path('', account_views.IndexView.as_view(), name='index'),
    path('login/', account_views.SiteLoginView.as_view(), name='site_login'),
    path('registration/', account_views.SiteRegistrationView.as_view(), name='site_registration'),
    path('account/', account_views.SiteAccountView.as_view(), name='site_account'),
]
