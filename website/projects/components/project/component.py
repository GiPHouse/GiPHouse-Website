from django_components import component

@component.register("project")
class Project(component.Component):
    template_name = "project/template.html"

    def get_context_data(self, project):
        return {
            'project': project,
        }
