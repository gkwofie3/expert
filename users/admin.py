from multiprocessing import Event
from django.contrib import admin
from .models import User, Education,ResearchInterest,ResearchProject,Publication,ProfessionalExperience,AcademicAchievement,Award,AdminNote,Skill
admin.site.register(User)
admin.site.register(Education)
admin.site.register(ResearchInterest)
admin.site.register(ResearchProject)
admin.site.register(Publication)
admin.site.register(ProfessionalExperience)
admin.site.register(AcademicAchievement)
admin.site.register(Award)
admin.site.register(AdminNote)
admin.site.register(Skill)