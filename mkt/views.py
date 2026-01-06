#from django.shortcuts import render

# Create your views here.
from mkt.models import Ad
from mkt.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView


class AdListView(OwnerListView):
    model = Ad
    # By convention:
    # template_name = "mkt/article_list.html"


class AdDetailView(OwnerDetailView):
    model = Ad

class AdCreateView(OwnerCreateView):
    model = Ad
    # List Article model fields to copy to the Article form / template
    fields = ['title', 'price','text']

class AdUpdateView(OwnerUpdateView):
    model = Ad
    fields = ['title', 'price', 'text']


class AdDeleteView(OwnerDeleteView):
    model = Ad