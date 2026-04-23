import csv
from io import StringIO

from admin_auto_filters.filters import AutocompleteFilter

from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.views import View
from django.utils.safestring import mark_safe
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from courses.models import Semester

from projects.models import Project

from nested_admin import NestedModelAdmin, NestedTabularInline

from registrations.models import Employee, Registration
from registrations.models.registration import (
    Question,
    QuestionChoice,
    Registrations,
    RegistrationSubmission,
    Answer,
)
from registrations.team_assignment import (
    CSV_STRUCTURE,
    # TeamAssignmentGenerator,
)

User: Employee = get_user_model()

"The following four classes provide the logic behind the admin"
"interface for Registrationss with the proper inlines."

class QuestionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        required_labels = {
            label
            for (label, _, must_be_set) in Question.QUESTION_LABELS
            if must_be_set
        }

        used_labels = set()

        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue
            if not form.cleaned_data:
                continue

            label = form.cleaned_data.get("label")
            if label:
                used_labels.add(label)

        missing = required_labels - used_labels
        if missing:
            raise ValidationError(
                f"Missing required labels: {', '.join(missing)}"
            )

class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get("question_type")
        min_choices = cleaned_data.get("min_choices")
        max_choices = cleaned_data.get("max_choices")

        errors = []
    
        if question_type == Question.MULTI:
            if min_choices is not None and min_choices < 0:
                errors.append("min_choices cannot be negative.")
            if max_choices is not None and max_choices < 0:
                errors.append("max_choices cannot be negative.")
            if (
                min_choices is not None
                and max_choices is not None
                and min_choices > max_choices
            ):
                errors.append(
                    "min_choices cannot be greater than max_choices."
                )

            if self.instance and self.instance.pk:
                choice_count = self.instance.choices.count()
                if min_choices is not None and min_choices > choice_count:
                    errors.append(
                        f"min_choices ({min_choices}) cannot exceed the number of choices ({choice_count})."
                    )
                if max_choices is not None and max_choices > choice_count:
                    errors.append(
                        f"max_choices ({max_choices}) cannot exceed the number of choices ({choice_count})."
                    )

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data


class FollowUpQuestionChoiceInline(NestedTabularInline):
    model = QuestionChoice
    extra = 0
    fk_name = "question"
    inlines = []


class FollowUpQuestionInline(NestedTabularInline):
    model = Question
    fk_name = "parent_choice"
    extra = 0
    exclude = ["parent_choice", "registration"]
    inlines = [FollowUpQuestionChoiceInline]

class QuestionChoiceInline(NestedTabularInline):
    model = QuestionChoice
    extra = 0
    fk_name = "question"
    inlines = [FollowUpQuestionInline]


class QuestionInline(NestedTabularInline):
    model = Question
    fk_name = "registration"
    form = QuestionAdminForm
    formset = QuestionInlineFormSet
    extra = 0
    exclude = ["parent_choice"]
    inlines = [QuestionChoiceInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(parent_choice__isnull=True)

    class Media:
        js = ("js/question_type_toggle_admin.js",)


@admin.register(Registrations)
class RegistrationsAdmin(NestedModelAdmin):
    list_display = ("title", "semester")
    inlines = [QuestionInline]

    # Override get_urls to add custom url for sample registration
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "create-sample/",
                self.admin_site.admin_view(self.create_sample_registration),
                name="create-sample-registration",
            )
        ]
        return custom_urls + urls

    # Create a sample registration with autofilled questions
    def create_sample_registration(self, request):
        reg = Registrations.objects.create(
            title="Sample Registration",
            semester=Semester.objects.get_or_create_current_semester(),
        )

        sample_questions = [
            ("firstname",  "First name", Question.TEXT),
            ("lastname",   "Last name", Question.TEXT),

            ("project1",   "1st project preference", Question.DROPDOWN, ["Project A", "Project B", "Project C"]),
            ("project2",   "2nd project preference", Question.DROPDOWN, ["Project A", "Project B", "Project C"]),
            ("project3",   "3rd project preference", Question.DROPDOWN, ["Project A", "Project B", "Project C"]),

            ("partner1",   "1st partner preference", Question.TEXT),
            ("partner2",   "2nd partner preference", Question.TEXT),
            ("partner3",   "3rd partner preference", Question.TEXT),

            ("devexp",     "Dev Experience", Question.CHOICE),
            ("management", "Management Interest", Question.CHOICE, ["Yes", "No"]),
            ("nondutch",   "Non-dutch", Question.CHOICE, ["Yes", "No"]),

            ("timeslot1",  "Available during scheduled timeslot 1", Question.CHOICE),
            ("timeslot2",  "Available during scheduled timeslot 2", Question.CHOICE),
            ("timeslot3",  "Available during scheduled timeslot 3", Question.CHOICE),
            ("timeslot4",  "Available during scheduled timeslot 4", Question.CHOICE),
            ("timeslot5",  "Available during scheduled timeslot 5", Question.CHOICE),
            ("timeslot6",  "Available during scheduled timeslot 6", Question.CHOICE),
            ("timeslot7",  "Available during scheduled timeslot 7", Question.CHOICE),
            ("timeslot8",  "Available during scheduled timeslot 8", Question.CHOICE),
            ("timeslot9",  "Available during scheduled timeslot 9", Question.CHOICE),
            ("timeslot10", "Available during scheduled timeslot 10", Question.CHOICE),

            ("nonda",      "Has problems with signing an NDA", Question.CHOICE, ["Yes", "No"]),
        ]

        for item in sample_questions:
            # Case distinction for questions with and without choices
            if len(item) == 3:
                label, text, qtype = item
                choices = []
            else:
                label, text, qtype, choices = item

            q = Question.objects.create(
                registration=reg,
                label=label,
                question=text,
                question_type=qtype,
            )

            for choice_text in choices:
                QuestionChoice.objects.create(
                    question=q,
                    value=choice_text
                )


        url = reverse("admin:registrations_registrations_change", args=[reg.pk])
        return redirect(url)

    # Set changelist to add button that calls create_sample_registration
    change_list_template = "admin/registrations/change_list.html"



@admin.register(Question)
class QuestionAdmin(NestedModelAdmin):
    form = QuestionAdminForm
    list_display = ("question", "registration", "question_type", "label", "optional")
    inlines = [QuestionChoiceInline]


class AnswerInline(NestedTabularInline):
    model = Answer
    extra = 0
    readonly_fields = ("question_text", "answer_value")
    exclude = ("question",)

    def question_text(self, obj):
        return obj.question.question

    question_text.short_description = "Question"

    def answer_value(self, obj):
        return obj.answer_value

    answer_value.short_description = "Answer"


@admin.register(RegistrationSubmission)
class RegistrationSubmissionAdmin(admin.ModelAdmin):
    list_display = ("registration", "participant", "submitted", "created")
    inlines = [AnswerInline]


class UserAdminSemesterFilter(AutocompleteFilter):
    """Filter class to filter Semester objects."""

    title = "Semester"
    field_name = "semester"
    rel_model = Registration

    def queryset(self, request, queryset):
        """Filter semesters."""
        if self.value():
            return queryset.filter(registration__semester=self.value())
        else:
            return queryset


class UserAdminProjectFilter(AutocompleteFilter):
    """Filter class to filter current Project objects."""

    title = "Projects"
    field_name = "projects"
    rel_model = Registration

    def queryset(self, request, queryset):
        """Filter out participants in the specified Project."""
        if self.value():
            return queryset.filter(registration__projects=self.value())
        return queryset


class RegistrationInline(NestedTabularInline):
    """Inline form for Registration."""

    model = Registrations
    extra = 0


class RegistrationSubmissionInline(NestedTabularInline):
    """Inline form for Registration."""

    model = RegistrationSubmission
    extra = 0
    inlines = [AnswerInline]


@admin.register(User)
class UserAdmin(NestedModelAdmin):
    """Custom admin for Student."""

    actions = (
        "unassign_from_project",
        "export_student_numbers",
        "export_registrations",
    )

    fieldsets = (
        (
            "Personal",
            {"fields": ("first_name", "last_name", "email", "student_number")},
        ),
        (
            "Administration",
            {
                "fields": (
                    "date_joined",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "GitHub",
            {
                "fields": ("github_id", "github_username"),
                "classes": ("collapse",),
            },
        ),
        ("Private comments", {"fields": ("comments",)}),
    )

    inlines = [RegistrationSubmissionInline]
    list_display = (
        "__str__",
        "get_current_project",
        "is_staff",
    )

    list_filter = (
        UserAdminSemesterFilter,
        UserAdminProjectFilter,
        "registration__course",
        "registration__dev_experience",
        "registration__git_experience",
        "registration__scrum_experience",
        "registration__management_interest",
        "is_staff",
        "registration__is_international",
        "registration__available_during_scheduled_timeslot_1",
        "registration__available_during_scheduled_timeslot_2",
        "registration__available_during_scheduled_timeslot_3",
        "registration__has_problems_with_signing_an_nda",
    )

    # Necessary for the autocomplete filter
    search_fields = (
        "first_name",
        "last_name",
        "student_number",
        "github_username",
    )

    def get_current_project(self, obj):
        """Return current project."""
        registration = obj.registration_set.first()
        return (
            mark_safe("<br>".join(str(p) for p in registration.get_projects()))
            if registration
            else None
        )

    get_current_project.short_description = "Project"

    def export_student_numbers(self, request, queryset):
        """Export the first name, last name and student number of the selected users to a CSV file."""
        content = StringIO()
        writer = csv.writer(
            content, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(["First name", "Last name", "Student number"])
        for user in queryset:
            writer.writerow(
                [user.first_name, user.last_name, user.student_number]
            )

        response = HttpResponse(
            content.getvalue(), content_type="application/x-zip-compressed"
        )
        response["Content-Disposition"] = (
            "attachment; filename=student-numbers.csv"
        )
        return response

    export_student_numbers.short_description = (
        "Export names and student numbers"
    )

    def export_registrations(self, request, queryset):
        """Export the registration information of the most recent registration of the selected users to a CSV file."""
        content = StringIO()
        writer = csv.writer(
            content, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "First name",
                "Last name",
                "Student number",
                "GitHub username",
                "Course",
                "1st project preference",
                "2nd project preference",
                "3rd project preference",
                "1st partner preference",
                "2nd partner preference",
                "3rd partner preference",
                "Dev Experience",
                "Git Experience",
                "Scrum Experience",
                "Management Interest",
                "Non-dutch",
                "Available during scheduled timeslot 1",
                "Available during scheduled timeslot 2",
                "Available during scheduled timeslot 3",
                "Available during scheduled timeslot 4",
                "Available during scheduled timeslot 5",
                "Available during scheduled timeslot 6",
                "Available during scheduled timeslot 7",
                "Available during scheduled timeslot 8",
                "Available during scheduled timeslot 9",
                "Available during scheduled timeslot 10",
                "Has problems with signing an NDA",
                "Registration Comments",
            ]
        )
        for user in queryset:
            registration = user.registration_set.first()
            writer.writerow(
                [
                    user.first_name,
                    user.last_name,
                    user.student_number,
                    user.github_username,
                    registration.course,
                    registration.preference1,
                    registration.preference2,
                    registration.preference3,
                    registration.partner_preference1,
                    registration.partner_preference2,
                    registration.partner_preference3,
                    registration.dev_experience,
                    registration.git_experience,
                    registration.scrum_experience,
                    registration.management_interest,
                    registration.is_international,
                    registration.available_during_scheduled_timeslot_1,
                    registration.available_during_scheduled_timeslot_2,
                    registration.available_during_scheduled_timeslot_3,
                    registration.available_during_scheduled_timeslot_4,
                    registration.available_during_scheduled_timeslot_5,
                    registration.available_during_scheduled_timeslot_6,
                    registration.available_during_scheduled_timeslot_7,
                    registration.available_during_scheduled_timeslot_8,
                    registration.available_during_scheduled_timeslot_9,
                    registration.available_during_scheduled_timeslot_10,
                    registration.has_problems_with_signing_an_nda,
                    registration.comments,
                ]
            )

        response = HttpResponse(
            content.getvalue(), content_type="application/x-zip-compressed"
        )
        response["Content-Disposition"] = (
            "attachment; filename=registrations.csv"
        )
        return response

    def unassign_from_project(self, request, queryset):
        """Clear the set project for a registration."""
        num_unassigned = 0
        for user in queryset:
            reg = user.registration_set.first()
            if reg is not None and reg.get_projects() is not None:
                reg.remove_projects()
                reg.save()
                num_unassigned += 1
        messages.success(
            request,
            f"Succesfully unassigned {num_unassigned} registrations.",
        )

    def get_urls(self):
        """Get admin urls."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "import/",
                self.admin_site.admin_view(
                    ImportAssignmentAdminView.as_view()
                ),
                name="import",
            ),
        ]
        return custom_urls + urls


class CsvImportForm(forms.Form):
    """Form used when importing a csv group assignment."""

    csv_file = forms.FileField(required=True)
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(), required=True
    )


class ImportAssignmentAdminView(View):
    """Import a CSV file with project assignment."""

    def get(self, request):
        """Get a form to select the semester to import for."""
        form = CsvImportForm()
        payload = {
            "form": form,
            "header": CSV_STRUCTURE[:5],
            "title": "Import",
        }

        return render(request, "admin/registrations/import-csv.html", payload)

    @staticmethod
    def handle_csv(csv_file, semester):
        """Process a CSV file with project assignment."""
        csv_data = csv_file.read().decode("utf-8")
        dialect = csv.Sniffer().sniff(csv_data)
        reader = csv.reader(StringIO(csv_data), dialect=dialect)

        num_assigned = 0
        num_ignored = 0

        expected_header = CSV_STRUCTURE[:5]

        for row in reader:
            if reader.line_num == 1 and row[:5] != expected_header:
                raise ValueError("Invalid columns")
            elif reader.line_num == 1 or not row[4]:
                continue

            csv_first_name = row[0]
            csv_last_name = row[1]
            csv_student_number = row[2]
            csv_course = row[3]
            csv_project = row[4]

            try:
                project = Project.objects.get(
                    name=csv_project, semester=semester
                )
            except Project.DoesNotExist:
                raise ValueError(
                    f"No project was found for {csv_project} in semester {semester}."
                )

            try:
                registration = Registration.objects.get(
                    user__first_name=csv_first_name,
                    user__last_name=csv_last_name,
                    semester=semester,
                    course__name=csv_course,
                    user__student_number=csv_student_number,
                )
            except Registration.DoesNotExist:
                raise ValueError(
                    f"No registration was found for {csv_first_name} {csv_last_name} with student number "
                    f"{csv_student_number} in semester {semester} for course {csv_course}. "
                )

            if registration.get_projects().count() != 0:
                num_ignored += 1
            else:
                registration.add_project(project)
                registration.save()
                num_assigned += 1

        return num_assigned, num_ignored

    def post(self, request):
        """Import and process a .csv file with assigned projects."""
        csv_file = request.FILES["csv_file"]
        semester = Semester.objects.get(pk=request.POST.get("semester"))
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "File is not CSV type")
        elif csv_file.multiple_chunks():
            messages.error(
                request,
                "Uploaded file is too big (%.2f MB)."
                % (csv_file.size / (1000 * 1000),),
            )
        else:
            try:
                num_assigned, num_ignored = self.handle_csv(csv_file, semester)
                messages.success(
                    request,
                    f"CSV file has been imported. {num_assigned} registrations are updated. "
                    f"{num_ignored} registrations were already assigned and not been overwritten.",
                )
            except ValueError as e:
                messages.error(request, e)
        return redirect("..")


class DownloadAssignmentForm(forms.Form):
    """Form used when generating and downloading a team assignment."""

    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(), required=True
    )
