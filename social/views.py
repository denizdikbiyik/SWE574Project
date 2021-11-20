from django.shortcuts import render
from django.views import View
from .models import Service
from .forms import ServiceForm

class ServiceListView(View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.all().order_by('-createddate')
        form = ServiceForm()

        context = {
            'service_list': services,
            'form': form,
        }

        return render(request, 'social/service_list.html', context)
    
    def post(self, request, *args, **kwargs):
        services = Service.objects.all().order_by('-createddate')
        form = ServiceForm(request.POST)

        if form.is_valid():
            new_service = form.save(commit=False)
            new_service.creater = request.user
            new_service.save()

        context = {
            'service_list': services,
            'form': form,
        }

        return render(request, 'social/service_list.html', context)
