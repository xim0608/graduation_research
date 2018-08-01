from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
# from django.http import request
from .models import Spot
from graduation_research.lib.recommend import Recommend
from graduation_research.lib.multi_spots_recommend import MultiSpotsRecommend
from graduation_research.lib.multiple_instance_recommend import MultipleInstanceRecommend
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import SpotSerializer
from silk.profiling.profiler import silk_profile


# r1_recommend_method = 'normalize_except_proper_nouns_fix_area'
# r2_recommend_method = 'normalize_except_nouns'
# r1 = Recommend(r1_recommend_method)
# r2 = Recommend(r2_recommend_method)
# recommend_instances = [r1, r2]

# multiple_recommend_instance = MultipleInstanceRecommend(recommend_instances, [0.5, 0.5])
r = Recommend('normalize_nouns_and_adjectives_except_area_nouns_and_station_for_interrim_presentation_wo_english_8')
msr = MultiSpotsRecommend(r)


class SpotListView(ListView):
    model = Spot


class SpotDetailView(DetailView):
    model = Spot


def search(request):
    return render(request, 'index.html', {})


class SpotListAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SpotSerializer
    queryset = Spot.objects.filter(count__gt=5)


@silk_profile(name='recommend search')
def search_api(request):
    spots_id = request.GET.get('id[]')
    spots_id = [int(i) for i in spots_id]
    if spots_id:
        spots = msr.find(spot_ids=spots_id)
        s = SpotSerializer(spots, many=True)
        print(s.data)
        to_json = {
            'recommends': s.data
        }
        return JsonResponse(to_json)
    else:
        return HttpResponse(status=204)
