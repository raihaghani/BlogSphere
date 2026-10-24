from django.urls import path
from . import views
urlpatterns = [path('', views.home, name='home'), path('categories/<slug:slug>/', views.home, name='category'),
               path('posts/<slug:slug>/', views.detail, name='post_detail'), path('dashboard/', views.dashboard, name='dashboard'),
               path('dashboard/posts/create/', views.editor, name='post_create'),
               path('dashboard/posts/<int:pk>/edit/', views.editor, name='post_edit'),
               path('dashboard/posts/<int:pk>/delete/', views.delete, name='post_delete'),
               path('dashboard/posts/<int:pk>/publish/', views.publication, {'action': 'publish'}, name='post_publish'),
               path('dashboard/posts/<int:pk>/unpublish/', views.publication, {'action': 'unpublish'}, name='post_unpublish')]
