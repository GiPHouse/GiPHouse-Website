# import logging
from unittest.mock import MagicMock, patch

from django.contrib import messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import Client, TestCase
from django.utils import timezone

from courses.models import Course, Semester

from projects.models import Project

from registrations.admin import UserAdminProjectFilter, UserAdminSemesterFilter
from registrations.models import Employee, Registration

User: Employee = get_user_model()


class RegistrationAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Course.objects.create(name="Software Engineering")
        Course.objects.create(name="System Development Management")
        Course.objects.create(name="Software Development Entrepreneurship")

        cls.admin_password = "hunter2"
        cls.admin = User.objects.create_superuser(
            github_id=0, github_username="super"
        )

        cls.course = Course.objects.sdm()

        cls.courseSE = Course.objects.se()

        cls.semester = Semester.objects.get_or_create_current_semester()
        cls.semester.registration_start = timezone.now() - timezone.timedelta(
            days=30
        )
        cls.semester.registration_end = timezone.now() + timezone.timedelta(
            days=30
        )
        cls.semester.save()

        cls.project = Project.objects.create(
            name="GiPHouse1234",
            slug="giphouse1234",
            description="Test",
            semester=cls.semester,
        )
        cls.project2 = Project.objects.create(
            name="4321aProject",
            slug="4321aproject",
            description="Test",
            semester=cls.semester,
        )

        cls.manager = User.objects.create(
            github_id=1,
            github_username="manager",
            first_name="Man",
            last_name="Ager",
            student_number="s1234567",
        )

        cls.registration = Registration.objects.create(
            user=cls.manager,
            semester=cls.semester,
            dev_experience=Registration.EXPERIENCE_BEGINNER,
            preference1=cls.project,
            partner_preference1="Partner name",
            course=cls.course,
            comments="comment",
            is_international=False,
        )
        cls.registration.add_project(cls.project)

        cls.user = User.objects.create(
            github_id=2,
            github_username="lol",
            first_name="First",
            last_name="Last",
            student_number="s1234568",
        )

        cls.registration2 = Registration.objects.create(
            user=cls.user,
            semester=cls.semester,
            dev_experience=Registration.EXPERIENCE_BEGINNER,
            preference1=cls.project,
            course=cls.course,
            is_international=False,
        )

        cls.manager2 = User.objects.create(
            github_id=3,
            github_username="lmao",
            first_name="Mr",
            last_name="Bond",
            student_number="s007",
        )

        cls.registration3 = Registration.objects.create(
            user=cls.manager2,
            semester=cls.semester,
            dev_experience=Registration.EXPERIENCE_BEGINNER,
            preference1=cls.project,
            course=cls.course,
            is_international=False,
        )
        cls.registration3.add_project(cls.project)
        cls.registration3.add_project(cls.project2)

        cls.userNoReg = User.objects.create(
            github_id=9,
            github_username="hahaha",
            first_name="No",
            last_name="Registration",
            student_number="s009",
        )

        cls.userNoPreference = User.objects.create(
            github_id=10,
            github_username="dontmind",
            first_name="No",
            last_name="Preference",
            student_number="s010",
        )

        cls.registration4 = Registration.objects.create(
            user=cls.userNoPreference,
            semester=cls.semester,
            dev_experience=Registration.EXPERIENCE_BEGINNER,
            course=cls.course,
            is_international=False,
        )

        cls.message = {
            "date_joined_0": "2000-12-01",
            "date_joined_1": "12:00:00",
            "initial-date_joined_0": "2000-12-01",
            "initial-date_joined_1": "12:00:00",
            "github_id": 4,
            "github_username": "bob",
            "student_number": "s0000000",
            "registration_set-TOTAL_FORMS": 1,
            "registration_set-INITIAL_FORMS": 0,
            "registration_set-MIN_NUM_FORMS": 0,
            "registration_set-MAX_NUM_FORMS": 1,
            "registration_set-0-preference1": cls.project.id,
            "registration_set-0-semester": cls.semester.id,
            "registration_set-0-course": cls.course.id,
            "registration_set-0-projects": [cls.project.id],
            "registration_set-0-dev_experience": Registration.EXPERIENCE_BEGINNER,
            "registration_set-0-git_experience": Registration.EXPERIENCE_BEGINNER,
            "registration_set-0-scrum_experience": Registration.EXPERIENCE_BEGINNER,
            "registration_set-0-management_interest": False,
            "_save": "Save",
        }

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.admin)

    def test_get_changelist(self):
        response = self.client.get(
            reverse("admin:registrations_employee_changelist"), follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_get_form(self):
        response = self.client.get(
            reverse(
                "admin:registrations_employee_change", args=[self.manager.id]
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_form_save(self):
        response = self.client.post(
            reverse("admin:registrations_employee_add"),
            self.message,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(User.objects.get(student_number="s0000000"))

    def test_student_change_list_without_registration(self):
        response = self.client.get(
            reverse(
                "admin:registrations_employee_change", args=[self.user.pk]
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_get_user_changelist_semesterfilter(self):
        response = self.client.get(
            reverse("admin:registrations_employee_changelist"),
            data={UserAdminSemesterFilter.parameter_name: self.semester.id},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_get_user_changelist_projectfilter(self):
        response = self.client.get(
            reverse("admin:registrations_employee_changelist"),
            data={
                f"{UserAdminProjectFilter.field_name}__{UserAdminProjectFilter.field_pk}__exact": self.project.id
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_student_number_csv_export(self):
        response = self.client.post(
            reverse("admin:registrations_employee_changelist"),
            {
                ACTION_CHECKBOX_NAME: [self.user.pk],
                "action": "export_student_numbers",
                "index": 0,
            },
        )

        self.assertContains(
            response, '"First name","Last name","Student number"'
        )
        self.assertContains(
            response,
            f'"{self.user.first_name}","{self.user.last_name}","{self.user.student_number}"',
        )
        self.assertEqual(response.status_code, 200)

    def test_registration_csv_export(self):
        response = self.client.post(
            reverse("admin:registrations_employee_changelist"),
            {
                ACTION_CHECKBOX_NAME: [self.manager.pk],
                "action": "export_registrations",
                "index": 0,
            },
        )
        self.assertContains(
            response,
            (
                '"First name","Last name","Student number","GitHub username",'
                '"Course","1st project preference","2nd project preference","3rd project preference",'
                '"1st partner preference","2nd partner preference","3rd partner preference",'
                '"Dev Experience","Git Experience","Scrum Experience","Management Interest",'
                '"Non-dutch","Available during scheduled timeslot 1",'
                '"Available during scheduled timeslot 2","Available during scheduled timeslot 3",'
                '"Available during scheduled timeslot 4","Available during scheduled timeslot 5",'
                '"Available during scheduled timeslot 6","Available during scheduled timeslot 7",'
                '"Available during scheduled timeslot 8","Available during scheduled timeslot 9",'
                '"Available during scheduled timeslot 10",'
                '"Has problems with signing an NDA","Registration Comments"'
            ),
        )
        self.assertContains(
            response,
            (
                f'"{self.manager.first_name}",'
                f'"{self.manager.last_name}",'
                f'"{self.manager.student_number}",'
                f'"{self.manager.github_username}",'
                f'"{self.registration.course}",'
                f'"{self.registration.preference1}",'
                f'"",'
                f'"",'
                f'"{self.registration.partner_preference1}",'
                f'"",'
                f'"",'
                f'"{self.registration.dev_experience}",'
                f'"{self.registration.dev_experience}",'
                f'"{self.registration.dev_experience}",'
                '"False",'
                f'"{self.registration.is_international}",'
                f'"{self.registration.available_during_scheduled_timeslot_1}",'
                f'"{self.registration.available_during_scheduled_timeslot_2}",'
                f'"{self.registration.available_during_scheduled_timeslot_3}",'
                f'"{self.registration.available_during_scheduled_timeslot_4}",'
                f'"{self.registration.available_during_scheduled_timeslot_5}",'
                f'"{self.registration.available_during_scheduled_timeslot_6}",'
                f'"{self.registration.available_during_scheduled_timeslot_7}",'
                f'"{self.registration.available_during_scheduled_timeslot_8}",'
                f'"{self.registration.available_during_scheduled_timeslot_9}",'
                f'"{self.registration.available_during_scheduled_timeslot_10}",'
                f'"{self.registration.has_problems_with_signing_an_nda}",'
                f'"{self.registration.comments}"'
            ),
        )

    def test_unassign_project(self):
        response = self.client.post(
            reverse("admin:registrations_employee_changelist"),
            {
                ACTION_CHECKBOX_NAME: [
                    self.manager.pk,
                    self.user.pk,
                    self.manager2.pk,
                ],
                "action": "unassign_from_project",
                "index": 0,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.registration.refresh_from_db()
        self.registration2.refresh_from_db()
        self.registration3.refresh_from_db()
        self.assertFalse(self.registration.has_projects())
        self.assertFalse(self.registration2.has_projects())
        self.assertFalse(self.registration3.has_projects())

    def test_import_csv__get(self):
        response = self.client.get(reverse("admin:import"), follow=True)
        self.assertEqual(response.status_code, 200)

    @patch("registrations.admin.ImportAssignmentAdminView.handle_csv")
    def test_import_csv__post(self, mock_handle_csv):
        test_csv_file = SimpleUploadedFile(
            "csv_file.csv", b"123456,test,abcdef", content_type="text/csv"
        )
        response = self.client.post(
            reverse("admin:import"),
            {"csv_file": test_csv_file, "semester": self.semester.pk},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        mock_handle_csv.assert_called_once()

    @patch("registrations.admin.ImportAssignmentAdminView.handle_csv")
    def test_import_csv__post_no_csv_file(self, mock_handle_csv):
        messages.error = MagicMock()
        test_csv_file = SimpleUploadedFile(
            "csv_file.png", b"123456,test,abcdef", content_type="text/csv"
        )
        response = self.client.post(
            reverse("admin:import"),
            {"csv_file": test_csv_file, "semester": self.semester.pk},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages.error.assert_called_once()
        mock_handle_csv.assert_not_called()

    @patch("registrations.admin.ImportAssignmentAdminView.handle_csv")
    def test_import_csv__post_file_too_big(self, mock_handle_csv):
        messages.error = MagicMock()
        file_content = 20000000 * b"test"
        test_csv_file = SimpleUploadedFile(
            "csv_file.csv", file_content, content_type="text/csv"
        )
        response = self.client.post(
            reverse("admin:import"),
            {"csv_file": test_csv_file, "semester": self.semester.pk},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        messages.error.assert_called_once()
        mock_handle_csv.assert_not_called()

    @patch(
        "registrations.admin.ImportAssignmentAdminView.handle_csv",
        **{"return_value.raiseError.side_effect": ValueError()},
    )
    def test_import_csv__post_file_error_handling(self, mock_handle_csv):
        messages.error = MagicMock()
        test_csv_file = SimpleUploadedFile(
            "csv_file.csv", b"123456,test,abcdef", content_type="text/csv"
        )
        response = self.client.post(
            reverse("admin:import"),
            {"csv_file": test_csv_file, "semester": self.semester.pk},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        mock_handle_csv.assert_called_once()
        messages.error.assert_called_once()

    def test_handle_csv(self):
        file_content = (
            b"First name, Last name, Student number, Course, Project name\nPiet, Janssen, s1234569, "
            b"System Development Management, GiPHouse1234"
        )
        user = User.objects.create(
            github_id=1234567,
            github_username="abcdefghij",
            first_name="Piet",
            last_name="Janssen",
            student_number="s1234569",
        )
        registration = Registration.objects.create(
            user=user,
            semester=self.semester,
            dev_experience=Registration.EXPERIENCE_BEGINNER,
            preference1=self.project,
            course=self.course,
            is_international=False,
        )

        test_csv_file = SimpleUploadedFile(
            "csv_file.csv", file_content, content_type="text/csv"
        )
        response = self.client.post(
            reverse("admin:import"),
            {"csv_file": test_csv_file, "semester": self.semester.pk},
            follow=True,
        )
        registration.refresh_from_db()
        self.assertIn(self.project, registration.get_projects())
        self.assertEqual(response.status_code, 200)

    def test_handle_csv__already_assigned(self):
        file_content = (
            b"First name, Last name, Student number, Course, Project name\nPiet, Janssen, s1234569, "
            b"System Development Management, GiPHouse1234"
        )
        user = User.objects.create(
            github_id=1234567,
            github_username="abcdefghij",
            first_name="Piet",
            last_name="Janssen",
            student_number="s1234569",
        )
        registration = Registration.objects.create(
            user=user,
            semester=self.semester,
            dev_experience=Registration.EXPERIENCE_BEGINNER,
            preference1=self.project,
            course=self.course,
            is_international=False,
        )
        registration.add_project(self.project2)

        test_csv_file = SimpleUploadedFile(
            "csv_file.csv", file_content, content_type="text/csv"
        )
        response = self.client.post(
            reverse("admin:import"),
            {"csv_file": test_csv_file, "semester": self.semester.pk},
            follow=True,
        )
        registration.refresh_from_db()
        self.assertIn(self.project2, registration.get_projects())
        self.assertEqual(response.status_code, 200)

    def test_handle_csv__invalid_header(self):
        file_content = b"Piet, Janssen, s1234569, System Development Management, GiPHouse1234"
        user = User.objects.create(
            github_id=1234567,
            github_username="abcdefghij",
            first_name="Piet",
            last_name="Janssen",
            student_number="s1234569",
        )
        registration = Registration.objects.create(
            user=user,
            semester=self.semester,
            dev_experience=Registration.EXPERIENCE_BEGINNER,
            preference1=self.project,
            course=self.course,
            is_international=False,
        )

        test_csv_file = SimpleUploadedFile(
            "csv_file.csv", file_content, content_type="text/csv"
        )
        response = self.client.post(
            reverse("admin:import"),
            {"csv_file": test_csv_file, "semester": self.semester.pk},
            follow=True,
        )
        registration.refresh_from_db()
        self.assertFalse(registration.has_projects())
        self.assertEqual(response.status_code, 200)

    def test_handle_csv__nonexistent_project(self):
        file_content = (
            b"First name, Last name, Student number, Course, Project name\nPiet, Janssen, s1234569, "
            b"System Development Management, NonExistingProject"
        )
        user = User.objects.create(
            github_id=1234567,
            github_username="abcdefghij",
            first_name="Piet",
            last_name="Janssen",
            student_number="s1234569",
        )
        registration = Registration.objects.create(
            user=user,
            semester=self.semester,
            dev_experience=Registration.EXPERIENCE_BEGINNER,
            preference1=self.project,
            course=self.course,
            is_international=False,
        )

        test_csv_file = SimpleUploadedFile(
            "csv_file.csv", file_content, content_type="text/csv"
        )
        response = self.client.post(
            reverse("admin:import"),
            {"csv_file": test_csv_file, "semester": self.semester.pk},
            follow=True,
        )
        registration.refresh_from_db()
        self.assertFalse(registration.has_projects())
        self.assertEqual(response.status_code, 200)

    def test_handle_csv__no_project(self):
        file_content = (
            b"First name, Last name, Student number, Course, Project name\nPiet, Janssen, s1234569, "
            b"System Development Management,"
        )
        user = User.objects.create(
            github_id=1234567,
            github_username="abcdefghij",
            first_name="Piet",
            last_name="Janssen",
            student_number="s1234569",
        )
        registration = Registration.objects.create(
            user=user,
            semester=self.semester,
            dev_experience=Registration.EXPERIENCE_BEGINNER,
            preference1=self.project,
            course=self.course,
            is_international=False,
        )

        test_csv_file = SimpleUploadedFile(
            "csv_file.csv", file_content, content_type="text/csv"
        )
        response = self.client.post(
            reverse("admin:import"),
            {"csv_file": test_csv_file, "semester": self.semester.pk},
            follow=True,
        )
        registration.refresh_from_db()
        self.assertFalse(registration.has_projects())
        self.assertEqual(response.status_code, 200)

    def test_handle_csv__nonexistent_user(self):
        file_content = (
            b"First name, Last name, Student number, Course, Project name\nPiet, Janssen, s1234569, "
            b"System Development Management, GiPHouse1234"
        )
        user = User.objects.create(
            github_id=1234567,
            github_username="abcdefghij",
            first_name="Piet",
            last_name="Janssen",
            student_number="s0000000",
        )
        registration = Registration.objects.create(
            user=user,
            semester=self.semester,
            dev_experience=Registration.EXPERIENCE_BEGINNER,
            preference1=self.project,
            course=self.course,
            is_international=False,
        )

        test_csv_file = SimpleUploadedFile(
            "csv_file.csv", file_content, content_type="text/csv"
        )
        response = self.client.post(
            reverse("admin:import"),
            {"csv_file": test_csv_file, "semester": self.semester.pk},
            follow=True,
        )
        registration.refresh_from_db()
        self.assertFalse(registration.has_projects())
        self.assertEqual(response.status_code, 200)

    def test_convert_timeslots(self):
        from registrations.admin import UserAdmin

        user_admin = UserAdmin(User, None)
        
        # Test with multiple timeslots
        self.assertEqual(
            user_admin.convert_timeslots("available during scheduled timeslot 1, available during scheduled timeslot 2"),
            [True, True, False, False, False, False, False, False, False, False]
        )
        
        # Test with single timeslot
        self.assertEqual(
            user_admin.convert_timeslots("available during scheduled timeslot 2"),
            [False, True, False, False, False, False, False, False, False, False]
        )
        
        # Test with timeslot 5
        self.assertEqual(
            user_admin.convert_timeslots("available during scheduled timeslot 5"),
            [False, False, False, False, True, False, False, False, False, False]
        )
        
        # Test with timeslot 10
        self.assertEqual(
            user_admin.convert_timeslots("available during scheduled timeslot 10"),
            [False, False, False, False, False, False, False, False, False, True]
        )
        
        # Test with multiple non-consecutive timeslots
        self.assertEqual(
            user_admin.convert_timeslots("available during scheduled timeslot 1, available during scheduled timeslot 5, available during scheduled timeslot 10"),
            [True, False, False, False, True, False, False, False, False, True]
        )
        
        # Test with empty string
        self.assertEqual(
            user_admin.convert_timeslots(""),
            [False, False, False, False, False, False, False, False, False, False]
        )


