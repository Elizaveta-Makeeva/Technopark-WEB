from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Value
from django.db.models.functions import Coalesce


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    nickname = models.CharField(max_length=50)
    login = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def new(self):
        return self.with_details().order_by('-created_at')

    def hot(self):
        return self.with_details().order_by('-rating', '-created_at')

    def with_tags(self, tag_name):
        return self.with_details().filter(tags__name=tag_name)

    def with_details(self):
        return self.get_queryset().annotate(
            answers_count=Count('answers'),
            rating=Coalesce(Sum('likes__value'), Value(0))
        )

    def get_popular_tags(self):
        return Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]

    def get_best_members(self):
        return User.objects.annotate(
            num_answers=Count('answers'),
            num_questions=Count('questions')
        ).order_by('-num_answers', '-num_questions')[:10]


class AnswerManager(models.Manager):
    def for_question(self, question_id):
        return self.filter(question_id=question_id).annotate(
            rating=Coalesce(Sum('likes__value'), Value(0))
        ).order_by('-is_correct', '-rating', '-created_at')


class Question(models.Model):
    title = models.CharField(max_length=100, blank=True)
    text = models.TextField(max_length=2000, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    tags = models.ManyToManyField(Tag, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestionManager()

    def __str__(self):
        return f"{self.title[:50]}... by {self.author.username}"

    def get_rating(self):
        return self.likes.aggregate(rating=Sum('value'))['rating'] or 0

    def get_absolute_url(self):
        return f"/question/{self.id}/"

    def get_tags(self):
        return self.tags.all()

    def get_answers_count(self):
        return self.answers.count()

    class Meta:
        ordering = ['-created_at']


class Answer(models.Model):
    text = models.TextField(max_length=2000, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Answer to {self.question.title[:30]}... by {self.author.username}"

    def get_rating(self):
        return self.likes.aggregate(rating=Sum('value'))['rating'] or 0

    objects = AnswerManager()

    class Meta:
        ordering = ['-is_correct', '-created_at']


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_likes')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes')
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'question']

    def __str__(self):
        return f"{self.user.username} {'liked' if self.value > 0 else 'disliked'} {self.question.title[:30]}..."


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_likes')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'answer']

    def __str__(self):
        return f"{self.user.username} {'liked' if self.value > 0 else 'disliked'} answer to {self.answer.question.title[:30]}..."