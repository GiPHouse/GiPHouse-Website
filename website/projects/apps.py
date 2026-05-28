from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """AppConfig for projects app."""

    name = "projects"
    import components.semester_projects.component
