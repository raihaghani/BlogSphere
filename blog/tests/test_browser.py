import secrets
from pathlib import Path
from django.contrib.auth.models import User, Group
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from django.test import override_settings
from playwright.sync_api import sync_playwright, expect
from blog.models import Category, Post

@override_settings(STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'}, 'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class BrowserSmokeTests(StaticLiveServerTestCase):
    """Run explicitly: python manage.py test blog.tests.test_browser."""
    def test_complete_author_and_reader_journey(self):
        call_command('setup_roles', verbosity=0)
        Category.objects.create(name='Technology', slug='technology')
        password = secrets.token_urlsafe(24)
        author = User.objects.create_user('browser_author', password=password)
        author.groups.add(Group.objects.get(name='Author'))
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={'width':1440,'height':1000})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(self.live_server_url + '/register/')
            page.get_by_label('Username').fill('browser_reader')
            page.get_by_label('Email').fill('browser@example.com')
            page.locator('input[name="password1"]').fill(password)
            page.locator('input[name="password2"]').fill(password)
            page.get_by_role('button', name='Create account').click()
            page.get_by_label('Username').fill('browser_author')
            page.locator('input[name="password"]').fill(password)
            page.get_by_role('button', name='Sign in', exact=True).click()
            page.get_by_role('link', name='My dashboard').click()
            page.set_viewport_size({'width':390,'height':844})
            self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
            page.screenshot(path='evidence/browser-dashboard-mobile.png', full_page=True)
            page.set_viewport_size({'width':1440,'height':1000})
            page.get_by_role('link', name='+ Write an article').click()
            page.set_viewport_size({'width':390,'height':844})
            self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
            page.screenshot(path='evidence/browser-editor-mobile.png', full_page=True)
            page.set_viewport_size({'width':1440,'height':1000})
            page.locator('[name="title"]').fill('A browser-tested story')
            page.locator('[name="category"]').select_option(label='Technology')
            page.locator('[name="content"]').fill('A complete publishing workflow, verified in a real browser.\n\nEvery boundary matters.')
            page.get_by_role('button', name='Save draft', exact=True).click()
            expect(page.get_by_text('A browser-tested story')).to_be_visible()
            expect(page.get_by_text('Draft', exact=True)).to_be_visible()
            page.get_by_role('link', name='Edit', exact=True).click()
            expect(page.locator('select[name="status"]')).to_have_count(0)
            page.get_by_role('button', name='Publish', exact=True).click()
            page.get_by_role('link', name='Edit', exact=True).click()
            page.get_by_role('button', name='Save draft', exact=True).click()
            expect(page.get_by_text('Draft', exact=True)).to_be_visible()
            page.get_by_role('link', name='Edit', exact=True).click()
            page.get_by_role('button', name='Publish', exact=True).click()
            page.get_by_role('link', name='View', exact=True).click()
            expect(page.get_by_role('heading',name='A browser-tested story')).to_be_visible()
            page.locator('[name="content"]').fill('Verified browser comment.')
            page.get_by_role('button',name='Post comment').click()
            expect(page.get_by_text('Verified browser comment.')).to_be_visible()
            page.get_by_role('button', name='Log out').click()
            page.get_by_role('link',name='Sign in',exact=True).click()
            page.get_by_label('Username').fill('browser_reader')
            page.locator('input[name="password"]').fill(password)
            page.get_by_role('button',name='Sign in',exact=True).click()
            expect(page.get_by_role('link', name='My dashboard')).to_have_count(0)
            Path('evidence').mkdir(exist_ok=True)
            page.screenshot(path='evidence/browser-desktop.png', full_page=True)
            for width in [390, 768]:
                page.set_viewport_size({'width':width,'height':844})
                self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
                page.screenshot(path=f'evidence/browser-{width}.png',full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            page.get_by_role('button',name='Menu',exact=True).click()
            expect(page.get_by_role('button',name='Log out')).to_be_visible()
            self.assertEqual(errors, [])
            browser.close()
