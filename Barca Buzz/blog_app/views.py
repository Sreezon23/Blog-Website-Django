from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count
from django.contrib import messages
from .models import Post, Comment, Category, Tag
from .forms import PostForm, CommentForm


# ================== STATIC / SIMPLE PAGES ==================

def home(request):
    """Homepage: Displays recent and trending posts."""
    categories = Category.objects.all()
    recent_posts = Post.objects.filter(status='published').order_by('-published_date')[:9]

    # Trending = Most viewed posts in the last 14 days
    window = timezone.now() - timezone.timedelta(days=14)
    trending_posts = Post.objects.filter(
        status='published',
        published_date__gte=window
    ).order_by('-views_count', '-published_date')[:5]

    context = {
        'categories': categories,
        'recent_posts': recent_posts,
        'trending_posts': trending_posts,
    }
    return render(request, 'blog_app/pages/home.html', context)


def about(request):
    """About page."""
    return render(request, 'blog_app/pages/about.html')


# ================== POST CRUD ==================

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "Post created successfully!")
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog_app/posts/post_form.html', {'form': form})


@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog_app/posts/post_form.html', {'form': form})


@login_required
def post_remove(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.delete()
    messages.warning(request, "Post deleted successfully!")
    return redirect('home')


@login_required
def post_publish(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.status = 'published'
    post.published_date = timezone.now()
    post.save()
    messages.info(request, "Post published successfully!")
    return redirect('post_detail', slug=slug)


def post_draft_list(request):
    drafts = Post.objects.filter(status='draft').order_by('-created_date')
    return render(request, 'blog_app/posts/post_draft_list.html', {'drafts': drafts})


def post_list(request):
    """List all published posts"""
    posts = Post.objects.filter(status='published').order_by('-published_date')
    return render(request, 'blog_app/posts/post_list.html', {'posts': posts})


# ================== POST DETAIL ==================

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    post.views_count += 1
    post.save(update_fields=['views_count'])

    comments = post.comments.filter(approved=True)
    related_posts = Post.objects.filter(
        tags__in=post.tags.all(),
        status='published'
    ).exclude(id=post.id).distinct()[:4]

    is_liked = request.user.is_authenticated and post.likes.filter(id=request.user.id).exists()
    is_bookmarked = request.user.is_authenticated and post.bookmarks.filter(id=request.user.id).exists()

    return render(request, 'blog_app/posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'is_liked': is_liked,
        'is_bookmarked': is_bookmarked,
    })


# ================== COMMENTS ==================

@login_required
def add_comment_to_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect('post_detail', slug=slug)
    else:
        form = CommentForm()
    return render(request, 'blog_app/posts/comment_form.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approved = True
    comment.save()
    return redirect('post_detail', slug=comment.post.slug)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    slug = comment.post.slug
    comment.delete()
    return redirect('post_detail', slug=slug)


# ================== FILTERING ==================

def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published').order_by('-published_date')
    return render(request, 'blog_app/category_posts.html', {'category': category, 'posts': posts})


def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag, status='published').order_by('-published_date')
    return render(request, 'blog_app/tag_posts.html', {'tag': tag, 'posts': posts})


def search_results(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query),
        status='published'
    ).distinct() if query else []
    return render(request, 'blog_app/search_results.html', {'posts': posts, 'query': query})


# ================== DASHBOARDS ==================

def dashboard(request):
    """Route to appropriate dashboard based on user role"""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return admin_dashboard(request)
        else:
            return user_dashboard(request)
    return redirect('login')


@login_required
def user_dashboard(request):
    user_posts = Post.objects.filter(author=request.user)
    return render(request, 'blog_app/dashboards/user_dashboard.html', {'user_posts': user_posts})


@login_required
def admin_dashboard(request):
    posts = Post.objects.all().order_by('-published_date')
    total_posts = posts.count()
    total_comments = Comment.objects.count()
    total_categories = Category.objects.count()
    return render(request, 'blog_app/dashboards/admin_dashboard.html', {
        'posts': posts,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_categories': total_categories,
    })


# ================== INTERACTIONS (LIKES & BOOKMARKS) ==================

@login_required
def toggle_like(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})


@login_required
def toggle_bookmark(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user in post.bookmarks.all():
        post.bookmarks.remove(request.user)
        bookmarked = False
    else:
        post.bookmarks.add(request.user)
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked})
