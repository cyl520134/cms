# Create your views here.
import os
import uuid
from datetime import date

import mistune
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView

from cms import settings
from .models import Post, Category


class CommonViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(Category.get_category())
        return context


class PostDetailView(CommonViewMixin, DetailView):
    queryset = (Post.objects.filter(status=Post.STATUS_NORMAL)
                .select_related('category', 'owner'))
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=self.queryset)
        obj.content = mistune.markdown(obj.content)
        return obj


class PostListView(CommonViewMixin, ListView):
    template_name = 'blog/list.html'
    paginate_by = 5
    queryset = (Post.objects.filter(status=Post.STATUS_NORMAL)
                .select_related('category', 'owner')
                .only('id', 'cover_image', 'owner__username', 'title', 'desc', 'created_time', 'category__name')
                .order_by('-id'))
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加搜索相关变量的默认值
        context['keyword'] = self.request.GET.get('keyword', '')
        context['key_date'] = self.request.GET.get('key_date', '')
        context['key_category'] = self.request.GET.get('key_category', '')
        return context


class CategoryView(PostListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        context.update({
            'category': category,
        })
        return context

    def get_queryset(self):
        """重写queryset，根据分类过滤"""
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        return queryset.filter(category_id=category_id)


class SearchView(PostListView):

    def get_queryset(self):
        queryset = super().get_queryset()
        key_word = self.request.GET.get('keyword')
        key_date = self.request.GET.get('key_date')
        key_category = self.request.GET.get('key_category')

        filters = Q()

        if key_word:
            filters &= Q(title__icontains=key_word) | Q(desc__icontains=key_word)
        if key_date:
            filters &= Q(created_time__icontains=key_date)
        if key_category:
            filters &= Q(category_id=key_category)
        return queryset.filter(filters)


@login_required
@csrf_exempt
def upload_attachment(request):
    """处理附件上传的视图"""
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        # 1. 验证文件类型
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.txt']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            return JsonResponse({
                'success': 0,
                'message': f'不支持的文件类型，允许的类型：{", ".join(allowed_extensions)}'
            })

        # 2. 验证文件大小（限制为10MB）
        if file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': 0,
                'message': '文件大小不能超过10MB'
            })

        # 3. 构建保存路径（按日期分类）
        today = date.today()
        upload_dir = os.path.join('attachments', str(today.year), str(today.month))
        os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_dir), exist_ok=True)

        # 生成唯一文件名（避免重名）
        filename = f'{uuid.uuid4().hex}{ext}'
        file_path = os.path.join(upload_dir, filename)

        # 保存文件
        default_storage.save(file_path, ContentFile(file.read()))

        # 4. 返回文件URL
        file_url = f'{settings.MEDIA_URL}{file_path}'
        return JsonResponse({
            'success': 1,
            'url': file_url,
            'name': file.name  # 原始文件名
        })

    return JsonResponse({'success': 0, 'message': '无效请求'})
