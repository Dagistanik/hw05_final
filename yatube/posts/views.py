from django.shortcuts import redirect, render, get_object_or_404
from yatube.settings import PAGE_NUM
from posts.models import Post, Group, User, Follow
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from posts.forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    posts = Post.objects.all()
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    title = str(group)
    description = group.description
    paginator = Paginator(posts, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    context = {
        'description': description,
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


def profile(request, username):
    username = get_object_or_404(User, username=username)
    posts = username.posts.all()
    paginator = Paginator(posts, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts_num = posts.count()
    title = 'Профайл пользователя ' + str(username.get_full_name())
    following = Follow.objects.filter(author=username).exists()
    context = {
        'username': username,
        'title': title,
        'posts_num': posts_num,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_num = post.author.posts.all().count()
    title = str(post)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'posts_num': posts_num,
        'title': title,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
@csrf_exempt
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    groups = Group.objects.all()
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', form.author)
    context = {
        'form': form,
        'groups': groups,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    groups = Group.objects.all()
    if form.is_valid():
        form = form.save(False)
        form.author = request.user
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
        'groups': groups,
    }
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        for comm in post.comments.all():
            print(comm.text)
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    title = 'Авторы, на которых подписан пользователь'
    follow = Follow.objects.filter(user=request.user)
    following_author = User.objects.filter(following__in=follow)
    post_list = Post.objects.filter(author__in=following_author)
    paginator = Paginator(post_list, PAGE_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts = Post.objects.all()
    context = {
        'title': title,
        'page_obj': page_obj,
        'posts': posts,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписка на автора"""
    user = get_object_or_404(User, username=request.user.username)
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора"""
    get_object_or_404(
        Follow, user=request.user, author__username=username).delete()
    return redirect('posts:profile', username=username)
