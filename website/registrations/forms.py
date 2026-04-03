import re

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from registrations.models import Employee, questions

student_number_regex = re.compile(r"^[sS]?(\d{7})$")
wrong_email_regex = re.compile(r"^[sS]?(\d{7})@(?:student\.)?ru\.nl$")

User: Employee = get_user_model()


class Step2Form(forms.Form):
    """Form to get user information for registration."""
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    student_number = forms.CharField(label="Student Number")
    github_username = forms.CharField(disabled=True)
    github_id = forms.IntegerField(disabled=True)
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

        current_registration = (
            questions.Registrations.objects.current_registration()
        )

        if not current_registration:
            raise ValueError("No registration found for the current semester")

        for q in current_registration.question_set.all():
            field_name = f"question_{q.id}"

            if q.question_type == questions.Question.TEXT:
                self.fields[field_name] = forms.CharField(
                    label=q.question, required=not q.optional
                )

            elif q.question_type == questions.Question.CHOICE:
                choices = questions.QuestionChoice.objects.filter(
                    question=q
                ).values_list("id", "value")
                self.fields[field_name] = forms.ChoiceField(
                    label=q.question,
                    choices=choices,
                    required=not q.optional,
                    widget=forms.RadioSelect,
                )

            elif q.question_type == questions.Question.MULTI:
                choices = questions.QuestionChoice.objects.filter(
                    question=q
                ).values_list("id", "value")
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=q.question,
                    choices=choices,
                    required=not q.optional,
                    widget=forms.CheckboxSelectMultiple,
                )
            elif q.question_type == questions.Question.DROPDOWN:
                choices = questions.QuestionChoice.objects.filter(
                    question=q
                ).values_list("id", "value")
                self.fields[field_name] = forms.ChoiceField(
                    label=q.question,
                    choices=choices,
                    required=not q.optional,
                    widget=forms.Select,
                )
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
                raise ValidationError(
                    "Email address already in use.", code="exists"
                )

            if wrong_email_regex.match(email) is not None:
                raise ValidationError(
                    "Non-existent email address.", code="invalid"
                )

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
            raise ValidationError(
                "Student Number already in use.", code="exists"
            )

        return student_number

    def clean(self):
        cleaned_data = super().clean()

        for field_name in self.fields:
            if field_name.startswith("question_"):
                question_id = int(field_name.split("_")[1])
                question = questions.Question.objects.get(pk=question_id)
                answer = cleaned_data.get(field_name)

                if not question.optional and not answer:
                    raise ValidationError(
                        f"Question '{question.question}' is required."
                    )

                if (
                    question.question_type == questions.Question.MULTI
                    and answer
                ):
                    selected_count = len(answer)

                    if (
                        question.min_choices is not None
                        and selected_count < question.min_choices
                    ):
                        self.warnings.append(
                            (
                                field_name,
                                f"At least {question.min_choices} choices are required (you selected {selected_count}).",
                            )
                        )

                    if (
                        question.max_choices is not None
                        and selected_count > question.max_choices
                    ):
                        self.warnings.append(
                            (
                                field_name,
                                f"No more than {question.max_choices} choices are allowed (you selected {selected_count}).",
                            )
                        )

                    if question.warnings:
                        self.warnings.append(question.warnings.strip())

        return cleaned_data
