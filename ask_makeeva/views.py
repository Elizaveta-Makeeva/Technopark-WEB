from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import random

popular_tags_list = ['JavaScript', 'Kubernetes', 'SQL', 'Docker', 'ES6', 'Performance', 'Algorithms', 'Big-O']
best_members_list = ['CodeWizard42', 'DataGuru', 'React', 'SQLMaster', 'DevOpsQueen', 'Algorithmist', 'StackOverflower']

questions_db = {}
answers_db = {}


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page


def initialize_data():
    if not questions_db:
        for i in range(1, 51):
            num_tags = random.randint(1, 3)
            question_tags = random.sample(popular_tags_list, num_tags)
            answers_count = random.randint(0, 10)

            questions_db[i] = {
                'title': f"Question title {i} about {', '.join(question_tags)}",
                'id': i,
                'text': f"Question text {i} about {', '.join(question_tags)}",
                'answers_count': answers_count,
                'tags': question_tags,
                'rating': random.randint(-5, 20),
                'author': {
                    'name': f"Author{i}",
                    'avatar': f"avatar{i}.jpg"
                }
            }

            answers_db[i] = [
                {
                    'text': f"Answer {j} to question {i}. Detailed solution here.",
                    'rating': random.randint(-2, 10),
                    'is_correct': j == 1,
                    'author': {
                        'name': f'ExpertUser{j}',
                        'avatar': f'avatar_answer{j}.jpg'
                    }
                } for j in range(1, answers_count + 1)
            ]


initialize_data()


def index(request):
    page = paginate(list(questions_db.values()), request, per_page=20)
    context = {
        'questions': page,
        'user': {
            'name': 'Dr. Pepper',
            'avatar': 'hello.jpg'
        },
        'popular_tags': popular_tags_list,
        'best_members': best_members_list,
    }
    return render(request, 'index.html', context)


def hot(request):
    sorted_questions = sorted(questions_db.values(), key=lambda x: x['rating'], reverse=True)
    page = paginate(sorted_questions, request, per_page=20)

    context = {
        'questions': page,
        'user': {
            'name': 'Dr. Pepper',
            'avatar': 'hello.jpg'
        },
        'popular_tags': popular_tags_list,
        'best_members': best_members_list,
    }
    return render(request, 'index.html', context)


def question(request, question_id):
    question_id = int(question_id)
    question_data = questions_db[question_id]
    answers = answers_db.get(question_id, [])
    page = paginate(answers_db.get(question_id, []), request, per_page=30)

    context = {
        'question': question_data,
        'answers': page,
        'answers_count': len(answers),
        'user': {
            'name': 'Dr. Pepper',
            'avatar': 'hello.jpg'
        },
        'popular_tags': popular_tags_list,
        'best_members': best_members_list
    }
    return render(request, 'question.html', context)


def tag(request, tag_name):
    questions = [q for q in questions_db.values() if tag_name in q['tags']]
    page = paginate(questions, request, per_page=20)

    context = {
        'questions': page,
        'tag_name': tag_name,
        'user': {'name': 'Dr. Pepper', 'avatar': 'hello.jpg'},
        'popular_tags': popular_tags_list,
        'best_members': best_members_list
    }
    return render(request, 'tag.html', context)


def login(request):
    context = {
        'error': 'Sorry, wrong password!',
        'popular_tags': ['JavaScript', 'Kubernetes', 'SQL', 'Docker', 'ES6', 'Performance', 'Algorithms', 'Big-O'],
        'best_members': ['CodeWizard42', 'DataGuru', 'React', 'SQLMaster', 'DevOpsQueen', 'Algorithmist',
                         'StackOverflower']
    }
    return render(request, 'login.html', context)


def signup(request):
    context = {
        'error': 'Fill in all fields, please!',
        'is_logged_in': False,
        'popular_tags': ['JavaScript', 'Kubernetes', 'SQL', 'Docker', 'ES6', 'Performance', 'Algorithms', 'Big-O'],
        'best_members': ['CodeWizard42', 'DataGuru', 'React', 'SQLMaster', 'DevOpsQueen', 'Algorithmist',
                         'StackOverflower']
    }
    return render(request, 'signup.html', context)


def ask(request):
    context = {
        'error': 'Fill in all fields, please!',
        'user': {
            'name': 'Dr. Pepper',
            'avatar': 'hello.jpg'
        },
        'popular_tags': ['JavaScript', 'Kubernetes', 'SQL', 'Docker', 'ES6', 'Performance', 'Algorithms', 'Big-O'],
        'best_members': ['CodeWizard42', 'DataGuru', 'React', 'SQLMaster', 'DevOpsQueen', 'Algorithmist',
                         'StackOverflower']
    }
    return render(request, 'ask.html', context)


def settings(request):
    context = {
        'user': {
            'name': 'Dr. Pepper',
            'avatar': 'hello.jpg',
            'email': 'drpepper@mail.ru'
        },
        'popular_tags': ['JavaScript', 'Kubernetes', 'SQL', 'Docker', 'ES6', 'Performance', 'Algorithms', 'Big-O'],
        'best_members': ['CodeWizard42', 'DataGuru', 'React', 'SQLMaster', 'DevOpsQueen', 'Algorithmist',
                         'StackOverflower']
    }
    return render(request, 'settings.html', context)