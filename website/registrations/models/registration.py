from difflib import SequenceMatcher

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.functional import cached_property
#from django.core.exceptions import ValidationError

from courses.models import Course, Semester

from projects.models import Project

from registrations.models import Employee

User: Employee = get_user_model()


class RegistrationManager(models.Manager):
    """Manager for the Registration model."""

    def current_registration(self):
        """Get first registration of the current semester."""
        return self.filter(
            semester=Semester.objects.get_or_create_current_semester()
        ).first()


"Change name to Registration after removing registration.py and its dependencies."


class Registrations(models.Model):
    """A group of questions."""

    title = models.CharField(max_length=200)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    projects = models.ManyToManyField(Project, blank=True)

    objects = RegistrationManager()

    def __str__(self):
        """Return title + semester."""
        return f"{self.title} ({self.semester})"
    
    def clean(self):
        """Make sure all labels that must be set are present in the questions"""
        
        if not self.pk:
            return

        # required_labels = {
        #     label
        #     for (label, _, must_be_set) in Question.QUESTION_LABELS
        #     if must_be_set
        # }

        # used_labels = set(
        #     self.question_set.values_list("label", flat=True)
        # )

        # missing = required_labels - used_labels
        # if missing:
        #     raise ValidationError(
        #         {"questions": f"Missing required labels: {', '.join(missing)}"}
        #     )
        
    def get_projects(self):
        """Get all the projects of a registration."""
        return self.projects.all()

    def has_projects(self):
        """Returns true if there is at least one project."""
        return self.projects.all().count() != 0

    def remove_projects(self):
        """Remove all the projects of a registration."""
        return self.projects.set([])

    def add_project(self, value):
        """Set the projects of a registration."""
        self.projects.add(value)



class RegistrationSubmission(models.Model):
    """Submission of a Registration by a user."""

    registration = models.ForeignKey(Registrations, on_delete=models.CASCADE)
    #Change participant to user after removing Registration class and its dependencies
    participant = models.ForeignKey(Employee, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE)

    submitted = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    
    def get_answer(self, question_label):
        """Get the answer for a question with the given label."""
        answer = self.answer_set.filter(question__label=question_label).first()
        if answer is None:
            return ""
        return answer.answer_value
    
    def get_projects(self):
        """Get all the projects of a registration."""
        return self.projects.all()

    def has_projects(self):
        """Returns true if there is at least one project."""
        return self.projects.all().count() != 0

    def remove_projects(self):
        """Remove all the projects of a registration."""
        return self.projects.set([])

    def add_project(self, value):
        """Set the projects of a registration."""
        self.projects.add(value)

    @property
    def is_director(self):
        """Check if a registration is a director."""
        return (
            self.projects.all().count() == 0
            and self.course == Course.objects.sdm()
        )

    def _match_partner_name_to_user(self, name):
        """
        Match a string to a user.

        Find the most similar user name to the given name.
        """
        if name is None:
            return None

        ratios = {}
        for user in User.objects.filter(
            registration__semester=self.registration.semester
        ).all():
            ratio = SequenceMatcher(None, name, user.get_full_name()).ratio()
            if ratio > 0.5:
                ratios[user] = ratio

        if ratios:
            return max(ratios, key=lambda k: ratios[k])
        return None

    @cached_property
    def partner_preference1_user(self):
        """Get the user most similar to the first partner preference."""
        return self._match_partner_name_to_user(self.partner_preference1)

    @cached_property
    def partner_preference2_user(self):
        """Get the user most similar to the second partner preference."""
        return self._match_partner_name_to_user(self.partner_preference2)

    @cached_property
    def partner_preference3_user(self):
        """Get the user most similar to the third partner preference."""
        return self._match_partner_name_to_user(self.partner_preference3)

    def __str__(self):
        """Return string representation of the submission."""
        return f"{self.registration.title} submission by {self.participant} at {self.created}"


class Question(models.Model):
    "Question for the registration form."

    TEXT = "text"
    CHOICE = "choice"
    MULTI = "multi"
    BIGTEXT = "bigtext"
    DROPDOWN = "dropdown"

    QUESTION_TYPES = [
        (TEXT, "Text"),
        (BIGTEXT, "Big text"),
        (CHOICE, "Single choice"),
        (MULTI, "Multiple choice"),
        (DROPDOWN, "Dropdown"),
    ]

    FIRSTNAME   = "first_name"
    LASTNAME    = "last_name"
    EMAIL       = "email"
    GITHUB_USERNAME = "github_username"
    GITHUB_ID   = "github_id"
    STUDENT_NUMBER = "student_number"
    COURSE     = "course"

    PROJECT1    = "project1"
    PROJECT2    = "project2"
    PROJECT3    = "project3"

    PARTNER1    = "partner1"
    PARTNER2    = "partner2"
    PARTNER3    = "partner3"

    DEVEXP      = "devexp"
    MANAGEMENT  = "management"
    NONDUTCH    = "nondutch"

    TIMESLOTS   = "timeslots"
    TIMESLOT1   = "timeslot1"
    TIMESLOT2   = "timeslot2"
    TIMESLOT3   = "timeslot3"
    TIMESLOT4   = "timeslot4"
    TIMESLOT5   = "timeslot5"
    TIMESLOT6   = "timeslot6"
    TIMESLOT7   = "timeslot7"
    TIMESLOT8   = "timeslot8"
    TIMESLOT9   = "timeslot9"
    TIMESLOT10  = "timeslot10"

    NONDA       = "nonda"

    COMMENTS    = "comments"

    QUESTION_LABELS = [
        (FIRSTNAME, "First name", False),
        (LASTNAME, "Last name", False),
        (EMAIL, "Email", True),
        (GITHUB_USERNAME, "GitHub username", False),
        (GITHUB_ID, "GitHub ID", False),
        (STUDENT_NUMBER, "Student number", True),
        (COURSE, "Course", True),
        (PROJECT1, "1st project preference", True),
        (PROJECT2, "2nd project preference", True),
        (PROJECT3, "3rd project preference", True),
        (COURSE, "Course", True),
        (PARTNER1, "1st partner preference", True),
        (PARTNER2, "2nd partner preference", True),
        (PARTNER3, "3rd partner preference", True),
        (DEVEXP, "Dev Experience", True),
        (MANAGEMENT, "Management Interest", True),
        (NONDUTCH, "Non-dutch", True),
        (TIMESLOTS, "Timeslot availability", False),
        (NONDA, "Has problems with signing an NDA", True),
        (COMMENTS, "Comments", True),
    ]

    registration = models.ForeignKey(Registrations, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    label = models.CharField(max_length=50, choices=[(a, b) for a, b, _ in QUESTION_LABELS], blank=True, null=True)
    optional = models.BooleanField(default=False)

    parent_choice = models.ForeignKey(
        "QuestionChoice",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="follow_up_questions",
    )

    min_choices = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum number of choices for MULTI questions",
    )
    max_choices = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of choices for MULTI questions",
    )
    warnings = models.TextField(
        blank=True, null=True, help_text="Warnings to show if validation fails"
    )

    def __str__(self):
        return self.question


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submission = models.ForeignKey(
        RegistrationSubmission, on_delete=models.CASCADE
    )

    @property
    def answer(self):
        """Return the correct answer data object depending on question type."""
        qtype = self.question.question_type

        if qtype == Question.TEXT or qtype == Question.BIGTEXT:
            try:
                return self.textdata
            except TextData.DoesNotExist:
                return None

        elif qtype == Question.CHOICE or qtype == Question.DROPDOWN:
            try:
                return self.choicedata
            except ChoiceData.DoesNotExist:
                return None

        else:
            try:
                return self.multidata
            except MultiData.DoesNotExist:
                return None

    @answer.setter
    def answer(self, value):
        """Set the correct answer value depending on question type."""
        qtype = self.question.question_type

        if qtype == Question.TEXT or qtype == Question.BIGTEXT:
            try:
                self.textdata.value = value
            except TextData.DoesNotExist:
                self.textdata = TextData(answer=self, value=value)
            self.textdata.save()

        elif qtype == Question.CHOICE or qtype == Question.DROPDOWN:
            try:
                self.choicedata.choice = value
            except ChoiceData.DoesNotExist:
                self.choicedata = ChoiceData(answer=self, choice=value)
            self.choicedata.save()

        else:
            try:
                data = self.multidata
            except MultiData.DoesNotExist:
                data = MultiData.objects.create(answer=self)

            data.choices.set(value)
            data.save()

    @property
    def answer_value(self):
        """Return the human-readable answer depending on question type."""
        qtype = self.question.question_type

        if qtype == Question.TEXT or qtype == Question.BIGTEXT:
            return getattr(self.textdata, "value", "")

        elif qtype == Question.CHOICE or qtype == Question.DROPDOWN:
            return getattr(self.choicedata.choice, "value", "")

        elif qtype == Question.MULTI:
            try:
                return ", ".join(c.value for c in self.multidata.choices.all())
            except MultiData.DoesNotExist:
                return ""

        return ""

    @classmethod
    def save_from_cleaned_data(cls, submission, cleaned_data):
        "Create Answer objects for all question_* fields."

        for key, raw_value in cleaned_data.items():
            if not key.startswith("question_"):
                continue

            question_id = int(key.split("_")[1])
            question = Question.objects.get(pk=question_id)

            answer = cls.objects.create(
                submission=submission, question=question
            )
            answer.set_value(raw_value)

    def set_value(self, raw_value):
        """Store the answer depending on the question type."""
        qtype = self.question.question_type

        if qtype in (Question.TEXT, Question.BIGTEXT):
            TextData.objects.update_or_create(
                answer=self, defaults={"value": raw_value}
            )

        elif qtype in (Question.CHOICE, Question.DROPDOWN):
            choice = QuestionChoice.objects.get(pk=int(raw_value))
            ChoiceData.objects.update_or_create(
                answer=self, defaults={"choice": choice}
            )

        elif qtype == Question.MULTI:
            choice_ids = [int(v) for v in raw_value]
            choices = self.question.choices.filter(pk__in=choice_ids)

            multi, _ = MultiData.objects.get_or_create(answer=self)
            multi.choices.set(choices)
            multi.save()

    def __str__(self):
        return f"{self.submission.participant} answers #{self.question.id}"


class QuestionChoice(models.Model):
    "Model for ChoiceData and MultiData."

    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=255)
    follow_up = models.BooleanField(default=False)

    def __str__(self):
        return self.value


class TextData(models.Model):
    "Model storing value of an open question."

    answer = models.OneToOneField(Answer, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.value


class ChoiceData(models.Model):
    "Model storing choice answer for a closed question."

    answer = models.OneToOneField(Answer, on_delete=models.CASCADE)
    choice = models.ForeignKey(QuestionChoice, on_delete=models.CASCADE)


class MultiData(models.Model):
    "Model storing multiple choice answers for a closed question."

    answer = models.OneToOneField(Answer, on_delete=models.CASCADE)
    choices = models.ManyToManyField(QuestionChoice)


class Registration(models.Model):
    """Model containing registration specific data."""

    EXPERIENCE_BEGINNER = 1
    EXPERIENCE_INTERMEDIATE = 2
    EXPERIENCE_ADVANCED = 3

    EXPERIENCE_CHOICES = (
        (EXPERIENCE_BEGINNER, "Beginner"),
        (EXPERIENCE_INTERMEDIATE, "Intermediate"),
        (EXPERIENCE_ADVANCED, "Advanced"),
    )

    class Meta:
        """Meta class for Registration."""

        unique_together = [["user", "semester"]]
        ordering = ["semester"]

    user = models.ForeignKey(Employee, on_delete=models.CASCADE)

    projects = models.ManyToManyField(Project, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    preference1 = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    preference2 = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    preference3 = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    partner_preference1 = models.CharField(
        null=True, blank=True, max_length=50
    )
    partner_preference2 = models.CharField(
        null=True, blank=True, max_length=50
    )
    partner_preference3 = models.CharField(
        null=True, blank=True, max_length=50
    )

    dev_experience = models.PositiveSmallIntegerField(
        choices=EXPERIENCE_CHOICES
    )
    git_experience = models.PositiveSmallIntegerField(
        choices=EXPERIENCE_CHOICES, default=EXPERIENCE_BEGINNER
    )
    scrum_experience = models.PositiveSmallIntegerField(
        choices=EXPERIENCE_CHOICES, default=EXPERIENCE_BEGINNER
    )

    management_interest = models.BooleanField(default=False)

    is_international = models.BooleanField(default=False)
    available_during_scheduled_timeslot_1 = models.BooleanField(default=True)
    available_during_scheduled_timeslot_2 = models.BooleanField(default=True)
    available_during_scheduled_timeslot_3 = models.BooleanField(default=True)
    available_during_scheduled_timeslot_4 = models.BooleanField(default=True)
    available_during_scheduled_timeslot_5 = models.BooleanField(default=True)
    available_during_scheduled_timeslot_6 = models.BooleanField(default=True)
    available_during_scheduled_timeslot_7 = models.BooleanField(default=True)
    available_during_scheduled_timeslot_8 = models.BooleanField(default=True)
    available_during_scheduled_timeslot_9 = models.BooleanField(default=True)
    available_during_scheduled_timeslot_10 = models.BooleanField(default=True)
    has_problems_with_signing_an_nda = models.BooleanField(default=False)
    comments = models.TextField(null=True, blank=True)

    def get_projects(self):
        """Get all the projects of a registration."""
        return self.projects.all()

    def has_projects(self):
        """Returns true if there is at least one project."""
        return self.projects.all().count() != 0

    def remove_projects(self):
        """Remove all the projects of a registration."""
        return self.projects.set([])

    def add_project(self, value):
        """Set the projects of a registration."""
        self.projects.add(value)

    @property
    def is_director(self):
        """Check if a registration is a director."""
        return (
            self.projects.all().count() == 0
            and self.course == Course.objects.sdm()
        )

    def _match_partner_name_to_user(self, name):
        """
        Match a string to a user.

        Find the most similar user name to the given name.
        """
        if name is None:
            return None

        ratios = {}
        for user in User.objects.filter(
            registration__semester=self.semester
        ).all():
            ratio = SequenceMatcher(None, name, user.get_full_name()).ratio()
            if ratio > 0.5:
                ratios[user] = ratio

        if ratios:
            return max(ratios, key=lambda k: ratios[k])
        return None

    @cached_property
    def partner_preference1_user(self):
        """Get the user most similar to the first partner preference."""
        return self._match_partner_name_to_user(self.partner_preference1)

    @cached_property
    def partner_preference2_user(self):
        """Get the user most similar to the second partner preference."""
        return self._match_partner_name_to_user(self.partner_preference2)

    @cached_property
    def partner_preference3_user(self):
        """Get the user most similar to the third partner preference."""
        return self._match_partner_name_to_user(self.partner_preference3)

    def __str__(self):
        """Give user information about this object."""
        return f"{self.user.get_full_name()} ({self.semester})"
