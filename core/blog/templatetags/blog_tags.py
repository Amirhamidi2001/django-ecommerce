from django import template
from blog.models import Post

register = template.Library()


@register.inclusion_tag("blog/blog_latest_posts.html")
def latest_posts(count=6):
    """
    Returns the latest published posts.
    """
    latest_posts = Post.objects.filter(status=True).order_by("-published_at")[:count]
    return {"latest_posts": latest_posts}
