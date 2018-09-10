from django_elasticsearch_dsl import DocType, Index, TextField
from .models import Spot

spot = Index('spot')

@spot.doc_type
class SpotDocument(DocType):
    class Meta:
        model = Spot
        fields = [
            'title'
        ]
        reviews = TextField()

        def prepare_reviews(self, instance):
            return [s.title + s.content for s in instance.reviews()]
