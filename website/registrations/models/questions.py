from django.db import models
from courses.models import Semester
from registrations.models import Employee


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

    objects = RegistrationManager()

    def __str__(self):
        """Return title + semester."""
        return f"{self.title} ({self.semester})"


class RegistrationSubmission(models.Model):
    """Submission of a Registration by a user."""

    registration = models.ForeignKey(Registrations, on_delete=models.CASCADE)
    participant = models.ForeignKey(Employee, on_delete=models.CASCADE)

    submitted = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)

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

    registration = models.ForeignKey(Registrations, on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    optional = models.BooleanField(default=False)

    parent_choice = models.ForeignKey(
        "QuestionChoice", null=True, blank=True,
        on_delete=models.CASCADE,
        related_name="follow_up_questions"
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

            answer = cls.objects.create(submission=submission, question=question)
            answer.set_value(raw_value)

    def set_value(self, raw_value):
        """Store the answer depending on the question type."""
        qtype = self.question.question_type

        if qtype in (Question.TEXT, Question.BIGTEXT):
            TextData.objects.update_or_create(
                answer=self,
                defaults={"value": raw_value}
            )

        elif qtype == Question.CHOICE:
            choice = QuestionChoice.objects.get(pk=int(raw_value))
            ChoiceData.objects.update_or_create(
                answer=self,
                defaults={"choice": choice}
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
