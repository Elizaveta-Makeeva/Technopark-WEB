from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_protect
from .forms import LoginForm, SignUpForm, SettingsForm, AskForm, AnswerForm
from .models import Question, Answer, Tag, QuestionLike, AnswerLike
from .utils import paginate
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse


def benchmark_view(request):
    return HttpResponse("<html><body><h1>Dynamic Test</h1></body></html>")


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


@csrf_protect
@login_required
def question_detail(request, question_id):
    question = get_object_or_404(
        Question.objects.with_details().prefetch_related('tags').select_related('author__profile'),
        pk=question_id
    )
    answers = Answer.objects.for_question(question.id).filter(question=question).select_related('author__profile')
    page = paginate(answers, request)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = Answer.objects.create(
                text=form.cleaned_data['text'],
                question=question,
                author=request.user
            )
            return HttpResponseRedirect(
                f"{question.get_absolute_url()}?page={page.paginator.num_pages}#answer-{answer.id}")
    else:
        form = AnswerForm()


    question.rating = question.likes.aggregate(rating=Sum('value'))['rating'] or 0

    context = get_base_context()
    context.update({
        'question': question,
        'answers': page,
        'answers_count': answers.count(),
        'page_title': question.title,
        'form': form
    })
    return render(request, 'question.html', context)

@csrf_protect
def login(request):
    context = get_base_context()

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.POST.get('next', '')
            if next_url and next_url != 'None':
                return redirect(next_url)
            return redirect('app:index')
    else:
        form = LoginForm(request)
        initial = {'next': request.GET.get('next', '')}
        form = LoginForm(request, initial=initial)

    context['form'] = form
    return render(request, 'login.html', context)


@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('app:index')
    else:
        form = SignUpForm()

    context = get_base_context()
    context['form'] = form
    return render(request, 'signup.html', context)


@csrf_protect
def logout_view(request):
    if request.method == 'POST':
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
        auth_logout(request)
        return redirect(next_url)
    return redirect('app:index')


@login_required
@csrf_protect
def settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, user=request.user, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('app:edit')
    else:
        form = SettingsForm(user=request.user, instance=request.user.profile)

    context = get_base_context()
    context['form'] = form
    return render(request, 'settings.html', context)


@login_required
@csrf_protect
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = Question.objects.create(
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text'],
                author=request.user
            )

            tags = form.cleaned_data['tags']
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                for tag_name in tag_list:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    question.tags.add(tag)

            return redirect('app:question', question_id=question.id)
    else:
        form = AskForm()

    context = get_base_context()
    context['form'] = form
    return render(request, 'ask.html', context)


@require_POST
@login_required
def question_like(request):
    try:
        question_id = request.POST.get('question_id')
        value = int(request.POST.get('value'))

        question = Question.objects.get(pk=question_id)
        like, created = QuestionLike.objects.get_or_create(
            user=request.user,
            question=question,
            defaults={'value': value}
        )

        if not created:
            if like.value == value:
                like.delete()
            else:
                like.value = value
                like.save()

        new_rating = Question.objects.filter(pk=question_id).annotate(
            rating=Coalesce(Sum('likes__value'), Value(0))
        ).first().rating

        user_vote = QuestionLike.objects.filter(
            user=request.user,
            question=question
        ).first()

        return JsonResponse({
            'status': 'ok',
            'rating': new_rating or 0,
            'user_vote': user_vote.value if user_vote else 0
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_POST
@login_required
def answer_like(request):
    try:
        answer_id = request.POST.get('answer_id')
        value = int(request.POST.get('value'))

        answer = Answer.objects.get(pk=answer_id)
        like, created = AnswerLike.objects.get_or_create(
            user=request.user,
            answer=answer,
            defaults={'value': value}
        )

        if not created:
            if like.value == value:
                like.delete()
            else:
                like.value = value
                like.save()

        new_rating = Answer.objects.filter(pk=answer_id).annotate(
            rating=Coalesce(Sum('likes__value'), Value(0))
        ).first().rating

        user_vote = AnswerLike.objects.filter(
            user=request.user,
            answer=answer
        ).first()

        return JsonResponse({
            'status': 'ok',
            'rating': new_rating or 0,
            'user_vote': user_vote.value if user_vote else 0
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_POST
@login_required
def mark_correct_answer(request):
    question_id = request.POST.get('question_id')
    answer_id = request.POST.get('answer_id')

    try:
        question = Question.objects.get(pk=question_id, author=request.user)
        answer = Answer.objects.get(pk=answer_id, question=question)

        Answer.objects.filter(question=question).update(is_correct=False)
        answer.is_correct = True
        answer.save()

        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    questions = Question.objects.search(query)
    results = [{
        'title': q.title,
        'url': q.get_absolute_url(),
        'text': q.text[:100] + '...' if len(q.text) > 100 else q.text
    } for q in questions]

    return JsonResponse({'results': results})
