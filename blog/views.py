from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods
from .models import Post, Category
from .forms import PostForm, CommentForm
from .services import can_author, can_manage, set_publication, add_comment

def author_required(view):
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not can_author(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapped

def home(request, slug=None):
    posts = Post.objects.published().with_details()
    query = request.GET.get('q', '').strip()[:200]
    category_slug = slug or request.GET.get('category', '')
    category = get_object_or_404(Category, slug=category_slug) if category_slug else None
    if query:
        posts = posts.search(query)
    if category:
        posts = posts.filter(category=category)
    params = request.GET.copy()
    params.pop('page', None)
    return render(request, 'home.html', {'page_obj': Paginator(posts, 9).get_page(request.GET.get('page')),
                  'categories': Category.objects.all(), 'category': category, 'query': query,
                  'filter_query': params.urlencode(), 'featured': posts.first() if not query and not category else None})

@require_http_methods(['GET', 'POST'])
def detail(request, slug):
    post = get_object_or_404(Post.objects.published().with_details(), slug=slug)
    form = CommentForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            raise PermissionDenied
        if form.is_valid():
            try:
                add_comment(post, request.user, form.cleaned_data['content'])
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(request, 'Your comment has been added.')
                return redirect('post_detail', slug=post.slug)
    comments = Paginator(post.comments.select_related('user'), 20).get_page(request.GET.get('page'))
    return render(request, 'blog/detail.html', {'post': post, 'form': form, 'comments': comments})

@author_required
def dashboard(request):
    posts = Post.objects.filter(author=request.user).with_details().order_by('-created_at', '-pk')
    return render(request, 'blog/dashboard.html', {'page_obj': Paginator(posts, 10).get_page(request.GET.get('page')),
                  'total': posts.count(), 'published': posts.published().count(), 'drafts': posts.filter(status='DRAFT').count()})

@author_required
@require_http_methods(['GET', 'POST'])
def editor(request, pk=None):
    post = get_object_or_404(Post, pk=pk, author=request.user) if pk else Post(author=request.user)
    if pk and not can_manage(request.user, post):
        raise PermissionDenied
    form = PostForm(request.POST if request.method == 'POST' else None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Article saved successfully.')
        return redirect('dashboard')
    return render(request, 'blog/editor.html', {'form': form, 'post': post})

@author_required
@require_POST
def publication(request, pk, action):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    set_publication(post, request.user, Post.Status.PUBLISHED if action == 'publish' else Post.Status.DRAFT)
    messages.success(request, 'Publication status updated.')
    return redirect('dashboard')

@author_required
@require_http_methods(['GET', 'POST'])
def delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if not can_manage(request.user, post, 'delete'):
        raise PermissionDenied
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Article deleted.')
        return redirect('dashboard')
    return render(request, 'blog/delete.html', {'post': post})

def error403(request, exception=None):
    return render(request, 'errors/error.html', {'code': 403, 'message': 'You do not have access to this page.'}, status=403)
def error404(request, exception=None):
    return render(request, 'errors/error.html', {'code': 404, 'message': 'This page could not be found.'}, status=404)
def error500(request):
    return render(request, 'errors/error.html', {'code': 500, 'message': 'Something went wrong. Please try again later.'}, status=500)
