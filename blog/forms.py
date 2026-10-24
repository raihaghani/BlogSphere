from django import forms
from .models import Post, Comment
class PostForm(forms.ModelForm):
    def editor_fields(self):
        """Status is validated from the submit button, not rendered as a field."""
        return [field for field in self if field.name != 'status']

    class Meta:
        model = Post
        fields = ['title', 'category', 'excerpt', 'content', 'cover_image', 'status']
        widgets = {'content': forms.Textarea(attrs={'rows': 15}), 'excerpt': forms.Textarea(attrs={'rows': 3})}
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add a thoughtful perspective…'})}
