from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from courses.models import Semester


from registrations.forms import Step2Form
from registrations.models import Employee, registration


# Only for testing
def dev_login(request):
    """Simulate GitHub OAuth login for local development. This sets the session variables that Step2Form expects."""

    employee = Employee.objects.get(github_username="devuser")
    login(request, employee)

    request.session["github_id"] = 123456
    request.session["github_username"] = "devuser"
    request.session["github_name"] = "Dev User"
    request.session["github_email"] = "devuser@example.com"

    # Redirect to Step2View where the form is return redirect("registrations:step2")
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

    form_class = Step2Form
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
            for warning in form.warnings:
                if isinstance(warning, tuple) and len(warning) == 2:
                    field_name, message = warning
                    form.add_error(field_name, message)
                else:
                    form.add_error(None, warning)
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
            
            submitted_registration = (
                registration.Registrations.objects.current_registration()
            )

            if not submitted_registration:
                form.add_error(
                    None, "No registration form found for this semester."
                )
                return self.form_invalid(form)

            submission = registration.RegistrationSubmission.objects.create(
                registration=submitted_registration, participant=user
            )
            # TO DO: Validate dynamic parts of the form and save the answers to the database
            registration.Answer.save_from_cleaned_data(submission, form.cleaned_data)

        # Clean up session
        for key in [
            "github_id",
            "github_username",
            "github_name",
            "github_email",
        ]:
            if key in self.request.session:
                del self.request.session[key]

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
