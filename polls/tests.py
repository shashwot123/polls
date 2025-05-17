from django.test import TestCase
import datetime
from django.utils import timezone
from django.urls import reverse

from .models import Question

# Create your tests here.
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_date(self):
        #add a future date to the pub_date of a question
        #returns false for a future date
        time = timezone.now() + datetime.timedelta(days = 30)
        future_question = Question(pub_date = time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_old_question(self):
        #returns false for pub_date older than 1 day
        time = timezone.now() - datetime.timedelta(days = 1, seconds = 1)
        old_question = Question(pub_date = time)
        self.assertIs(old_question.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_question(self):
        #returns true for pub_date within the last day
        time = timezone.now() - datetime.timedelta(hours = 23, minutes = 59, seconds = 59)
        recent_question = Question(pub_date = time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days = days)
    return Question.objects.create(question_text = question_text, pub_date = time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertEqual(list(response.context["latest_question_list"]), [])
    
    def test_future_question(self):
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        question = create_question(question_text = "Past Question.", days = -30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])
    
    def test_future_and_past_question(self):
        create_question(question_text="Future question.", days=30)
        question = create_question(question_text = "Past Question.", days = -30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])

    def test_two_past_questions(self):
        question1 = create_question(question_text = "Question 1", days = -30)
        question2 = create_question(question_text = "Question 2", days = -20)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question2, question1])

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        question = create_question(question_text = "Future Question", days = 5)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertEqual(response.status_code, 404)  

    def test_past_question(self):
        question = create_question(question_text = "Future Question", days = -5)
        response = self.client.get(reverse("polls:detail", args=(question.id,)))
        self.assertContains(response, question.question_text)  
