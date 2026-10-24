from django.contrib import admin
from django.urls import include, path

urlpatterns = [path('admin/', admin.site.urls), path('', include('accounts.urls')),
               path('', include('blog.urls')), path('api/', include('api.urls'))]
handler403 = 'blog.views.error403'
handler404 = 'blog.views.error404'
handler500 = 'blog.views.error500'
