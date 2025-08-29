# blog/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from blog.models import Category, Post
from cms.custom_site import custom_site


@admin.register(Category, site=custom_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'owner', 'created_time', 'post_count')  # 页面上显示的字段
    fields = ('name', 'status')  # 增加时显示的字段
    list_per_page = 10

    # 新增字段
    def save_model(self, request, obj, form, change):
        obj.owner = request.user  # 当前已经登录的用户作为作者
        return super().save_model(request, obj, form, change)

    def post_count(self, obj):
        """ 统计文章数量 """
        return obj.post_set.count()

    post_count.short_description = '文章数量'


@admin.register(Post, site=custom_site)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'created_time', 'owner', 'operator']
    list_display_links = []
    list_filter = ['category', ]
    # 自定义页面
    change_form_template = 'admin/blog/post/post_change_form.html'
    search_fields = ['title', 'category_name']
    list_per_page = 10
    actions_on_top = True
    actions_on_bottom = False

    # 编辑页面
    save_on_top = True

    fields = (
        'title',
        'cover_image',
        'desc',
        'content',
        'category'
        # 'status'
    )

    def operator(self, obj):
        """ 新增编辑按钮 """
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=[obj.id])
        )

    operator.short_description = '操作'

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super().save_model(request, obj, form, change)
