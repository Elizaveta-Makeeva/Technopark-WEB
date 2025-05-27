from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
import random
from django.db import transaction
from itertools import product


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int,)

    def handle(self, *args, **options):
        ratio = options['ratio']
        with transaction.atomic():
            users = []
            for i in range(1, ratio + 1):
                username = f'NewUser_{i}_{random.randint(1000, 9999)}'
                user = User.objects.create_user(
                    username=username,
                    email=f'user_{i}_{random.randint(1000, 9999)}@example.com',
                    password='testpass123'
                )
                Profile.objects.create(
                    user=user,
                    avatar='avatars/default.jpg',
                    nickname=f'User_{i}_{random.randint(1000, 9999)}',
                    login=f'user_{i}_{random.randint(1000, 9999)}',
                )
                users.append(user)

            all_users = users
            self.stdout.write(f"Created {len(users)} new users")

            tags = []
            for i in range(1, ratio + 1):
                tag = Tag.objects.create(name=f'Tag_{i}_{random.randint(1000, 9999)}')
                tags.append(tag)

            all_tags = tags
            self.stdout.write(f"Created {len(tags)} new tags")

            questions = []
            for i in range(1, ratio * 10 + 1):
                question = Question.objects.create(
                    title=f'New Question {i}',
                    text=f'New Question text {i}',
                    author=random.choice(all_users)
                )
                question.tags.set(random.sample(all_tags, k=random.randint(1, 3)))
                questions.append(question)

            all_questions = questions
            self.stdout.write(f"Created {len(questions)} new questions")

            answers = []
            for i in range(1, ratio * 100 + 1):
                answer = Answer.objects.create(
                    text=f'New Answer {i}',
                    question=random.choice(all_questions),
                    author=random.choice(all_users),
                    is_correct=random.choice([True, False])
                )
                answers.append(answer)

            all_answers = answers
            self.stdout.write(f"Created {len(answers)} new answers")

            existing_pairs = set(QuestionLike.objects.values_list('user_id', 'question_id'))
            all_possible_pairs = set((user.id, question.id) for user, question in product(users, questions))
            available_pairs = all_possible_pairs - existing_pairs
            max_question_likes = min(ratio * 200, len(available_pairs))
            if max_question_likes > 0:
                selected_pairs = random.sample(list(available_pairs), max_question_likes)
                question_likes_to_create = []
                for user_id, question_id in selected_pairs:
                    question_likes_to_create.append(QuestionLike(
                        user_id=user_id,
                        question_id=question_id,
                        value=random.choice([1, -1])
                    ))
                QuestionLike.objects.bulk_create(question_likes_to_create, batch_size=1000, ignore_conflicts=True)
                self.stdout.write(f"Created {len(question_likes_to_create)} new question_likes")

            existing_pairs = set(AnswerLike.objects.values_list('user_id', 'answer_id'))
            all_possible_pairs = set((user.id, answer.id) for user, answer in product(users, answers))
            available_pairs = all_possible_pairs - existing_pairs
            max_answer_likes = min(ratio * 200, len(available_pairs))
            if max_answer_likes > 0:
                selected_pairs = random.sample(list(available_pairs), max_answer_likes)
                answer_likes_to_create = []
                for user_id, answer_id in selected_pairs:
                    answer_likes_to_create.append(AnswerLike(
                        user_id=user_id,
                        answer_id=answer_id,
                        value=random.choice([1, -1])
                    ))
                AnswerLike.objects.bulk_create(answer_likes_to_create, batch_size=1000, ignore_conflicts=True)
                self.stdout.write(f"Created {len(answer_likes_to_create)} new answer_likes")