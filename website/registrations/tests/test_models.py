from django.contrib.auth import get_user_model
from django.test import TestCase

from courses.models import Semester

from registrations.models import Employee

from registrations.models.registration import (
    QuestionChoice,
    Registrations,
    RegistrationSubmission,
    Question,
    Answer,
    TextData,
    ChoiceData,
    MultiData,
)

User: Employee = get_user_model()


class questionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the happy path tests
        cls.test_semester = Semester.objects.get_or_create_current_semester()
        cls.test_registration = Registrations.objects.create(
            title="Test Registration", semester=cls.test_semester
        )
        cls.test_participant = Employee.objects.create_user(
            github_id=1, first_name="Test", last_name="Participant"
        )
        cls.test_submission = RegistrationSubmission.objects.create(
            registration=cls.test_registration,
            participant=cls.test_participant,
        )
        # TEST QUESTION TYPES
        cls.test_question_CHOICE = Question.objects.create(
            registration=cls.test_registration,
            question="What is your favorite color?",
            question_type=Question.CHOICE,
            optional=False,
        )
        cls.test_question_TEXT = Question.objects.create(
            registration=cls.test_registration,
            question="What is your name?",
            question_type=Question.TEXT,
            optional=False,
        )
        cls.test_question_BIGTEXT = Question.objects.create(
            registration=cls.test_registration,
            question="Please describe your experience with Python:",
            question_type=Question.BIGTEXT,
            optional=False,
        )
        cls.test_question_MULTI = Question.objects.create(
            registration=cls.test_registration,
            question="Please select all that apply:",
            question_type=Question.MULTI,
            optional=False,
        )
        cls.test_question_DROPDOWN = Question.objects.create(
            registration=cls.test_registration,
            question="Please select your preferred option:",
            question_type=Question.DROPDOWN,
            optional=False,
        )
        # TEST ANSWERS models
        cls.test_answer_CHOICE = Answer.objects.create(
            submission=cls.test_submission, question=cls.test_question_CHOICE
        )
        cls.test_answer_TEXT = Answer.objects.create(
            submission=cls.test_submission, question=cls.test_question_TEXT
        )
        cls.test_answer_BIGTEXT = Answer.objects.create(
            submission=cls.test_submission, question=cls.test_question_BIGTEXT
        )
        cls.test_answer_MULTI = Answer.objects.create(
            submission=cls.test_submission, question=cls.test_question_MULTI
        )
        cls.test_answer_DROPDOWN = Answer.objects.create(
            submission=cls.test_submission, question=cls.test_question_DROPDOWN
        )
        # TEST ANSWERS DATA
        cls.test_TextData = TextData.objects.create(
            answer=cls.test_answer_TEXT, value="Test Participant"
        )
        cls.test_BigTextData = TextData.objects.create(
            answer=cls.test_answer_BIGTEXT,
            value="I have been programming in Python for 5 years and have experience with Django and Flask.",
        )

        cls.test_questionChoice = QuestionChoice.objects.create(
            question=cls.test_question_CHOICE, value="Blue"
        )
        cls.test_questionMulti1 = QuestionChoice.objects.create(
            question=cls.test_question_MULTI, value="Option 1"
        )
        cls.test_questionMulti2 = QuestionChoice.objects.create(
            question=cls.test_question_MULTI, value="Option 2"
        )

        cls.test_ChoiceData = ChoiceData.objects.create(
            answer=cls.test_answer_CHOICE, choice=cls.test_questionChoice
        )
        cls.test_MultiData = MultiData.objects.create(
            answer=cls.test_answer_MULTI,
        )
        cls.test_MultiData.choices.set(
            [cls.test_questionMulti1, cls.test_questionMulti2]
        )
        cls.test_DropdownData = ChoiceData.objects.create(
            answer=cls.test_answer_DROPDOWN, choice=cls.test_questionMulti1
        )

        # Set up data for edge case tests (e.g., missing fields, invalid data types)

    def test_registration_str(self):
        self.assertEqual(
            f"{self.test_registration.title} ({self.test_semester})",
            str(self.test_registration),
        )

    def test_registrationsubmission_str(self):
        submission = RegistrationSubmission.objects.create(
            registration=self.test_registration,
            participant=self.test_participant,
        )
        self.assertEqual(
            f"{self.test_registration.title} submission by {self.test_participant} at {submission.created}",
            str(submission),
        )

    def test_question_str(self):
        self.assertEqual(
            "What is your favorite color?", str(self.test_question_CHOICE)
        )

    def test_answer_get(self):
        self.assertEqual("Blue", self.test_answer_CHOICE.answer_value)
        self.assertEqual(
            "Test Participant", self.test_answer_TEXT.answer_value
        )
        self.assertEqual(
            "I have been programming in Python for 5 years and have experience with Django and Flask.",
            self.test_answer_BIGTEXT.answer_value,
        )
        self.assertEqual(
            "Option 1, Option 2", self.test_answer_MULTI.answer_value
        )
        self.assertEqual("Option 1", self.test_answer_DROPDOWN.answer_value)
