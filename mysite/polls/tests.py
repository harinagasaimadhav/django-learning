import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text="future question", pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within one day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), True)

    def test_was_published_recently_with_question_older_than_a_day(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than a day.
        """
        time = timezone.now() - datetime.timedelta(days=1, minutes=1)
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), False)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_question(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'], [question])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on the
        index page.
        """
        question = create_question(question_text="future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are available.')
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both future and past question exists. Only past should display
        :return:
        """
        past_question = create_question(question_text='Past Question', days=-20)
        future_question = create_question(question_text='future question', days=20)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'], [past_question])

    def test_two_past_question(self):
        """
        The question index page may display multiple questions
        :return:
        """
        question_1 = create_question(question_text='question 1', days=-5)
        question_2 = create_question(question_text='question 2', days=-20)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'], [question_1, question_2])


class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        :return:
        """
        future_question = create_question(question_text='future question', days=1)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        display's the question's text
        :return:
        """
        question = create_question(question_text='past question', days=-1)
        response = self.client.get(reverse('polls:detail', args=(question.id,)))
        self.assertContains(response, question.question_text)
