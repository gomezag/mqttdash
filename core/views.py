from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import environ
from .models import *
env = environ.Env()
# Create your views here.


def index(request, **kwargs):
    template_name = "dash1.html"
    session = request.session

    demo_count = session.get('django_plotly_dash', {})

    ind_use = demo_count.get('ind_use', 0)
    ind_use += 1
    demo_count['ind_use'] = ind_use
    session['django_plotly_dash'] = demo_count

    # Use some of the information during template rendering
    context = {'ind_use' : ind_use}

    return render(request, template_name=template_name, context=context)

@login_required(login_url='/accounts/login?next=/control')
def control(request):
    template_name = "control.html"
    ws_url = env('DATASOCKET_URL')
    return render(request, template_name=template_name,
                  context={
                      'ws_url': ws_url,
                  })


@login_required(login_url='/accounts/login?next=/control')
def live_view(request):
    template_name = "live_view.html"
    ws_url = env('DATASOCKET_URL')
    current = dict()
    for loc in ['T', 'TO','H','HO','P1','P2','P3','NB']:
        current[loc] = Dato.objects.get(location=loc).valor
    return render(request, template_name=template_name,
                  context={
                      'ws_url': ws_url,
                      'data': current,
                  })
