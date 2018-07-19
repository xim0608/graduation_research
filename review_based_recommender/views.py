# from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
# /spots/search
def search(request):
    return HttpResponse("スポット検索画面")
