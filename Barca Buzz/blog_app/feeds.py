from django.contrib.syndication.views import Feed
from .models import Post

class LatestPostsFeed(Feed):
    title = "Barça Buzz — Latest"
    link = "/"
    description = "Latest posts from Barça Buzz"

    def items(self):
        return Post.objects.filter(status='published').order_by('-published_date')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or (item.text[:180] + '...')

    def item_link(self, item):
        return item.get_absolute_url()
