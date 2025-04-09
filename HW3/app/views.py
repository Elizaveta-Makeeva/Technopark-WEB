from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Question, Answer, Tag
from .utils import paginate


def get_base_context():
    return {
        'popular_tags': Question.objects.get_popular_tags(),
        'best_members': Question.objects.get_best_members(),
    }


def index(request):
    questions = Question.objects.new().prefetch_related('tags').select_related('author__profile')
    page = paginate(questions, request)
    context = get_base_context()
    context.update({'questions': page, 'page_title': 'New Questions'})
    return render(request, 'index.html', context)


def hot(request):
    questions = Question.objects.hot().prefetch_related('tags').select_related('author__profile')
    page = paginate(questions, request)
    context = get_base_context()
    context.update({'questions': page, 'page_title': 'Hot Questions'})
    return render(request, 'index.html', context)


def tag(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.with_tags(tag_name).prefetch_related('tags').select_related('author__profile')
    page = paginate(questions, request)
    context = get_base_context()
    context.update({
        'questions': page,
        'tag_name': tag_name,
        'page_title': f'Questions tagged "{tag_name}"'
    })
    return render(request, 'tag.html', context)


def question_detail(request, question_id):
    question = get_object_or_404(
        Question.objects.with_details().prefetch_related('tags').select_related('author__profile'), pk=question_id)
    answers = Answer.objects.for_question(question.id).filter(question=question).select_related('author__profile')
    page = paginate(answers, request)
    context = get_base_context()
    context.update({
        'question': question,
        'answers': page,
        'answers_count': answers.count(),
        'page_title': question.title
    })
    return render(request, 'question.html', context)


def ask(request):
    context = get_base_context()
    return render(request, 'ask.html', context)


def login(request):
    context = get_base_context()
    return render(request, 'login.html', context)


def signup(request):
    context = get_base_context()
    return render(request, 'signup.html', context)


def settings(request):
    context = get_base_context()
    return render(request, 'settings.html', context)