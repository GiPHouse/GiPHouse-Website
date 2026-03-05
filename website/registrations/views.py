from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from courses.models import Semester
from registrations.forms import Step2FormNew, Step2Form
from registrations.models import Employee, Registration, questions

# Only for testing
from django.shortcuts import redirect

def dev_login(request):
    """
    Simulate GitHub OAuth login for local development.
    This sets the session variables that Step2FormNew expects.
    """
    employee = Employee.objects.get(github_username="devuser")
    login(request, employee)

    request.session["github_id"] = 123456
    request.session["github_username"] = "devuser"
    request.session["github_name"] = "Dev User"
    request.session["github_email"] = "devuser@example.com"

    # Redirect to Step2View where the form is
    return redirect("registrations:step2")  

User: Employee = get_user_model()


class Step1View(TemplateView):
    """View showing GitHub link."""

    template_name = "registrations/step-1.html"

    def get_context_data(self, *args, **kwargs):
        """Add semester to register form."""
        return super().get_context_data(
            registration_semester=Semester.objects.get_first_semester_with_open_registration(),
            **kwargs,
        )

    def dispatch(self, request, *args, **kwargs):
        """Check whether user is authenticated and if registration is possible."""
        # if not Semester.objects.get_first_semester_with_open_registration():
        #     messages.warning(
        #         request,
        #         "Registrations are currently not open",
        #         extra_tags="danger",
        #     )
        #     return redirect("home")

        if request.user.is_authenticated:
            logout(request)

        return super().dispatch(request, *args, **kwargs)


class Step2View(FormView):
    """View to show Step2Form."""

    template_name = "registrations/step-2.html"

    form_class = Step2FormNew

    success_url = "/"
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["session"] = self.request.session
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        """Check whether github_id is set in the session."""
        if not self.request.session.get("github_id"):
            return HttpResponseBadRequest()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Add semester to register form."""
        return super().get_context_data(
            registration_semester=Semester.objects.get_first_semester_with_open_registration(),
            **kwargs,
        )

    def get_initial(self):
        """Get the initial data for the form."""
        initial = super(Step2View, self).get_initial()

        try:
            first_name, last_name = self.request.session["github_name"].rsplit(
                " ", 1
            )
        except KeyError, AttributeError:
            first_name, last_name = "", ""
        except ValueError:
            first_name, last_name = self.request.session["github_name"], ""

        initial.update(
            {
                "email": self.request.session.get("github_email") or "",
                "github_id": self.request.session.get("github_id") or "",
                "github_username": self.request.session.get("github_username")
                or "",
                "first_name": first_name,
                "last_name": last_name,
            }
        )

        return initial

    def form_valid(self, form):
        """Check for warnings before registering."""
        if form.warnings and not form.cleaned_data.get("ignore_warnings"):
            form.add_error(None, form.warnings[0])
            return self.form_invalid(form)

        """Register new user if the form is valid."""
        with transaction.atomic():
            user, _ = User.objects.get_or_create(
                github_id=self.request.session["github_id"]
            )

            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.github_username = form.cleaned_data["github_username"]
            user.student_number = form.cleaned_data["student_number"]
            user.save()

            reg = questions.Registrations.objects.current_registration()

            if not reg:
                form.add_error(None, "No registration form found for this semester.")
                return self.form_invalid(form)
            
            submission = questions.RegistrationSubmission.objects.create(
                registration=reg,
                participant=user
            )

            # Registration.objects.create(
            #     user=user,
            #     semester=Semester.objects.get_first_semester_with_open_registration(),                
            #     course=form.cleaned_data["course"],
            #     git_experience=form.cleaned_data["git_experience"],
            #     dev_experience=form.cleaned_data["dev_experience"],
            #     scrum_experience=form.cleaned_data["scrum_experience"],
            #     management_interest=form.cleaned_data["management_interest"],
            #     preference1=form.cleaned_data["project1"],
            #     preference2=form.cleaned_data["project2"],
            #     preference3=form.cleaned_data["project3"],
            #     partner_preference1=form.cleaned_data["partner1"],
            #     partner_preference2=form.cleaned_data["partner2"],
            #     partner_preference3=form.cleaned_data["partner3"],
            #     comments=form.cleaned_data["comments"],
            #     is_international=form.cleaned_data["international"],
            #     available_during_scheduled_timeslot_1=form.cleaned_data[
            #         "available_during_scheduled_timeslot_1"
            #     ],
            #     available_during_scheduled_timeslot_2=form.cleaned_data[
            #         "available_during_scheduled_timeslot_2"
            #     ],
            #     available_during_scheduled_timeslot_3=form.cleaned_data[
            #         "available_during_scheduled_timeslot_3"
            #     ],
            #     available_during_scheduled_timeslot_4=form.cleaned_data[
            #         "available_during_scheduled_timeslot_4"
            #     ],
            #     available_during_scheduled_timeslot_5=form.cleaned_data[
            #         "available_during_scheduled_timeslot_5"
            #     ],
            #     available_during_scheduled_timeslot_6=form.cleaned_data[
            #         "available_during_scheduled_timeslot_6"
            #     ],
            #     available_during_scheduled_timeslot_7=form.cleaned_data[
            #         "available_during_scheduled_timeslot_7"
            #     ],
            #     available_during_scheduled_timeslot_8=form.cleaned_data[
            #         "available_during_scheduled_timeslot_8"
            #     ],
            #     available_during_scheduled_timeslot_9=form.cleaned_data[
            #         "available_during_scheduled_timeslot_9"
            #     ],
            #     available_during_scheduled_timeslot_10=form.cleaned_data[
            #         "available_during_scheduled_timeslot_10"
            #     ],
            #     has_problems_with_signing_an_nda=form.cleaned_data[
            #         "has_problems_with_signing_an_nda"
            #     ],
            # )

            for key, value in form.cleaned_data.items():
                if key.startswith("question-"):
                    question_id = int(key.split("-")[1])
                    question = questions.Question.objects.get(pk=question_id)

                    answer_obj = questions.Answer.objects.create(
                        submission=submission,
                        question=question
                    )

                    if question.question_type == questions.Question.TEXT:
                        questions.TextData.objects.create(answer=answer_obj, value=value)

                    elif question.question_type == questions.Question.CHOICE:
                        choice_obj = question.choices.get(pk=int(value))
                        questions.ChoiceData.objects.create(answer=answer_obj, choice=choice_obj)

                    elif question.question_type == questions.Question.MULTI:
                        choice_ids = [int(v) for v in value]
                        choice_objs = question.choices.filter(pk__in=choice_ids)
                        multi_data = questions.MultiData.objects.create(answer=answer_obj)
                        multi_data.choices.set(choice_objs)

            messages.success(
                self.request,
                "Registration created successfully",
                extra_tags="success",
            )

            login(
                self.request,
                user,
                backend="github_oauth.backends.GithubOAuthBackend",
            )

        return redirect("home")
