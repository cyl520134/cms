# Create your views here.
from django.shortcuts import render
from .models import Post, Category


def category_post_list(request, category_id=None):
    # 获取所有分类用于侧边栏显示
    categories = Category.objects.all()

    # 如果指定了分类ID，则筛选该分类下的文章
    if category_id:
        posts = Post.objects.filter(category_id=category_id)
        current_category = Category.objects.get(id=category_id)
    else:
        # 否则显示所有文章-按时间倒排
        posts = Post.objects.all()
        current_category = None

    context = {
        'categories': categories,
        'posts': posts,
        'current_category': current_category,
    }

    context.update(Category.get_category())
    return render(request, 'blog/oldHistory/demo-search.html', context)


def post_detail(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        post = None

    context = {
        "post": post
    }
    context.update(Category.get_category())
    return render(request, 'blog/detail.html', context)
