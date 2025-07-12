from .models import Slider,Lab,Slider,Sponsor,Research,New,Publication,Teaching,Database
from users.models import User

from collections import defaultdict
from django.db.models.functions import ExtractYear
from main.models import Publication
from django.conf import settings

def publication_view():
    # Get all publications, sorted by year (descending) and then by date (descending)
    publications = Publication.objects.all().order_by('-publication_date')
    # Organize publications by year
    publications_by_year = defaultdict(list)
    for pub in publications:
        year = pub.publication_date.year  # Extract year from publication_date
        publications_by_year[year].append(pub)
    # Convert to a normal dictionary and sort by year (newest first)
    publications_by_year = dict(sorted(publications_by_year.items(), reverse=True))    
    return publications_by_year


def refreshDB():
    context=None
    sliders = Slider.objects.all()
    labs = Lab.objects.first()
    sponsors = Sponsor.objects.all().order_by('index')
    researches = Research.objects.all()
    news = New.objects.all()
    publications = Publication.objects.all()
    teachings = Teaching.objects.all()
    databases = Database.objects.all()
    people= User.objects.all()

    context = {
        'sliders': sliders,
        'lab': labs,
        'sponsors': sponsors,
        'researches': researches,
        'news': news,
        'publications': publication_view(),
        'teachings': teachings,
        'people': people,
        'databases': databases,
        'host':settings.ALLOWED_HOSTS[0]
    }
    return context
