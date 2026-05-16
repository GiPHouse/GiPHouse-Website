from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import Client, TestCase
from django.utils import timezone

from courses.models import Course, Semester

from registrations.models import Employee, registration, Registrations, Question, QuestionChoice
from registrations.admin import RegistrationsAdmin

User: Employee = get_user_model()


class RedirectTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_base_url_redirects_to_step_1(self):
        response = self.client.get("/register/")

        self.assertRedirects(
            response,
            reverse("registrations:step1"),
            fetch_redirect_response=False,
        )


class Step1Test(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.test_user = User.objects.create_user(github_id=0)
        cls.test_user.backend = ""

    def setUp(self):
        self.client = Client()

    def test_step1(self):
        semester = Semester.objects.get_or_create_current_semester()
        semester.registration_start = timezone.now()
        semester.registration_end = timezone.now() + timezone.timedelta(days=1)
        semester.save()

        response = self.client.get("/register/step1")

        self.assertEqual(response.status_code, 200)

    def test_step1_authenticated(self):
        semester = Semester.objects.get_or_create_current_semester()
        semester.registration_start = timezone.now()
        semester.registration_end = timezone.now() + timezone.timedelta(days=1)
        semester.save()

        self.client.force_login(self.test_user)

        response = self.client.get("/register/step1")
        self.assertFalse(response.context["user"].is_authenticated)

    def test_step1_no_semester(self):
        """Uncomment a branch of the dispatch() method of
        the Step1View Class for this test to pass."""

        response = self.client.get("/register/step1", follow=True)

        self.assertRedirects(response, reverse("home"))
        self.assertContains(response, "Registrations are currently not open")

    def test_step1_semester_without_registrations(self):
        """Uncomment a branch of the dispatch() method of
         the Step1View Class for this test to pass."""

        Semester.objects.get_or_create_current_semester()

        response = self.client.get("/register/step1", follow=True)

        self.assertRedirects(response, reverse("home"))
        self.assertContains(response, "Registrations are currently not open")

    def test_step1_current_semester_closed_registration(self):
        """Uncomment a branch of the dispatch() method of
        the Step1View Class for this test to pass."""

        semester = Semester.objects.get_or_create_current_semester()
        semester.registration_start = timezone.now() - timezone.timedelta(
            days=2
        )
        semester.registration_end = timezone.now() - timezone.timedelta(days=1)
        semester.save()

        response = self.client.get("/register/step1", follow=True)

        self.assertRedirects(response, reverse("home"))
        self.assertContains(response, "Registrations are currently not open")

    def test_step1_old_semester_open_registration(self):
        Semester.objects.create(
            year=2017,
            season=Semester.SPRING,
            registration_start=timezone.now(),
            registration_end=timezone.now() + timezone.timedelta(days=1),
        )

        response = self.client.get("/register/step1", follow=True)

        self.assertEqual(response.status_code, 200)


class Step2Test(TestCase):
    @classmethod
    def setUpTestData(cls):
        Course.objects.create(name="Software Engineering")
        cls.se = Course.objects.se()

        # Semester should have a registration period set,
        # but we do not check for registrations being open
        # at the moment. Sample registration does not specify
        # the registration period either.
        cls.semester = Semester.objects.get_or_create_current_semester()

        # cls.semester.registration_end = timezone.now() + timezone.timedelta(days=1)
        # cls.semester.save()

        # create sample registration
        site = AdminSite()
        admin = RegistrationsAdmin(Registrations, site)
        # the request parameter is not used inside
        # the function, so None should work
        admin.create_sample_registration(None)

        cls.q_ids_start = Question.objects.all().first().pk

        cls.first_name = "FirstTest"
        cls.last_name = "LastTest"
        cls.email = "test@test.com"
        cls.github_username = "test"
        cls.github_id = 1
        cls.student_number = "s1234567"

        cls.dev_exp_question_id = Question.objects.filter(
            question="Dev Experience" # not optimal
        ).first().pk
        # choose any of the options, say, the first one
        cls.dev_experience = QuestionChoice.objects.filter(
            question_id=cls.dev_exp_question_id,
        ).first().value # right now it would be = "None"

        # you could access them the same filtering way
        # but Ima just go with what they are: hardcoded
        cls.project_preference1 = "Project A"
        cls.project_preference2 = "Project B"
        cls.project_preference3 = "Project C"

        cls.project_partner_preference1 = "Piet Janssen"
        cls.project_partner_preference2 = "FirstTest LastTest"
        cls.project_partner_preference3 = "Einstein"

        cls.available_during_scheduled_timeslots = [1, 2, 3, 10]

        cls.management_interest = "No"
        cls.non_dutch = "Yes"
        cls.problem_with_NDA = "No"

        timeslot_q_id = Question.objects.filter(
            question="Timeslot availability"  # semi-optimal
        ).first().pk
        cls.availability_ids_start = QuestionChoice.objects.filter(
            question_id=timeslot_q_id,
        ).first().id

    def setUp(self):
        self.client = Client()

        self.session = self.client.session
        self.session["github_id"] = self.github_id
        self.session["github_username"] = self.github_username
        self.session["github_email"] = self.email
        self.session["github_name"] = f"{self.first_name} {self.last_name}"

        self.session.save()

        # All questions must be answered;
        # This is a sample payload, the values are based on
        # the human-readable attributes defined above
        self.form_data_filled = {
            f"question_{self.q_ids_start}_first_name": self.first_name,
            f"question_{self.q_ids_start + 1}_last_name": self.last_name,
            f"question_{self.q_ids_start + 2}_email": self.email,
            f"question_{self.q_ids_start + 3}_student_number": self.student_number,
            f"question_{self.q_ids_start + 4}_course": QuestionChoice.objects.filter(
                question_id=self.q_ids_start + 4,
                value=self.se,  # because it's a dropdown
            ).first().pk,
            f"question_{self.q_ids_start + 5}": QuestionChoice.objects.filter(
                question_id=self.q_ids_start + 5,
                value=self.project_preference1,  # DROPDOWN
            ).first().pk,
            f"question_{self.q_ids_start + 6}": QuestionChoice.objects.filter(
                question_id=self.q_ids_start + 6,
                value=self.project_preference2,
            ).first().pk,
            f"question_{self.q_ids_start + 7}": QuestionChoice.objects.filter(
                question_id=self.q_ids_start + 7,
                value=self.project_preference3,  # DROPDOWN
            ).first().pk,
            f"question_{self.q_ids_start + 8}": self.project_partner_preference1,  # TEXT
            f"question_{self.q_ids_start + 9}": self.project_partner_preference2,
            f"question_{self.q_ids_start + 10}": self.project_partner_preference3,
            f"question_{self.q_ids_start + 11}": QuestionChoice.objects.filter(
                question_id=self.dev_exp_question_id,
                value=self.dev_experience,  # CHOICE
            ).first().pk,
            f"question_{self.q_ids_start + 12}": QuestionChoice.objects.filter(
                question_id=self.q_ids_start + 12,
                value=self.management_interest,  # CHOICE
            ).first().pk,
            f"question_{self.q_ids_start + 13}": QuestionChoice.objects.filter(
                question_id=self.q_ids_start + 13,
                value=self.non_dutch,  # CHOICE
            ).first().pk,
            f"question_{self.q_ids_start + 14}": [self.availability_ids_start + t - 1 for t in
                                                 self.available_during_scheduled_timeslots],  # offset 1
            f"question_{self.q_ids_start + 15}": QuestionChoice.objects.filter(
                question_id=self.q_ids_start + 15,
                value=self.problem_with_NDA,
            ).first().pk
            # "submit": "submit"
        }

    def test_step2(self):
        response = self.client.get("/register/step2")
        self.assertEqual(response.status_code, 200)

    def test_step2_no_github_id(self):
        del self.session["github_id"]
        self.session.save()

        response = self.client.get("/register/step2")

        self.assertEqual(response.status_code, 400)

    def test_post_step2(self):
        response = self.client.post(
            "/register/step2",
            self.form_data_filled,
            follow=True
        )

        self.assertRedirects(response, "/")
        self.assertContains(response, "Registration created successfully")

        session = self.client.session
        # check user logged in
        self.assertTrue("_auth_user_id" in session)

        # check session cleanup
        self.assertNotIn("github_id", session)
        self.assertNotIn("github_username", session)
        self.assertNotIn("github_name", session)
        self.assertNotIn("github_email", session)

    def test_post_step2_wrong_student_number(self):
        self.form_data_filled.update({
            f"question_{self.q_ids_start + 3}_student_number": "wrong format", # this one actually works lol
        })
        response = self.client.post(
            "/register/step2",
            self.form_data_filled,
            follow=True,
        )
        self.assertContains(response, "Invalid Student Number")

    # All tests below are for reference only and should be replaced
    def test_post_step2_duplicate_project(self):
        response = self.client.post(
            "/register/step2",
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "student_number": self.student_number,
                "github_id": self.github_id,
                "github_username": self.github_username,
                "course": self.se.id,
                "email": self.email,
                "dev_experience": self.dev_experience,
                "non_dutch": self.non_dutch,
                "project1": self.project_preference1.id,
                "project2": str(self.project_preference1.id),
            },
            follow=True,
        )
        self.assertContains(
            response, "You should fill in all preferences with unique values"
        )

    def test_post_step2_existing_user(self):
        existing_user = User.objects.create_user(
            github_id=self.github_id, student_number=self.student_number
        )
        registration.Registration.objects.create(
            user=existing_user,
            dev_experience=self.dev_experience,
            course_id=self.se.id,
            preference1_id=self.project_preference1.id,
            preference2_id=self.project_preference2.id,
            preference3_id=self.project_preference3.id,
            semester=Semester.objects.get_or_create_current_semester(),
        )

        response = self.client.post(
            "/register/step2",
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "student_number": self.student_number,
                "github_id": self.github_id,
                "github_username": self.github_username,
                "course": self.se.id,
                "email": self.email,
                "dev_experience": self.dev_experience,
                "non_dutch": self.non_dutch,
                "project1": self.project_preference1.id,
                "project2": self.project_preference2.id,
                "project3": self.project_preference3.id,
                "partner1": self.project_partner_preference1,
                "partner2": self.project_partner_preference2,
                "partner3": self.project_partner_preference3,
                "available_during_scheduled_timeslot_1": self.available_during_scheduled_timeslot_1,
                "available_during_scheduled_timeslot_2": self.available_during_scheduled_timeslot_2,
                "available_during_scheduled_timeslot_3": self.available_during_scheduled_timeslot_3,
            },
        )
        self.assertContains(
            response, "User already registered for this semester."
        )

    def test_post_step2_existing_user_different_semester(self):
        existing_user = User.objects.create_user(
            github_id=self.github_id, student_number=self.student_number
        )

        older_semester = Semester.objects.create(
            year=timezone.now().year - 2, season=Semester.FALL
        )

        registration.Registration.objects.create(
            user=existing_user,
            dev_experience=self.dev_experience,
            course_id=self.se.id,
            preference1_id=self.project_preference1.id,
            preference2_id=self.project_preference2.id,
            preference3_id=self.project_preference3.id,
            semester=older_semester,
            available_during_scheduled_timeslot_1=self.available_during_scheduled_timeslot_1,
            available_during_scheduled_timeslot_2=self.available_during_scheduled_timeslot_2,
            available_during_scheduled_timeslot_3=self.available_during_scheduled_timeslot_3,
            available_during_scheduled_timeslot_10=self.available_during_scheduled_timeslot_10,
        )

        response = self.client.post(
            "/register/step2",
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "student_number": self.student_number,
                "github_id": self.github_id,
                "github_username": self.github_username,
                "course": self.se.id,
                "email": self.email,
                "dev_experience": self.dev_experience,
                "git_experience": self.dev_experience,
                "scrum_experience": self.dev_experience,
                "management_interest": False,
                "non_dutch": self.non_dutch,
                "project1": self.project_preference1.id,
                "project2": self.project_preference2.id,
                "project3": self.project_preference3.id,
                "partner1": self.project_partner_preference1,
                "partner2": self.project_partner_preference2,
                "partner3": self.project_partner_preference3,
                "available_during_scheduled_timeslot_1": self.available_during_scheduled_timeslot_1,
                "available_during_scheduled_timeslot_2": self.available_during_scheduled_timeslot_2,
                "available_during_scheduled_timeslot_3": self.available_during_scheduled_timeslot_3,
            },
            follow=True,
        )
        self.assertRedirects(response, "/")
        self.assertContains(response, "Registration created successfully")

    def test_post_step2_existing_email(self):
        existing_user = User.objects.create_user(
            github_id=self.github_id,
            student_number=self.student_number,
            email=self.email,
        )
        registration.Registration.objects.create(
            user=existing_user,
            dev_experience=self.dev_experience,
            course_id=self.se.id,
            preference1_id=self.project_preference1.id,
            preference2_id=self.project_preference2.id,
            preference3_id=self.project_preference3.id,
            semester=Semester.objects.get_or_create_current_semester(),
            available_during_scheduled_timeslot_1=self.available_during_scheduled_timeslot_1,
            available_during_scheduled_timeslot_2=self.available_during_scheduled_timeslot_2,
            available_during_scheduled_timeslot_3=self.available_during_scheduled_timeslot_3,
        )

        self.session["github_id"] += 1
        self.session.save()

        response = self.client.post(
            "/register/step2",
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "student_number": self.student_number,
                "github_id": self.github_id + 1,
                "github_username": self.github_username,
                "dev_experience": self.dev_experience,
                "non_dutch": self.non_dutch,
                "course": self.se.id,
                "email": self.email,
                "project1": self.project_preference1.id,
                "project2": self.project_preference2.id,
                "project3": self.project_preference3.id,
                "partner1": self.project_partner_preference1,
                "partner2": self.project_partner_preference2,
                "partner3": self.project_partner_preference3,
                "available_during_scheduled_timeslot_1": self.available_during_scheduled_timeslot_1,
                "available_during_scheduled_timeslot_2": self.available_during_scheduled_timeslot_2,
                "available_during_scheduled_timeslot_3": self.available_during_scheduled_timeslot_3,
            },
            follow=True,
        )
        self.assertContains(response, "Email address already in use")

    def test_post_step2_existing_student_number(self):
        existing_user = User.objects.create_user(
            github_id=self.github_id,
            student_number=self.student_number,
            email="non-existent@test.invalid",
        )
        registration.Registration.objects.create(
            user=existing_user,
            dev_experience=self.dev_experience,
            course_id=self.se.id,
            preference1_id=self.project_preference1.id,
            preference2_id=self.project_preference2.id,
            preference3_id=self.project_preference3.id,
            semester=Semester.objects.get_or_create_current_semester(),
            available_during_scheduled_timeslot_1=self.available_during_scheduled_timeslot_1,
            available_during_scheduled_timeslot_2=self.available_during_scheduled_timeslot_2,
            available_during_scheduled_timeslot_3=self.available_during_scheduled_timeslot_3,
        )

        self.session["github_id"] += 1
        self.session.save()

        response = self.client.post(
            "/register/step2",
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "student_number": self.student_number,
                "github_id": self.github_id + 1,
                "github_username": self.github_username,
                "dev_experience": self.dev_experience,
                "git_experience": self.dev_experience,
                "scrum_experience": self.dev_experience,
                "management_interest": False,
                "non_dutch": self.non_dutch,
                "course": self.se.id,
                "email": self.email,
                "project1": self.project_preference1.id,
                "project2": self.project_preference2.id,
                "project3": self.project_preference3.id,
                "partner1": self.project_partner_preference1,
                "partner2": self.project_partner_preference2,
                "partner3": self.project_partner_preference3,
                "available_during_scheduled_timeslot_1": self.available_during_scheduled_timeslot_1,
                "available_during_scheduled_timeslot_2": self.available_during_scheduled_timeslot_2,
                "available_during_scheduled_timeslot_3": self.available_during_scheduled_timeslot_3,
            },
            follow=True,
        )
        self.assertContains(response, "Student Number already in use.")

    def test_step2_works_with_no_last_name(self):
        self.session["github_name"] = f"{self.first_name}"
        self.session.save()
        response = self.client.post(
            "/register/step2",
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "student_number": self.student_number,
                "github_id": self.github_id,
                "github_username": self.github_username,
                "semester": self.semester.id,
                "course": self.se.id,
                "email": self.email,
                "dev_experience": self.dev_experience,
                "git_experience": self.dev_experience,
                "scrum_experience": self.dev_experience,
                "management_interest": False,
                "non_dutch": self.non_dutch,
                "project1": self.project_preference1.id,
                "project2": self.project_preference2.id,
                "project3": self.project_preference3.id,
                "partner1": self.project_partner_preference1,
                "partner2": self.project_partner_preference2,
                "partner3": self.project_partner_preference3,
                "available_during_scheduled_timeslot_1": self.available_during_scheduled_timeslot_1,
                "available_during_scheduled_timeslot_2": self.available_during_scheduled_timeslot_2,
                "available_during_scheduled_timeslot_3": self.available_during_scheduled_timeslot_3,
                "available_during_scheduled_timeslot_10": self.available_during_scheduled_timeslot_10,
            },
            follow=True,
        )
        self.assertRedirects(response, "/")
        self.assertContains(response, "Registration created successfully")

    def test_post_step2_with_warning_no_ignore(self):
        response = self.client.post(
            "/register/step2",
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "student_number": self.student_number,
                "github_id": self.github_id,
                "github_username": self.github_username,
                "semester": self.semester.id,
                "course": self.se.id,
                "email": self.email,
                "dev_experience": self.dev_experience,
                "git_experience": self.dev_experience,
                "scrum_experience": self.dev_experience,
                "management_interest": False,
                "non_dutch": self.non_dutch,
                "project1": self.project_preference1.id,
                "project2": self.project_preference2.id,
                "project3": self.project_preference3.id,
                "partner1": self.project_partner_preference1,
                "partner2": self.project_partner_preference2,
                "partner3": self.project_partner_preference3,
                "available_during_scheduled_timeslot_1": True,
                "available_during_scheduled_timeslot_2": True,
                "available_during_scheduled_timeslot_3": True,
            },
            follow=True,
        )
        self.assertContains(
            response,
            "You are only available for less than 4 scheduled timeslots",
        )

    def test_post_step2_wrong_email(self):
        response = self.client.post(
            "/register/step2",
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "student_number": self.student_number,
                "github_id": self.github_id,
                "github_username": self.github_username,
                "course": self.se.id,
                "email": f"{self.student_number}@student.ru.nl",
                "dev_experience": self.dev_experience,
                "git_experience": self.dev_experience,
                "scrum_experience": self.dev_experience,
                "management_interest": False,
                "background": "background",
                "project1": self.project_preference1.id,
                "project2": self.project_preference2.id,
                "project3": self.project_preference3.id,
                "available_during_scheduled_timeslot_1": self.available_during_scheduled_timeslot_1,
                "available_during_scheduled_timeslot_2": self.available_during_scheduled_timeslot_2,
                "available_during_scheduled_timeslot_3": self.available_during_scheduled_timeslot_3,
            },
            follow=True,
        )
        self.assertContains(response, "Non-existent email address.")

    def test_post_step2_wrong_email2(self):
        response = self.client.post(
            "/register/step2",
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "student_number": self.student_number,
                "github_id": self.github_id,
                "github_username": self.github_username,
                "course": self.se.id,
                "email": f"{self.student_number}@ru.nl",
                "dev_experience": self.dev_experience,
                "git_experience": self.dev_experience,
                "scrum_experience": self.dev_experience,
                "management_interest": False,
                "background": "background",
                "project1": self.project_preference1.id,
                "project2": self.project_preference2.id,
                "project3": self.project_preference3.id,
                "available_during_scheduled_timeslot_1": self.available_during_scheduled_timeslot_1,
                "available_during_scheduled_timeslot_2": self.available_during_scheduled_timeslot_2,
                "available_during_scheduled_timeslot_3": self.available_during_scheduled_timeslot_3,
            },
            follow=True,
        )
        self.assertContains(response, "Non-existent email address.")
