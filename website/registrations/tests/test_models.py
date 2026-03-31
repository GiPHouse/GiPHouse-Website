from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from courses.models import Course, Semester

from projects.models import Project

from registrations.models import Employee, Registration, questions

User: Employee = get_user_model()


class ModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.first_name = "Test"
        cls.last_name = "Test"
        cls.project_name = "testproject"

        cls.test_user = User.objects.create_user(
            github_id=1, first_name=cls.first_name, last_name=cls.last_name
        )

        cls.test_user_2 = User.objects.create_user(
            github_id=2,
            github_username="testuser2",
            first_name="Test",
            last_name="user2",
        )

        cls.test_semester = Semester.objects.get_or_create_current_semester()

        cls.test_project = Project.objects.create(
            name=cls.project_name,
            slug=cls.project_name,
            semester=cls.test_semester,
        )
        cls.test_project2 = Project.objects.create(
            name=f"{cls.project_name}2",
            slug=f"{cls.project_name}2",
            semester=cls.test_semester,
        )

        cls.test_registration = Registration.objects.create(
            user=cls.test_user_2,
            course=Course.objects.sdm(),
            semester=cls.test_semester,
            preference1=cls.test_project,
            dev_experience=Registration.EXPERIENCE_ADVANCED,
            partner_preference1="Test partner1",
            partner_preference2="Test partner2",
            partner_preference3="Test partner3",
            is_international=False,
        )

    def test_semester_str(self):
        self.assertEqual(
            f"{self.test_semester.get_season_display()} {self.test_semester.year}",
            str(self.test_semester),
        )

    def test_add_project(self):
        self.test_registration.add_project(self.test_project)
        self.assertEqual(self.test_registration.projects.count(), 1)
        self.test_registration.add_project(self.test_project2)
        self.assertEqual(self.test_registration.projects.count(), 2)

    def test_add_duplicate_project(self):
        self.test_registration.add_project(self.test_project)
        self.assertEqual(self.test_registration.projects.count(), 1)

    def test_registration_is_director_correct(self):
        reg = Registration.objects.create(
            user=self.test_user,
            course=Course.objects.sdm(),
            semester=self.test_semester,
            preference1=self.test_project,
            dev_experience=Registration.EXPERIENCE_ADVANCED,
            is_international=False,
        )

        self.assertTrue(reg.is_director)

    def test_registration_is_director_with_project(self):
        reg = Registration.objects.create(
            user=self.test_user,
            course=Course.objects.sdm(),
            semester=self.test_semester,
            preference1=self.test_project,
            dev_experience=Registration.EXPERIENCE_ADVANCED,
            is_international=False,
        )
        reg.projects.add(self.test_project)

        self.assertFalse(reg.is_director)

    def test_registration_is_director_with_sde(self):
        reg = Registration.objects.create(
            user=self.test_user,
            course=Course.objects.sde(),
            semester=self.test_semester,
            preference1=self.test_project,
            dev_experience=Registration.EXPERIENCE_ADVANCED,
            is_international=False,
        )

        self.assertFalse(reg.is_director)

    def test_registration_is_director_with_se_and_project(self):
        reg = Registration.objects.create(
            user=self.test_user,
            course=Course.objects.se(),
            semester=self.test_semester,
            preference1=self.test_project,
            dev_experience=Registration.EXPERIENCE_ADVANCED,
            is_international=False,
        )
        reg.projects.add(self.test_project)

        self.assertFalse(reg.is_director)

    def test_project_str(self):
        self.assertEqual(
            f"{self.project_name} ({self.test_semester})",
            str(self.test_project),
        )

    def test__match_partner_name_to_user__complete(self):
        u1 = User.objects.create_user(
            github_id=11,
            github_username="testpartner1",
            first_name="Test",
            last_name="partner 1",
        )
        registration = Registration.objects.create(
            user=u1,
            course=Course.objects.se(),
            semester=self.test_semester,
            dev_experience=Registration.EXPERIENCE_ADVANCED,
            is_international=False,
        )

        self.assertEqual(
            registration._match_partner_name_to_user("Test partner 1"), u1
        )

    def test__match_partner_name_to_user__typo(self):
        u1 = User.objects.create_user(
            github_id=11,
            github_username="testpartner1",
            first_name="Test",
            last_name="partner 1",
        )
        registration = Registration.objects.create(
            user=u1,
            course=Course.objects.se(),
            semester=self.test_semester,
            dev_experience=Registration.EXPERIENCE_ADVANCED,
            is_international=False,
        )

        self.assertEqual(
            registration._match_partner_name_to_user("Testpatrner 1"), u1
        )

    def test__match_partner_name_to_user__no_match(self):
        u1 = User.objects.create_user(
            github_id=11,
            github_username="testpartner1",
            first_name="Test",
            last_name="partner 1",
        )
        registration = Registration.objects.create(
            user=u1,
            course=Course.objects.se(),
            semester=self.test_semester,
            dev_experience=Registration.EXPERIENCE_ADVANCED,
            is_international=False,
        )

        self.assertIsNone(registration._match_partner_name_to_user("Abcdefg"))

    def test_partner_preference1_user(self):
        self.test_registration._match_partner_name_to_user = MagicMock(
            return_value=self.test_user
        )
        self.assertEqual(
            self.test_registration.partner_preference1_user, self.test_user
        )

    def test_partner_preference2_user(self):
        self.test_registration._match_partner_name_to_user = MagicMock(
            return_value=self.test_user
        )
        self.assertEqual(
            self.test_registration.partner_preference2_user, self.test_user
        )

    def test_partner_preference3_user(self):
        self.test_registration._match_partner_name_to_user = MagicMock(
            return_value=self.test_user
        )
        self.assertEqual(
            self.test_registration.partner_preference3_user, self.test_user
        )



class questionTest (TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the happy path tests
        cls.test_semester = Semester.objects.get_or_create_current_semester()
        cls.test_registration = questions.Registrations.objects.create(
            title="Test Registration", semester=cls.test_semester
        )
        cls.test_participant = Employee.objects.create_user(
            github_id=1, first_name="Test", last_name="Participant"
        )
        cls.test_submission = questions.RegistrationSubmission.objects.create(
            registration=cls.test_registration, participant=cls.test_participant)
        #TEST QUESTION TYPES
        cls.test_question_CHOICE = questions.Question.objects.create(
            registration=cls.test_registration,
            question="What is your favorite color?",
            question_type=questions.Question.CHOICE,
            optional=False
        )
        cls.test_question_TEXT = questions.Question.objects.create(
            registration=cls.test_registration,
            question="What is your name?",
            question_type=questions.Question.TEXT,
            optional=False
        )
        cls.test_question_BIGTEXT = questions.Question.objects.create(
            registration=cls.test_registration,
            question="Please describe your experience with Python:",
            question_type=questions.Question.BIGTEXT,
            optional=False
        )
        cls.test_question_MULTI = questions.Question.objects.create(
            registration=cls.test_registration,
            question="Please select all that apply:",
            question_type=questions.Question.MULTI,
            optional=False
        )
        cls.test_question_DROPDOWN = questions.Question.objects.create(
            registration=cls.test_registration,
            question="Please select your preferred option:",
            question_type=questions.Question.DROPDOWN,
            optional=False
        )
        #TEST ANSWERS models
        cls.test_answer_CHOICE = questions.Answer.objects.create(
            submission=cls.test_submission,
            question=cls.test_question_CHOICE
        )
        cls.test_answer_TEXT = questions.Answer.objects.create(
            submission=cls.test_submission,
            question=cls.test_question_TEXT
        )
        cls.test_answer_BIGTEXT = questions.Answer.objects.create(
            submission=cls.test_submission,
            question=cls.test_question_BIGTEXT
        )
        cls.test_answer_MULTI = questions.Answer.objects.create(
            submission=cls.test_submission,
            question=cls.test_question_MULTI
        )
        cls.test_answer_DROPDOWN = questions.Answer.objects.create(
            submission=cls.test_submission,
            question=cls.test_question_DROPDOWN
        )
        # TEST ANSWERS DATA
        cls.test_TextData= questions.TextData.objects.create(
            answer=cls.test_answer_TEXT,
            value="Test Participant")
        cls.test_BigTextData= questions.TextData.objects.create(
            answer=cls.test_answer_BIGTEXT,
            value="I have been programming in Python for 5 years and have experience with Django and Flask.")
        
        cls.test_questionChoice = questions.QuestionChoice.objects.create(
            question=cls.test_question_CHOICE,
            value="Blue"
        )
        cls.test_questionMulti1 = questions.QuestionChoice.objects.create(
            question=cls.test_question_MULTI,
            value="Option 1"
        )
        cls.test_questionMulti2 = questions.QuestionChoice.objects.create(
            question=cls.test_question_MULTI,
            value="Option 2"
        )

        cls.test_ChoiceData= questions.ChoiceData.objects.create(
            answer=cls.test_answer_CHOICE,
            choice=cls.test_questionChoice
        )
        cls.test_MultiData= questions.MultiData.objects.create(
            answer=cls.test_answer_MULTI,
        )
        cls.test_MultiData.choices.set([cls.test_questionMulti1, cls.test_questionMulti2])
        cls.test_DropdownData= questions.ChoiceData.objects.create(
            answer=cls.test_answer_DROPDOWN,
            choice=cls.test_questionMulti1
        )

        # Set up data for edge case tests (e.g., missing fields, invalid data types)


    def test_registration_str(self):
        self.assertEqual(
            f"{self.test_registration.title} ({self.test_semester})",
            str(self.test_registration)
        )
    
    def test_registrationsubmission_str(self):
        submission = questions.RegistrationSubmission.objects.create(
            registration=self.test_registration,
            participant=self.test_participant
        )
        self.assertEqual(
            f"{self.test_registration.title} submission by {self.test_participant} at {submission.created}",
            str(submission)
        )
    
    def test_question_str(self):
        self.assertEqual(
            "What is your favorite color?",
            str(self.test_question_CHOICE)
        )
    
    def test_answer_get(self):
        self.assertEqual(
            "Blue",
            self.test_answer_CHOICE.answer_value
        )
        self.assertEqual(
            "Test Participant",
            self.test_answer_TEXT.answer_value
        )
        self.assertEqual(
            "I have been programming in Python for 5 years and have experience with Django and Flask.",
            self.test_answer_BIGTEXT.answer_value
        )
        self.assertEqual(
            "Option 1, Option 2",
            self.test_answer_MULTI.answer_value
        )
        self.assertEqual(
            "Option 1",
            self.test_answer_DROPDOWN.answer_value
        )