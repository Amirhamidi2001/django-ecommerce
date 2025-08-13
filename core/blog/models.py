from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from taggit.managers import TaggableManager

User = get_user_model()


class Category(models.Model):
    """
    Represents a category for blog posts.
    """

    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"
        # verbose_name = "Categorie"

    def __str__(self):
        """Returns the string representation of the category name."""
        return self.name


class Post(models.Model):
    """
    Represents a blog post.
    """

    title = models.CharField(max_length=200)
    # slug = models.SlugField(unique=True, max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=0)
    content = models.TextField()
    image = models.ImageField(
        upload_to="blog/", default="blog/default.jpg", null=True, blank=True
    )
    category = models.ManyToManyField(Category)
    tags = TaggableManager()
    counted_views = models.IntegerField(default=0)
    login_require = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Returns the string representation of the post title."""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a specific post."""
        return reverse("blog:single", kwargs={"pid": self.pk})


class Comment(models.Model):
    """
    Represents a comment on a blog post.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    comment = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Returns a string representation of the comment along with commenter's name and post title."""
        return f"Comment by {self.name} on {self.post.title}"
