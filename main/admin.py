from multiprocessing import Event
from django.contrib import admin
from .models import Lab,Slider,Sponsor,Research,New,Publication,Teaching,Database,NewsComment
admin.site.register(Lab)
admin.site.register(Slider)
admin.site.register(Sponsor)
admin.site.register(Research)
admin.site.register(New)
admin.site.register(Publication)
admin.site.register(Teaching)
admin.site.register(Database)
admin.site.register(NewsComment)