from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.shortcuts import redirect

from .models import Category, Post
from .forms import CommentForm


class PostListView(ListView):
    model = Post
    paginate_by = 2
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        queryset = Post.objects.filter(status=True)
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        author = self.request.GET.get('author')
        tag = self.request.GET.get('tag')
        date_str = self.request.GET.get('date')

        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(content__icontains=q))
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        if author:
            queryset = queryset.filter(author__profile__first_name__iexact=author)
        if tag:
            queryset = queryset.filter(tags__slug__iexact=tag)
        if date_str:
            date = parse_date(date_str)
            if date:
                queryset = queryset.filter(
                    created_at__year=date.year,
                    created_at__month=date.month,
                    created_at__day=date.day
                )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['recent_posts'] = Post.objects.filter(status=True).order_by('-created_at')[:3]
        # context['tags'] = Tag.objects.all()  # only if using taggit
        return context



class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        # Add comment form
        context['form'] = CommentForm()

        # Get approved comments
        context['comments'] = post.comments.filter(approved=True).order_by('-created_at')

        # Get previous and next posts
        context['prev_post'] = Post.objects.filter(
            status=True,
            created_at__lt=post.created_at
        ).order_by('-created_at').first()

        context['next_post'] = Post.objects.filter(
            status=True,
            created_at__gt=post.created_at
        ).order_by('created_at').first()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.save()
            return redirect(self.request.path_info)

        # If invalid form, re-render with errors
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)
