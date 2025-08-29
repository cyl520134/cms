import os

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from mdeditor.fields import MDTextField
from django.core.exceptions import ValidationError


# 自定义上传路径函数
def post_cover_path(instance, filename):
    """将封面图片按日期和文章ID分目录存储"""
    created_time = instance.created_time if instance.created_time else timezone.now()
    return f'post_covers/{created_time.strftime("%Y%m")}/{instance.id}/{filename}'


class Category(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(max_length=50, verbose_name='名称')
    status = models.PositiveIntegerField(choices=STATUS_ITEMS, default=STATUS_NORMAL, verbose_name='状态')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '分类'

    def __str__(self):
        return self.name

    @staticmethod
    def get_category():
        category_list = Category.objects.filter(status=Category.STATUS_NORMAL)
        return {
            "categories": category_list
        }


class Post(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除')
        # (STATUS_DRAFT, '草稿')
    )
    # 支持的图片格式
    ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    # 图片像素限制
    MAX_WIDTH = 200
    MAX_HEIGHT = 300
    title = models.CharField(max_length=200, verbose_name='文章标题')
    # 封面图片字段
    cover_image = models.ImageField(
        upload_to=post_cover_path,
        verbose_name='封面图片',
        blank=True,
        null=True,
        help_text=f'支持格式: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}, 最大5MB'
    )
    category = models.ForeignKey(Category, blank=True, null=True, verbose_name='文章分类', on_delete=models.DO_NOTHING)
    desc = models.CharField(max_length=500, verbose_name='内容摘要', default='')
    content = MDTextField()
    status = models.PositiveIntegerField(choices=STATUS_ITEMS, default=STATUS_NORMAL, verbose_name='状态')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def clean(self):
        """验证图片格式、大小和像素尺寸"""

        if self.cover_image:
            # 验证文件大小 (5MB = 5 * 1024 * 1024 bytes)
            if self.cover_image.size > 5 * 1024 * 1024:
                raise ValidationError("图片大小不能超过5MB")

            # 验证文件格式
            ext = os.path.splitext(self.cover_image.name)[1].lower()
            if ext not in self.ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError(f"不支持的图片格式，仅支持: {', '.join(self.ALLOWED_IMAGE_EXTENSIONS)}")

    class Meta:
        verbose_name = verbose_name_plural = '文章'
        ordering = ['-id']  # 根据id进行降序排序

    def __str__(self):
        return self.title


def query_posts():
    return Post.objects.filter(status=Post.STATUS_NORMAL)
