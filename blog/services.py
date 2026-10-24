from django.core.exceptions import PermissionDenied
from django.db import transaction
from .models import Post, Comment

def can_author(user):
    return user.is_authenticated and user.is_active and (user.is_superuser or
           (user.groups.filter(name='Author').exists() and user.has_perm('blog.add_post')))

def can_manage(user, post, action='change'):
    if not user.is_authenticated or not user.is_active:
        return False
    permission = user.has_perm(f'blog.{action}_post')
    return permission and ((can_author(user) and post.author_id == user.pk) or user.is_staff or user.is_superuser)

@transaction.atomic
def set_publication(post, user, status):
    post = Post.objects.select_for_update().get(pk=post.pk)
    if not can_manage(user, post):
        raise PermissionDenied
    post.status = status
    post.save()
    return post

@transaction.atomic
def add_comment(post, user, content):
    if not user.is_authenticated:
        raise PermissionDenied
    post = Post.objects.select_for_update().get(pk=post.pk)
    comment = Comment(post=post, user=user, content=content)
    comment.full_clean()
    comment.save()
    return comment
