from django.contrib import admin
from blog_app.models import Post, Comment, Category, Tag, AuthorProfile, PostLike, Bookmark

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','post_count','created_date')
    list_filter = ('created_date',)
    search_fields = ('name','description')
    prepopulated_fields = {'slug': ('name',)}
    def post_count(self, obj): return obj.posts.filter(status='published').count()

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name','post_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    def post_count(self, obj): return obj.posts.filter(status='published').count()

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title','author','category','status','published_date','is_featured','views_count','like_count')
    list_filter = ('status','category','tags','is_featured','published_date','created_date','author')
    search_fields = ('title','text','slug','author__username','category__name')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_date'
    ordering = ('-published_date','-created_date')
    readonly_fields = ('created_date','updated_date','views_count')
    def like_count(self, obj): return obj.likes.count()

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author','post','approved_comments','created_date')
    list_filter = ('approved_comments','created_date')
    search_fields = ('author','email','text','post__title')
    date_hierarchy = 'created_date'
    ordering = ('-created_date',)

@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user','post','created')
    list_filter = ('created',)

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user','post','created')
    list_filter = ('created',)
