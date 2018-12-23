from django.db.models import F
from django.http.response import JsonResponse
from django.views.generic import TemplateView

from .models import Parts, Alternatives


class IndexView(TemplateView):
    template_name = 'index.html'


class PartsView(TemplateView):
    template_name = 'parts.html'

    def get_context_data(self, **kwargs):
        context = super(PartsView, self).get_context_data(**kwargs)
        parts_list = list(Parts.objects.filter(alternatives=None).values('name', 'count', 'mustbe', 'arrive'))
        for alt in Alternatives.objects.all():
            parts_list.append(alt.alt_parts)
        context['parts_list'] = parts_list
        return context


def missing_parts(request):
    parts = Parts.objects.annotate(shortage=F('mustbe') - (F('count') + F('arrive'))
                                   ).filter(shortage__gt=0).values_list('name', 'shortage')
    result = dict(parts)
    return JsonResponse(result)
