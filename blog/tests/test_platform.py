from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, Client, override_settings
from rest_framework.test import APIClient
from blog.models import Category, Post, Comment
from blog.services import set_publication

@override_settings(STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'}, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class PlatformTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('setup_roles', verbosity=0)
        cls.author = User.objects.create_user('writer', 'writer@example.com', 'Test-password-714!')
        cls.author.groups.add(Group.objects.get(name='Author'))
        cls.other = User.objects.create_user('other', password='Test-password-714!')
        cls.other.groups.add(Group.objects.get(name='Author'))
        cls.reader = User.objects.create_user('reader', 'reader@example.com', 'Test-password-714!')
        cls.staff = User.objects.create_user('staff', password='Test-password-714!', is_staff=True)
        cls.category = Category.objects.create(name='Technology', slug='technology')
        cls.draft = Post.objects.create(title='Secret draft', content='Hidden knowledge', author=cls.author, category=cls.category)
        cls.post = Post.objects.create(title='Django craftsmanship', content='Useful Python patterns', excerpt='Build carefully',
                                      author=cls.author, category=cls.category, status='PUBLISHED')

    def setUp(self):
        self.api = APIClient()

    def payload(self, **changes):
        return dict(title='A new story', content='A meaningful article.', category=self.category.pk, **changes)

    def test_registration_reader_and_password_hash(self):
        response = self.client.post('/register/', {'username':'newreader','email':'NEW@Example.com', 'password1':'Uncommon-password-875!', 'password2':'Uncommon-password-875!', 'role':'Author'})
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newreader')
        self.assertEqual(user.email, 'new@example.com')
        self.assertTrue(user.check_password('Uncommon-password-875!'))
        self.assertEqual(list(user.groups.values_list('name', flat=True)), ['Reader'])

    def test_duplicate_registration(self):
        for username, email in [('reader','fresh@example.com'), ('fresh','READER@example.com')]:
            response = self.client.post('/register/', {'username':username,'email':email,'password1':'Uncommon-password-875!','password2':'Uncommon-password-875!'})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['form'].errors)

    def test_password_confirmation(self):
        response = self.client.post('/register/', {'username':'new','email':'n@example.com','password1':'Uncommon-password-875!','password2':'different'})
        self.assertIn('password2', response.context['form'].errors)

    def test_login_and_safe_redirect(self):
        response = self.client.post('/login/', {'username':'writer','password':'Test-password-714!', 'next':'https://evil.example/'})
        self.assertRedirects(response, '/')

    def test_invalid_login(self):
        response = self.client.post('/login/', {'username':'writer','password':'wrong'})
        self.assertTrue(response.context['form'].errors)

    def test_logout_requires_post(self):
        self.client.force_login(self.author)
        self.assertEqual(self.client.get('/logout/').status_code, 405)
        self.assertEqual(self.client.post('/logout/').status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_roles_idempotent(self):
        call_command('setup_roles', verbosity=0)
        self.assertEqual(Group.objects.filter(name__in=['Reader','Author']).count(), 2)
        self.assertEqual(Group.objects.get(name='Author').permissions.count(), 4)

    def test_reader_dashboard_denied(self):
        self.client.force_login(self.reader)
        self.assertEqual(self.client.get('/dashboard/').status_code, 403)
        self.assertEqual(self.client.post('/dashboard/posts/create/', self.payload()).status_code, 403)

    def test_author_dashboard_is_private(self):
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get('/dashboard/'), 'Secret draft')

    def test_web_create_draft_and_publish(self):
        self.client.force_login(self.author)
        for status in ['DRAFT','PUBLISHED']:
            self.assertEqual(self.client.post('/dashboard/posts/create/', self.payload(status=status)).status_code, 302)
        self.assertEqual(Post.objects.filter(title='A new story').count(), 2)

    def test_web_edit_owner(self):
        self.client.force_login(self.author)
        self.assertEqual(self.client.post(f'/dashboard/posts/{self.draft.pk}/edit/', self.payload(status='DRAFT')).status_code, 302)
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.title, 'A new story')

    def test_editor_has_only_status_submit_buttons(self):
        self.client.force_login(self.author)
        for url in ['/dashboard/posts/create/', f'/dashboard/posts/{self.draft.pk}/edit/']:
            response = self.client.get(url)
            self.assertNotContains(response, 'id_status')
            self.assertContains(response, 'name="status" value="PUBLISHED"', count=1)
            self.assertContains(response, 'name="status" value="DRAFT"', count=1)

    def test_editor_buttons_change_existing_status(self):
        self.client.force_login(self.author)
        url = f'/dashboard/posts/{self.draft.pk}/edit/'
        original_slug = self.draft.slug
        timestamp = None
        for status in ['PUBLISHED', 'DRAFT', 'PUBLISHED']:
            response = self.client.post(url, self.payload(status=status))
            self.assertEqual(response.status_code, 302)
            self.draft.refresh_from_db()
            self.assertEqual(self.draft.status, status)
            self.assertEqual(self.draft.slug, original_slug)
            timestamp = timestamp or self.draft.published_at
            self.assertEqual(self.draft.published_at, timestamp)
        self.assertEqual(Post.objects.count(), 2)

    def test_editor_invalid_status_or_content_does_not_save(self):
        self.client.force_login(self.author)
        url = f'/dashboard/posts/{self.draft.pk}/edit/'
        for data in [self.payload(), self.payload(status='INVALID'),
                     {**self.payload(status='PUBLISHED'), 'content': '   '}]:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['form'].errors)
            self.assertContains(response, 'role="alert"')
            self.draft.refresh_from_db()
            self.assertEqual(self.draft.status, 'DRAFT')
            self.assertEqual(self.draft.title, 'Secret draft')

    def test_web_nonowner_cannot_edit_delete_publish(self):
        self.client.force_login(self.other)
        for action in ['edit','delete','publish','unpublish']:
            self.assertEqual(self.client.post(f'/dashboard/posts/{self.draft.pk}/{action}/', self.payload()).status_code, 404)

    def test_web_delete_confirmation_and_cascade(self):
        Comment.objects.create(post=self.post, user=self.reader, content='Thoughtful')
        self.client.force_login(self.author)
        url = f'/dashboard/posts/{self.post.pk}/delete/'
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertFalse(Comment.objects.exists())
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_drafts_hidden_everywhere(self):
        for url in ['/', '/?q=Hidden', '/categories/technology/', '/api/posts/', '/api/posts/?search=Hidden']:
            self.assertNotContains(self.client.get(url), 'Secret draft')
        self.assertEqual(self.client.get(f'/posts/{self.draft.slug}/').status_code, 404)
        self.assertEqual(self.api.get(f'/api/posts/{self.draft.pk}/').status_code, 404)

    def test_published_detail_and_escaped_content(self):
        self.post.content = '<script>alert(1)</script>'
        self.post.save()
        response = self.client.get(f'/posts/{self.post.slug}/')
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')

    def test_search_all_fields(self):
        for term in ['django','PYTHON','carefully','']:
            self.assertContains(self.client.get('/', {'q':term}), self.post.title)
            self.assertEqual(self.api.get('/api/posts/', {'search':term}).data['count'], 1)

    def test_category_filter(self):
        Category.objects.create(name='Business', slug='business')
        self.assertNotContains(self.client.get('/categories/business/'), self.post.title)
        self.assertEqual(self.api.get('/api/posts/?category=business').data['count'], 0)
        self.assertEqual(self.client.get('/categories/missing/').status_code, 404)

    def test_pagination_keeps_filters(self):
        for i in range(11):
            Post.objects.create(title=f'Python {i}', content='Python', category=self.category, author=self.author, status='PUBLISHED')
        response = self.client.get('/?q=Python&category=technology')
        self.assertContains(response, 'q=Python&amp;category=technology&amp;page=2')
        self.assertEqual(len(self.api.get('/api/posts/').data['results']), 9)

    def test_title_and_content_boundaries(self):
        self.api.force_authenticate(self.author)
        for title, content, expected in [('', 'text',400), ('x'*200,'text',201),('x'*201,'text',400),('valid','   ',400)]:
            data = self.payload()
            data.update(title=title,content=content)
            self.assertEqual(self.api.post('/api/posts/', data).status_code, expected)

    def test_invalid_category_and_status(self):
        self.api.force_authenticate(self.author)
        for field, value in [('category',99999),('status','INVALID'),('cover_image','https://bad.example/')]:
            data = self.payload(); data[field] = value
            self.assertEqual(self.api.post('/api/posts/',data).status_code,400)

    def test_unique_stable_slugs(self):
        other = Post.objects.create(title=self.draft.title, content='text', author=self.author, category=self.category)
        self.assertNotEqual(other.slug, self.draft.slug)
        original = other.slug
        other.title = 'Different title'; other.save()
        self.assertEqual(other.slug, original)

    def test_publish_retry_and_unpublish(self):
        published = set_publication(self.draft, self.author, 'PUBLISHED')
        timestamp = published.published_at
        self.assertEqual(set_publication(published, self.author, 'PUBLISHED').published_at, timestamp)
        set_publication(published, self.author, 'DRAFT')
        self.assertEqual(self.api.get(f'/api/posts/{published.pk}/').status_code,404)
        self.assertEqual(set_publication(published, self.author, 'PUBLISHED').published_at, timestamp)

    def test_category_protected(self):
        from django.db.models.deletion import ProtectedError
        with self.assertRaises(ProtectedError): self.category.delete()

    def test_duplicate_category_slug(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(name='Other category',slug='technology')

    def test_api_anonymous_and_reader_create_denied(self):
        self.assertEqual(self.api.post('/api/posts/', self.payload()).status_code,403)
        self.api.force_authenticate(self.reader)
        self.assertEqual(self.api.post('/api/posts/', self.payload()).status_code,403)
        self.assertEqual(self.api.post(f'/api/posts/{self.post.pk}/publish/').status_code,403)

    def test_api_author_ignores_forged_identity(self):
        self.api.force_authenticate(self.author)
        response = self.api.post('/api/posts/', self.payload(author=self.other.pk))
        self.assertEqual(response.status_code,201)
        self.assertEqual(Post.objects.get(pk=response.data['id']).author,self.author)

    def test_api_owner_patch_draft_retry(self):
        self.api.force_authenticate(self.author)
        for _ in range(2):
            self.assertEqual(self.api.patch(f'/api/posts/{self.draft.pk}/', {'title':'Revised'}).status_code,200)
        self.assertEqual(Post.objects.count(),2)

    def test_api_nonowner_write_denied(self):
        self.api.force_authenticate(self.other)
        url = f'/api/posts/{self.draft.pk}/'
        self.assertEqual(self.api.patch(url, {'title':'Hijacked'}).status_code,404)
        self.assertEqual(self.api.delete(url).status_code,404)
        self.assertEqual(self.api.post(url+'publish/').status_code,404)

    def test_api_owner_publish_unpublish(self):
        self.api.force_authenticate(self.author)
        url = f'/api/posts/{self.draft.pk}/'
        self.assertEqual(self.api.post(url+'publish/').data['status'],'PUBLISHED')
        self.assertEqual(self.api.get(url).status_code,200)
        self.assertEqual(self.api.post(url+'unpublish/').data['status'],'DRAFT')
        self.assertEqual(self.api.get(url).status_code,404)

    def test_api_delete_and_missing_resource(self):
        self.api.force_authenticate(self.author)
        url = f'/api/posts/{self.draft.pk}/'
        self.assertEqual(self.api.delete(url).status_code,204)
        self.assertEqual(self.api.delete(url).status_code,404)
        self.assertEqual(self.api.get('/api/posts/999999/').status_code,404)

    def test_staff_not_unrestricted(self):
        self.api.force_authenticate(self.staff)
        self.assertEqual(self.api.patch(f'/api/posts/{self.post.pk}/', {'title':'No'}).status_code,403)
        self.assertEqual(self.api.post('/api/categories/', {'name':'No','slug':'no'}).status_code,403)

    def test_admin_permissions(self):
        self.staff.user_permissions.add(Permission.objects.get(codename='change_post'), Permission.objects.get(codename='add_category'))
        self.api.force_authenticate(self.staff)
        self.assertEqual(self.api.patch(f'/api/posts/{self.draft.pk}/', {'title':'Moderated'}).status_code,200)
        self.assertEqual(self.api.post('/api/categories/', {'name':'Science','slug':'science'}).status_code,201)

    def test_author_cannot_access_admin(self):
        self.client.force_login(self.author)
        self.assertEqual(self.client.get('/admin/').status_code,302)

    def test_comment_authenticated_and_assigned(self):
        self.api.force_authenticate(self.reader)
        response = self.api.post(f'/api/posts/{self.post.pk}/comments/', {'content':'Useful perspective', 'user':self.author.pk})
        self.assertEqual(response.status_code,201)
        self.assertEqual(Comment.objects.get().user,self.reader)
        self.assertEqual(self.api.get(f'/api/posts/{self.post.pk}/comments/').data['count'],1)

    def test_comment_boundaries(self):
        self.api.force_authenticate(self.reader)
        for content, expected in [('',400),('  ',400),('x'*2000,201),('x'*2001,400)]:
            self.assertEqual(self.api.post(f'/api/posts/{self.post.pk}/comments/',{'content':content}).status_code,expected)

    def test_comments_on_draft_and_anonymous_denied(self):
        self.assertEqual(self.api.post(f'/api/posts/{self.post.pk}/comments/',{'content':'Hello'}).status_code,403)
        self.api.force_authenticate(self.reader)
        self.assertEqual(self.api.post(f'/api/posts/{self.draft.pk}/comments/',{'content':'Hello'}).status_code,404)
        self.assertEqual(self.api.get(f'/api/posts/{self.draft.pk}/comments/').status_code,404)

    def test_web_comment(self):
        self.client.force_login(self.reader)
        self.assertEqual(self.client.post(f'/posts/{self.post.slug}/',{'content':'Web comment'}).status_code,302)
        self.assertEqual(Comment.objects.get().content,'Web comment')

    def test_csrf_web_and_session_api(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.author)
        self.assertEqual(client.post('/logout/').status_code,403)
        self.assertEqual(client.post('/api/posts/', self.payload()).status_code,403)
        client.get('/dashboard/posts/create/')
        token = client.cookies['csrftoken'].value
        self.assertEqual(client.post('/api/posts/',self.payload(),HTTP_X_CSRFTOKEN=token).status_code,201)
