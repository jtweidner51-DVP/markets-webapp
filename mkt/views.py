#from django.shortcuts import render

# Create your views here.
from mkt.models import Ad
from mkt.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
#v2 start
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from mkt.forms import CreateForm
# V2 end

class AdListView(OwnerListView):
    model = Ad
    # By convention:
    template_name = "mkt/ad_list.html"


class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "mkt/ad_detail.html"

class AdCreateView(LoginRequiredMixin, View):
    #v1 code: model = Ad
    # List Article model fields to copy to the Article form / template
    #v1 code: fields = ['title', 'price','text']
    template_name = 'mkt/ad_form.html'
    success_url = reverse_lazy('mkt:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        Ad = form.save(commit=False)
        Ad.owner = self.request.user
        Ad.save()
        return redirect(self.success_url)



class AdUpdateView(LoginRequiredMixin, View):
    #model = Ad
    #fields = ['title', 'price', 'text']
    template_name = 'mkt/ad_form.html'
    success_url = reverse_lazy('mkt:all')

    def get(self, request, pk):
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=ad)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        ad = get_object_or_404(Ad , id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=ad)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        ad = form.save(commit=False)
        ad.save()

        return redirect(self.success_url)


class AdDeleteView(OwnerDeleteView):
    model = Ad
    template_name="mkt/ad_confirm_delete.html"

def stream_file(request, pk):
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = ad.content_type
    response['Content-Length'] = len(ad.picture)
    response.write(ad.picture)
    return response