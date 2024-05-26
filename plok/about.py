import os
from django.conf import settings
from django.views.generic import TemplateView
from markdown import markdown


class AboutView(TemplateView):
    template_name = 'plok/about.html'

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        readme_path = os.path.join(settings.BASE_DIR, 'README.md')
        about_file = open(readme_path, 'r')
        about_content = about_file.read()
        about_file.close()
        about_text = markdown(about_content)

        context['about_text'] = about_text
        return context
