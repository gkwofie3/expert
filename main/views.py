# Create your views here.
from django.shortcuts import render,redirect
from django.utils import timezone
import pytz
from django.http import HttpResponse,JsonResponse
from urllib import request, response
from django.contrib import messages
# from .models import
from . import this
import random
import string
from io import BytesIO
import re
import os
from collections import defaultdict
from django.conf import settings
from django.shortcuts import get_object_or_404
from datetime import datetime,timedelta,date
from django.apps import apps
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Slider,Lab,Slider,Sponsor,Research,New,Publication,Teaching,Database,NewsComment
from users.models import Publication as userpubs,User,Award,ResearchInterest,ResearchProject,Education,AcademicAchievement,ProfessionalExperience,AdminNote,Skill

from django.utils.timezone import now

def index(request):
    context=None
    context=this.refreshDB()
    context['page_title']='EXPERT'
    return render(request,'main/index.html',context)
def home(request):
    hum=User.objects.all()
    for per in hum:
        User.objects.filter(id=per.id).update(
        experted_graduation=now().date())
    return render(request, 'main/home.html')

def people(request):
    context=None
    context=this.refreshDB()
    context['page_title']='People || Expert'
    people=User.objects.all()
    for per in people:
        if per.username =='admin':
            firstname="_".join((per.firstname).split())
            surname="_".join((per.surname).split())
            random_text = (''.join(random.choices(string.ascii_letters, k=3))).lower()
            username=(f'{firstname}_{surname}_{random_text}').lower()
            User.objects.filter(id=per.id).update(username=username)
        introduction = (
                            f"{per.firstname} {per.surname} is a prominent researcher in power electronics, specializing in energy conversion "
                            "and renewable energy systems. With a PhD in Electrical Engineering from [Prestigious University], "
                            f"{per.firstname} {per.surname} has significantly advanced high-efficiency power management and grid integration of renewables.\n\n"

                            f"{per.firstname} {per.surname} has authored numerous papers, presented at international conferences, and collaborated with industry "
                            "leaders to drive advancements in power systems. Currently, they lead projects on solid-state transformers and modular converters, "
                            "fostering innovation and mentoring future engineers to contribute to a sustainable energy future."
                        )
        User.objects.filter(id=per.id).update(introduction=introduction)
    return render(request, 'main/people.html',context)
def person(request,username):
    context=None
    context=this.refreshDB()
    try:
        person = User.objects.get(username=username)

        context['person']=person
        user_skills = Skill.objects.filter(user=person)
        skill_groups = []
        for skill in user_skills:
            if skill.category not in skill_groups:
                skill_groups.append(skill.category)

        context.update({
            'educations': Education.objects.filter(user=person) or None,
            'research_interests': ResearchInterest.objects.filter(user=person) or None,
            'project': ResearchProject.objects.filter(user=person).first() if ResearchProject.objects.filter(user=person).exists() else None,
            'publications': Publication.objects.filter(user=person) or None,
            'profession_experience': ProfessionalExperience.objects.filter(user=person) or None,
            'academic_achievements': AcademicAchievement.objects.filter(user=person) or None,
            'awards': Award.objects.filter(user=person) or None,
            'admin_notes': AdminNote.objects.filter(user=person) or None,
        })

        context['skill_groups']=skill_groups
        context['user_skills']=user_skills
        context['page_title']=f'{person.firstname} {person.surname}|| Expert '
        return render(request, 'main/person-page.html',context)
    except User.DoesNotExist:
        # Handle the case where the user does not exist
        person = None
    return HttpResponse('User not found')
        

def research(request):
    context=None
    context=this.refreshDB()
    context['page_title']='Research || Expert'
    return render(request, 'main/research.html',context)
def research_view(request,id):
    context=None
    context=this.refreshDB()

    if Research.objects.filter(id=id).exists():
        res=Research.objects.get(id=id)
    else:
        return redirect('/research/')
    
    
    context['page_title']=f' Research - {res.title}'
    context['research']=res
    return render(request, 'main/research_view.html',context)

def news(request):
    context=None
    context=this.refreshDB()
    context['page_title']='News || Expert'
    return render(request, 'main/news.html',context)
def news_read(request,id):
    if New.objects.filter(id=id).exists():
        this_news=New.objects.get(id=id)
    else:
        return redirect('/news/')
    context=None
    context=this.refreshDB()
    comments=NewsComment.objects.filter(post=this_news, is_visible=True)
    context['page_title']=this_news.title
    context['thisnews']=this_news
    context['comments']=comments
    if request.method =='GET':
        return render(request, 'main/news_read.html',context)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        # Backend Validations
        if not name:
            messages.error(request, "Name is required.")
        elif len(name) < 6:
            messages.error(request, "Name must be at least 6 characters.")
        elif not email:
            messages.error(request, "Email is required.")
        else:
            try:
                validate_email(email)  
            except ValidationError:
                messages.error(request, "Invalid email format.")

        if not message:
            messages.error(request, "Message cannot be empty.")
        elif len(message) < 5:
            messages.error(request, "Message must be at least 5 characters.")
        # If no errors, save the comment
        if not messages.get_messages(request):
            comment = NewsComment(post=this_news, name=name, email=email, message=message)
            comment.save()
            messages.success(request, "Your comment has been submitted and is awaiting approval.")
            return redirect(request.path)  # Avoid resubmission

        return redirect(request.path)

def publications(request):
    context=None
    context=this.refreshDB()
    context['page_title']='Publications || Expert'
    return render(request, 'main/publications.html',context)
def publications_year(request,year):
    context=None
    context=this.refreshDB()
    pubby=Publication.objects.filter(publication_date__year=year)
    context['pubby']=pubby
    context['year']=year

    context['page_title']='Publications || Expert'
    return render(request, 'main/pubby.html',context)

def teaching(request):
    return render(request, 'teaching.html')

def highlights(request):
    return render(request, 'highlights.html')

def database(request):
    return render(request, 'database.html')

def join(request):
    return render(request, 'join.html')
