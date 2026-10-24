from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from blog.models import Category, Post, Comment

STORIES = [
    ('Technology', 'technology', 'The quiet power of simpler software', 'Great technology gives people less to manage, not more.',
     'The most useful technology often disappears into the background. A well-designed tool makes a difficult task feel ordinary. That simplicity is rarely accidental: it comes from understanding the work before choosing the technology.\n\nStart with the smallest complete workflow. Observe where users hesitate, where they repeat themselves, and where information gets lost. Improve those moments before adding another feature.\n\nSimple systems also create room for reliable operations. Fewer moving parts mean fewer failure modes, clearer ownership, and a shorter path from a reported problem to a useful fix.'),
    ('Programming', 'programming', 'Write code for the person who comes next', 'Readable code is a practical investment in the future of a team.',
     'Software spends far more time being read than being written. A useful function name explains intent. A focused module gives readers a place to look. Together, these small choices reduce the cost of every future change.\n\nTests should describe behavior rather than repeat implementation details. Start with important boundaries: who can perform an action, which inputs are valid, and what happens when a dependency fails.\n\nBefore introducing an abstraction, look for a real repeated decision. A little duplication can be easier to change than a premature framework with too many responsibilities.'),
    ('Artificial Intelligence', 'artificial-intelligence', 'A thoughtful approach to evaluating AI tools', 'Begin with a real task, a clear baseline, and a measurable definition of useful.',
     'An impressive demonstration is not an evaluation. To understand whether a tool helps, choose representative tasks and compare its results with an existing workflow. Record failures as carefully as successes.\n\nConsider correctness, latency, cost, and the time a person spends reviewing the result. A fast answer that requires extensive repair may not improve the overall process.\n\nKeep sensitive data out of experiments until the data handling and access boundaries are understood. Give reviewers enough context to challenge an answer and trace its supporting evidence.'),
    ('Cybersecurity', 'cybersecurity', 'Security begins at the permission boundary', 'A hidden button is a design choice. A backend permission check is a security control.',
     'Every state-changing request needs a clear answer to two questions: who is acting, and are they allowed to change this specific resource? Authentication answers the first. Authorization answers the second.\n\nTest ownership checks by changing identifiers directly. A user who can edit one article must not gain access to another simply by guessing its ID. Apply the same rules to browser forms and API requests.\n\nDefense also depends on ordinary maintenance: installing supported security updates, keeping credentials out of source control, and checking backups through actual recovery exercises.'),
    ('Business', 'business', 'Build a product around a problem worth solving', 'The best product brief starts with a person and a frustrating moment.',
     'A list of features is not yet a product strategy. Begin by describing the person who needs help, the task they are trying to finish, and the obstacle that makes it difficult.\n\nA small, complete workflow is easier to evaluate than a broad collection of unfinished screens. Define success before implementation: can the person finish their task, understand the result, and recover from a mistake?\n\nUse feedback to decide what comes next. Repeated confusion is stronger evidence than a speculative feature request. Sustainable products improve through careful observation and consistent execution.'),
]

class Command(BaseCommand):
    help = 'Seed repeatable development content; creates a user with an unusable password.'
    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Demo seeding is disabled when DEBUG=False.')
        author, created = User.objects.get_or_create(username='blogsphere_editorial')
        if created:
            author.set_unusable_password()
            author.save()
        for name, slug, title, excerpt, content in STORIES:
            category, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            post, _ = Post.objects.get_or_create(slug=f'demo-{slug}', defaults={
                'title': title, 'excerpt': excerpt, 'content': content, 'category': category,
                'author': author, 'cover_image': f'images/{slug}.svg', 'status': 'PUBLISHED'})
            Comment.objects.get_or_create(post=post, user=author, content='What has your experience been? Share a practical example with the community.')
        Post.objects.get_or_create(slug='demo-editorial-draft', defaults={'title': 'A field guide to better technical decisions',
            'content': 'Start with the constraints. Compare alternatives against the same criteria. Record what would make you revisit the decision.',
            'author': author, 'category': category})
        self.stdout.write(self.style.SUCCESS('Demo content ready. No reusable login credentials created.'))
