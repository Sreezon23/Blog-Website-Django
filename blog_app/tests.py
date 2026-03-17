from django.test import TestCase, Client
from django.urls import reverse
from blog_app.models import NewsletterSubscriber, GuestSubmission

class MissingFeaturesTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_barca_songs_view(self):
        response = self.client.get(reverse('barca_songs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog_app/pages/barca_songs.html')
        self.assertContains(response, 'The Barça Songs')

    def test_guest_submission_view_get(self):
        response = self.client.get(reverse('guest_submission'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog_app/pages/guest_article.html')
        self.assertContains(response, 'Submit a Guest Article')

    def test_guest_submission_view_post(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'title': 'Test Article',
            'content': 'This is a test article content.'
        }
        response = self.client.post(reverse('guest_submission'), data)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.assertEqual(GuestSubmission.objects.count(), 1)
        
        submission = GuestSubmission.objects.first()
        self.assertEqual(submission.name, 'Test User')
        self.assertFalse(submission.is_reviewed)

    def test_newsletter_subscribe(self):
        data = {'email': 'subscriber@example.com'}
        
        # Test valid subscription
        response = self.client.post(reverse('newsletter_subscribe'), data, HTTP_REFERER='/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(NewsletterSubscriber.objects.count(), 1)
