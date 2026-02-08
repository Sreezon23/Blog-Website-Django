from django import forms
from blog_app.models import Post, Comment
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title','excerpt','text','category','tags','featured_image')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200',
                'placeholder': 'Give your post a captivating title...',
                'required': True
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200 resize-none',
                'rows': 3,
                'maxlength': '300',
                'placeholder': 'Brief summary (optional)'
            }),
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200 resize-none',
                'rows': 12,
                'placeholder': 'Start writing your story...'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200'
            }),
            'tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'hidden'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
        }
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['excerpt'].required = False
        self.fields['category'].required = False
        self.fields['tags'].required = False
        self.fields['featured_image'].required = False

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author','email','text')
        widgets = {
            'author': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200',
                'placeholder': 'Your name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200',
                'placeholder': 'Your email (optional)'
            }),
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200 resize-none',
                'rows': 4,
                'placeholder': 'Share your thoughts...'
            }),
        }
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['email'].required = False

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200',
        'placeholder': 'Enter a strong password'
    }))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200',
        'placeholder': 'Confirm password'
    }))
    class Meta:
        model = User
        fields = ('username','email','first_name','last_name')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200',
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200',
                'placeholder': 'Enter your email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200',
                'placeholder': 'First name (optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-barca-blue focus:ring-2 focus:ring-barca-blue/20 transition-all duration-200',
                'placeholder': 'Last name (optional)'
            }),
        }
    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('password'), cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned
    def clean_username(self):
        u = self.cleaned_data.get('username')
        if User.objects.filter(username=u).exists():
            raise forms.ValidationError("Username already taken!")
        return u
    def clean_email(self):
        e = self.cleaned_data.get('email')
        if User.objects.filter(email=e).exists():
            raise forms.ValidationError("Email already registered!")
        return e
