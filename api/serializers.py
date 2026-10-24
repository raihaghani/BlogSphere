from rest_framework import serializers
from blog.models import Post, Category, Comment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'excerpt', 'status', 'author', 'category', 'category_detail',
                  'cover_image', 'created_at', 'updated_at', 'published_at']
        read_only_fields = ['slug', 'created_at', 'updated_at', 'published_at']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    content = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True)
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at']
        read_only_fields = ['post', 'created_at']
