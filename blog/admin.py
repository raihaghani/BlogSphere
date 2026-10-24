from django.contrib import admin
from .models import Post, Category, Comment
from .services import set_publication

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'created_at', 'published_at']
    list_filter = ['status', 'category']
    search_fields = ['title', 'content', 'author__username']
    list_select_related = ['author', 'category']
    readonly_fields = ['slug', 'created_at', 'updated_at', 'published_at']
    actions = ['publish', 'unpublish']
    @admin.action(description='Publish selected articles', permissions=['change'])
    def publish(self, request, queryset):
        for post in queryset:
            set_publication(post, request.user, Post.Status.PUBLISHED)
    @admin.action(description='Return selected articles to draft', permissions=['change'])
    def unpublish(self, request, queryset):
        for post in queryset:
            set_publication(post, request.user, Post.Status.DRAFT)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['post', 'user']
    search_fields = ['content', 'user__username']
    list_select_related = ['post', 'user']

admin.site.site_header = 'BlogSphere administration'
admin.site.site_title = 'BlogSphere'
