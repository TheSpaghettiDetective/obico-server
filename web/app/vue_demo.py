from django.views.generic import TemplateView


class SimpleAppView(TemplateView):
    template_name = "vue-demo/simple.html"


class MultiAppView(TemplateView):
    template_name = "vue-demo/multi.html"
