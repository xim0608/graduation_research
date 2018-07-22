# from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
# from django.http import request
from .models import Spot
from graduation_research.lib.recommend import Recommend
from graduation_research.lib.multi_spots_recommend import MultiSpotsRecommend
from graduation_research.lib.multiple_instance_recommend import MultipleInstanceRecommend
from .serializers import SpotSerializer


class SpotListView(ListView):
    model = Spot


class SpotDetailView(DetailView):
    model = Spot


# 一時的にcsrf無効化
@csrf_exempt
def search(request):
    if request.method == 'GET':
        return HttpResponse("スポット検索画面")
    elif request.method == 'POST':
        spots_id = request.POST.getlist('spots_id')
        spots_id = [int(i) for i in spots_id]
        print(spots_id)
        if spots_id:
            recommend_instances = [Recommend('normalize_except_proper_nouns_fix_area'), Recommend('normalize_except_nouns')]
            multiple_recommend_instance = MultipleInstanceRecommend(recommend_instances, [0.5, 0.5])
            msr = MultiSpotsRecommend(multiple_recommend_instance)
            spots = msr.find(spots_id)
            s = SpotSerializer(spots, many=True)
            print(s.data)
            to_json = {
                'recommends': s.data
            }
            return JsonResponse(to_json)
        else:
            return HttpResponse(status=204)
# @staff_member_required
# # /spots/search
# def search(request):
#     return HttpResponse("スポット検索画面")
