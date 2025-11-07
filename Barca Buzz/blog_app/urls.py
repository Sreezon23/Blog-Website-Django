from django.urls import path
from blog_app import views

urlpatterns = [
    # ==================== MAIN PAGES ====================
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # ==================== POST CRUD ====================
    path('post/new/', views.post_new, name='post_new'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_remove, name='post_remove'),
    path('post/<slug:slug>/publish/', views.post_publish, name='post_publish'),
    path('drafts/', views.post_draft_list, name='post_draft_list'),
    
    # ==================== POST DETAIL & LIST ====================
    path('posts/', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # ==================== COMMENTS ====================
    path('post/<slug:slug>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/<int:pk>/approve/', views.comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', views.comment_remove, name='comment_remove'),
    
    # ==================== FILTERING ====================
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    path('search/', views.search_results, name='search'),
    
    # ==================== DASHBOARDS ====================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # ==================== INTERACTIONS ====================
    path('post/<slug:slug>/like/', views.toggle_like, name='toggle_like'),
    path('post/<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
]
