import re

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import widgets

from courses.models import Course, Semester
from projects.models import Project
from registrations.models import Employee, Registration, questions

student_number_regex = re.compile(r"^[sS]?(\d{7})$")
wrong_email_regex = re.compile(r"^[sS]?(\d{7})@(?:student\.)?ru\.nl$")

User: Employee = get_user_model()


class Step2Form(forms.Form):
    """Form to get user information for registration."""

    def __init__(self, *args, **kwargs):
        """Set querysets dynamically."""
        super().__init__(*args, **kwargs)

        self.fields["course"].queryset = Course.objects.all()

        self.fields["project1"].queryset = Project.objects.filter(
            semester=Semester.objects.get_first_semester_with_open_registration()
        )
        self.fields["project2"].queryset = Project.objects.filter(
            semester=Semester.objects.get_first_semester_with_open_registration()
        )
        self.fields["project3"].queryset = Project.objects.filter(
            semester=Semester.objects.get_first_semester_with_open_registration()
        )
        self.warnings = []

    ignore_warnings = forms.BooleanField(
        label="I acknowledge the warning(s) and want to proceed with the registration",
        required=False,
        initial=False,
    )

    github_id = forms.IntegerField(disabled=True, label="GitHub ID")
    github_username = forms.CharField(disabled=True, label="GitHub Username")

    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")

    student_number = forms.CharField(
        label="Student Number",
        widget=widgets.TextInput(attrs={"placeholder": "s1234567"}),
    )

    course = forms.ModelChoiceField(queryset=None, empty_label=None)

    email = forms.EmailField()

    dev_experience = forms.ChoiceField(
        label="What is your programming experience?",
        choices=Registration.EXPERIENCE_CHOICES,
        initial=Registration.EXPERIENCE_BEGINNER,
        help_text="<strong>Beginner</strong>: I passed the programming "
        "courses from my curriculum but it was not easy.<br>"
        "<strong>Intermediate</strong>: the programming courses in "
        "the curriculum were easy for me and I have experience "
        "with some small (hobby) projects.<br>"
        "<strong>Advanced</strong>: I have a lot of experience with "
        "programming.<br>"
        "<strong>NOTE</strong>: If you did not pass the programming "
        "courses and you are following the Software Engineering course, please "
        "do not register for this course.",
    )

    git_experience = forms.ChoiceField(
        label="What is your experience working with git(hub)?",
        choices=Registration.EXPERIENCE_CHOICES,
        initial=Registration.EXPERIENCE_BEGINNER,
        help_text="<strong>Beginner</strong>: I never really used git <br>"
        "<strong>Intermediate</strong>: I have used git before, working "
        "on small projects. With multiple branches and pull requests <br>"
        "<strong>Advanced</strong>: I have a lot of experience with "
        "git(hub) working on a project with multiple programmers. <br>"
        "<strong>NOTE</strong>: You do not need any experience with git, "
        "you are going to learn it in this course. But it is nice if you already know git.",
    )

    scrum_experience = forms.ChoiceField(
        label="What is your scrum experience?",
        choices=Registration.EXPERIENCE_CHOICES,
        initial=Registration.EXPERIENCE_BEGINNER,
        help_text="<strong>Beginner</strong>: None <br>"
        "<strong>Intermediate</strong>: I have worked in teams, but "
        " not really with scrum <br>"
        "<strong>Advanced</strong>: I have a lot of experience with "
        "scrum. (Work or committee)<br>"
        "<strong>NOTE</strong>: You do not need any experience with scrum, "
        "you are going to learn it in this course. But it is nice if you already know scrum.",
    )

    management_interest = forms.BooleanField(
        label="[Only relevant for bachelor students] I am interested in a management role",
        required=False,
        initial=False,
        help_text="If you check this box, you might get a more management oriented role.",
    )

    project1 = forms.ModelChoiceField(
        label="First project preference", queryset=None, required=False
    )

    project2 = forms.ModelChoiceField(
        label="Second project preference", queryset=None, required=False
    )

    project3 = forms.ModelChoiceField(
        label="Third project preference", queryset=None, required=False
    )

    partner1 = forms.CharField(
        label="Project partner preference",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Piet Janssen"}),
        max_length=100,
        required=False,
        help_text="Optional",
    )

    partner2 = forms.CharField(
        label="Project partner preference",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        max_length=100,
        required=False,
        help_text="Optional",
    )

    partner3 = forms.CharField(
        label="Project partner preference",
        widget=forms.TextInput(attrs={"placeholder": ""}),
        max_length=100,
        required=False,
        help_text="Optional",
    )

    international = forms.BooleanField(
        label="I don't speak Dutch", required=False
    )

    # 10 timeslot fields
    for i in range(1, 11):
        locals()[f"available_during_scheduled_timeslot_{i}"] = forms.BooleanField(
            label=f"I am available during scheduled timeslot {i} for the course",
            required=False,
            initial=True,
        )

    has_problems_with_signing_an_nda = forms.BooleanField(
        label="I have problems with signing an NDA",
        required=False,
        initial=False,
        help_text="If you check this box, you will not be placed in a project that requires an NDA.",
    )

    comments = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Do you have any comments?"}),
        required=False,
        help_text="Optional",
    )

    def clean_email(self):
        if (
            User.objects.exclude(github_id=self.cleaned_data["github_id"])
            .filter(email=self.cleaned_data["email"])
            .exists()
        ):
            raise ValidationError("Email address already in use.", code="exists")

        match = wrong_email_regex.match(self.cleaned_data["email"])
        if match is not None:
            raise ValidationError("Non-existent email address.", code="invalid")

        return self.cleaned_data["email"]

    def clean_student_number(self):
        student_number = self.cleaned_data["student_number"]

        m = student_number_regex.match(student_number)
        if m is None:
            raise ValidationError("Invalid Student Number", code="invalid")

        student_number = "s" + m.group(1)

        if (
            User.objects.exclude(github_id=self.cleaned_data["github_id"])
            .filter(student_number=student_number)
            .exists()
        ):
            raise ValidationError("Student Number already in use.", code="exists")
        return student_number

    def clean(self):
        cleaned_data = super().clean()

        if User.objects.filter(
            github_id=cleaned_data.get("github_id"),
            registration__semester=Semester.objects.get_first_semester_with_open_registration(),
        ).exists():
            raise ValidationError("User already registered for this semester.", code="exists")

        project1 = cleaned_data.get("project1")
        project2 = cleaned_data.get("project2")
        project3 = cleaned_data.get("project3")

        if len(set(filter(None, (project1, project2, project3)))) != 3:
            raise ValidationError("You should fill in all preferences with unique values.")

        available_slots = sum(
            bool(cleaned_data.get(f"available_during_scheduled_timeslot_{i}"))
            for i in range(1, 11)
        )

        if available_slots < 4 and not cleaned_data.get("available_during_scheduled_timeslot_10"):
            self.warnings.append(
                "You are only available for less than 4 scheduled timeslots and "
                "not available for the last timeslot on Friday afternoon. "
                "This may make scheduling difficult."
            )

        return cleaned_data


class Step2FormNew(forms.Form):
    """Form to get user information for registration."""
    first_name = forms.CharField()
    last_name = forms.CharField()
    course = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label=None)
    email = forms.EmailField()
    github_username = forms.CharField(disabled=True)
    github_id = forms.IntegerField(disabled=True)
    student_number = forms.CharField()
    ignore_warnings = forms.BooleanField(
        label="I acknowledge the warning(s) and want to proceed with the registration",
        required=False,
        initial=False,
    )

    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)

        if session is None or "github_id" not in session:
            raise ValueError("GitHub session info is required for this form")

        github_id = session["github_id"]
        github_username = session["github_username"]

        if github_id is None or github_username is None:
            raise ValueError("GitHub session info is incomplete")
        
        self.fields["github_id"].initial = github_id
        self.fields["github_username"].initial = github_username

        self.github_id = github_id
        self.github_username = github_username
        self.warnings = []

        current_registration = questions.Registrations.objects.current_registration()
        
        if not current_registration:
            raise ValueError("No registration found for the current semester")

        for q in current_registration.question_set.all():
            field_name = f"question_{q.id}"

            if q.question_type == questions.Question.TEXT:
                self.fields[field_name] = forms.CharField(
                    label=q.question,
                    required=not q.optional)

            elif q.question_type == questions.Question.CHOICE:
                choices=questions.QuestionChoice.objects.filter(
                        question=q
                    ).values_list("id", "value")
                self.fields[field_name] = forms.ChoiceField(
                    label=q.question,
                    choices=choices,
                    required=not q.optional,
                    widget=forms.RadioSelect)
                
            elif q.question_type == questions.Question.MULTI:
                choices=questions.QuestionChoice.objects.filter(
                        question=q
                    ).values_list("id", "value")
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=q.question,
                    choices=choices,
                    required=not q.optional,
                    widget=forms.CheckboxSelectMultiple)
            else:
                raise ValueError(f"Unknown question type: {q.question_type}")
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        github_id = self.cleaned_data.get("github_id")

        if email and github_id:
            if (
                User.objects.exclude(github_id=github_id)
                .filter(email=email)
                .exists()
            ):
                raise ValidationError("Email address already in use.", code="exists")

            if wrong_email_regex.match(email) is not None:
                raise ValidationError("Non-existent email address.", code="invalid")

        return email

    def clean_student_number(self):
        student_number = self.cleaned_data.get("student_number")
        github_id = self.cleaned_data.get("github_id")

        m = student_number_regex.match(student_number)
        if m is None:
            raise ValidationError("Invalid Student Number", code="invalid")

        student_number = "s" + m.group(1)

        if (
            User.objects.exclude(github_id=github_id)
            .filter(student_number=student_number)
            .exists()
        ):
            raise ValidationError("Student Number already in use.", code="exists")
        
        return student_number

    def clean(self):
        cleaned_data = super().clean()

        for field_name in self.fields:
            if field_name.startswith("question_"):
                question_id = int(field_name.split("_")[1])
                question = questions.Question.objects.get(pk=question_id)
                answer = cleaned_data.get(field_name)

                if not question.optional and not answer:
                    raise ValidationError(f"Question '{question.question}' is required.")
        
        return cleaned_data