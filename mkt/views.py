#from django.shortcuts import render

# Create your views here.
from mkt.models import Ad,Comment, Fav
from mkt.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
#v2 start
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from mkt.forms import CreateForm
from mkt.forms import CommentForm
# V2 end

class AdListView(OwnerListView):
    model = Ad
    # By convention:
    template_name = "mkt/ad_list.html"
    #Code for release 4: Retreive the list of favourites for the current user
    def get(self, request) :
        ad_list = Ad.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            favorites = list(request.user.favwc_favorite_ads.values_list('ad__id', flat=True))
        print(favorites)
        ctx = {'ad_list' : ad_list, 'favorites': favorites}
        return render(request, self.template_name, ctx)

class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "mkt/ad_detail.html"
    def get(self, request, pk) :
        x = get_object_or_404(Ad, id=pk)
        comments = Comment.objects.filter(ad=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'ad' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)

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
    model = Ad
    fields = ['title', 'price', 'text']
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

#New stuff for the comments in release 3 starts here
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
        comment.save()
        return redirect(reverse('mkt:ad_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "mkt/ad_comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        ad = self.object.ad
        return reverse('mkt:ad_detail', args=[ad.id])

#New stuff for the comments in release 3 ends here

def stream_file(request, pk):
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = ad.content_type
    response['Content-Length'] = len(ad.picture)
    response.write(ad.picture)
    return response

#New version 4 stuff
#Favourrite code for the toggling of the favourites to update the database:
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AdToggleView(LoginRequiredMixin, View):
    # Add get for manual retrieval

    def post(self, request, pk) :
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()
            return HttpResponse("Favorite added 42")
        except IntegrityError:  # Already there, lets delete...
            Fav.objects.get(user=request.user, ad=t).delete()
            return HttpResponse("Favorite deleted 42")
        return HttpResponse("Something went wrong")
