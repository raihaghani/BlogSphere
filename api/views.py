from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from blog.models import Post, Category
from blog.services import set_publication, add_comment
from .permissions import PostPermission, CategoryPermission
from .serializers import PostSerializer, CategorySerializer, CommentSerializer

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [PostPermission]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        posts = Post.objects.with_details()
        if self.request.method in ['GET', 'HEAD', 'OPTIONS'] or self.action == 'comments':
            posts = posts.published()
        elif not (self.request.user.is_staff and self.request.user.has_perm(
                'blog.delete_post' if self.request.method == 'DELETE' else 'blog.change_post')):
            posts = posts.filter(author=self.request.user)
        if self.action == 'list':
            posts = posts.search(self.request.query_params.get('search', '').strip()[:200])
            category = self.request.query_params.get('category')
            if category:
                posts = posts.filter(category__slug=category)
        return posts

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        return Response(self.get_serializer(set_publication(self.get_object(), request.user, Post.Status.PUBLISHED)).data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        return Response(self.get_serializer(set_publication(self.get_object(), request.user, Post.Status.DRAFT)).data)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == 'GET':
            page = self.paginate_queryset(post.comments.select_related('user'))
            return self.get_paginated_response(CommentSerializer(page, many=True).data)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            comment = add_comment(post, request.user, serializer.validated_data['content'])
        except DjangoValidationError as error:
            raise ValidationError(error.messages)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

class CategoryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CategoryPermission]
