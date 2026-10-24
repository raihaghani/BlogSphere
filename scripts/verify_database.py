"""Verify ORM relationships inside a transaction that is always rolled back."""
import contextlib
import io
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ['USE_SQLITE'] = 'False'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def main():
    try:
        import django
        django.setup()
        from django.contrib.auth.models import User, Group
        from django.db import connection, transaction
        from django.db.models.deletion import ProtectedError
        from blog.models import Category, Post, Comment
        from blog.services import set_publication, add_comment
        checks = []
        with transaction.atomic():
            marker = uuid.uuid4().hex
            author = User.objects.create_user('verify_' + marker)
            author.groups.add(Group.objects.get(name='Author'))
            category = Category.objects.create(name='Verification ' + marker, slug='verify-' + marker)
            post = Post.objects.create(title='Transactional verification', content='Temporary verification content.', author=author, category=category)
            post = set_publication(post, author, 'PUBLISHED')
            comment = add_comment(post, author, 'Temporary verification comment.')
            assert Post.objects.select_related('author', 'category').get(pk=post.pk).author_id == author.pk
            assert Comment.objects.get(pk=comment.pk).post_id == post.pk
            checks.append('PASS: PostgreSQL User/Category/Post/Comment relationships and writes.')
            timestamp = post.published_at
            assert set_publication(post, author, 'PUBLISHED').published_at == timestamp
            post = set_publication(post, author, 'DRAFT')
            assert not Post.objects.published().filter(pk=post.pk).exists()
            checks.append('PASS: PostgreSQL publication retry, preserved timestamp, and draft filtering.')
            try:
                category.delete()
                raise AssertionError('Category protection failed')
            except ProtectedError:
                checks.append('PASS: Referenced category deletion protected.')
            comment_id = comment.pk
            post.delete()
            assert not Comment.objects.filter(pk=comment_id).exists()
            checks.append('PASS: Post deletion cascades its comments.')
            assert connection.connection.pgconn.ssl_in_use
            transaction.set_rollback(True)
        assert not User.objects.filter(username='verify_' + marker).exists()
        checks.append('PASS: Verification transaction rolled back; no smoke-test accounts/content persisted.')
        print('\n'.join(checks))
        return 0
    except Exception as error:
        print(f'FAILED: Database verification ({type(error).__name__}); sensitive details suppressed.')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
