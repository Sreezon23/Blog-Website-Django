from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#DC143C')
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_posts', kwargs={'slug': self.slug})

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag_posts', kwargs={'slug': self.slug})

class Post(models.Model):
    STATUS_CHOICES = (('draft','Draft'),('published','Published'),('archived','Archived'))
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    excerpt = models.TextField(max_length=300, blank=True, null=True)
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    featured_image = models.ImageField(upload_to='featured_images/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)
    views_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-published_date','-created_date']
        indexes = [models.Index(fields=['slug']), models.Index(fields=['status','published_date'])]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure slug is unique
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def publish(self):
        self.status = 'published'
        self.published_date = timezone.now()
        self.save()

    def archive(self):
        self.status = 'archived'
        self.save()

    def approve_comments(self):
        return self.comments.filter(approved_comments=True)

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comments = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_date']

    def approve(self):
        self.approved_comments = True
        self.save()

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.post.slug})

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"

class AuthorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author_profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    twitter = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    telegram = models.URLField(blank=True)
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class PostLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user','post')

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user','post')
