"""
URL configuration for cms project.

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
import mdeditor.urls
from decorator_include import decorator_include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.decorators.clickjacking import xframe_options_exempt

from blog.views import CategoryView, PostDetailView, PostListView, SearchView, upload_attachment
from cms import settings
from cms.custom_site import custom_site

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('category/<int:category_id>/', CategoryView.as_view(), name='post-list'),
    path('post/<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    path('search/', SearchView.as_view(), name='post-list'),
    path('super_admin/', admin.site.urls, name='super-admin'),
    path('admin/', custom_site.urls, name='admin'),

    # 跨域问题  decorator_include和include的区别，xframe_options_exempt主要是为了iframe的嵌入
    path('mdeditor/', decorator_include(xframe_options_exempt, mdeditor.urls)),
    path('upload-attachment/', upload_attachment, name='upload_attachment'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
print(urlpatterns)