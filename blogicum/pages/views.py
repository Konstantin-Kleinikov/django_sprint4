from django.views.generic import TemplateView


class AboutPage(TemplateView):
    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'


class TokenErrorPage(TemplateView):
    template_name = 'pages/403csrf.html'


class NotFoundPage(TemplateView):
    template_name = 'pages/404.html'


class ServerErrorPage(TemplateView):
    template_name = 'pages/500.html'
