# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
import pytz
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from urllib import request, response
# from .models import 
from . import this
import random,string,re,os, json
from PIL import Image
from django.utils.timezone import now
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
from django.utils.html import strip_tags
from datetime import datetime,timedelta,date
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.db.models import Q
from . import countries
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from .models import Publication,User,Award,ResearchInterest,ResearchProject,Education,AcademicAchievement,ProfessionalExperience,AdminNote,Skill,ResetTokens

# ##################################################################################

# Login view
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        next_url = request.GET.get("next", ("/users/me/"))  # Default to home if no 'next' provided
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password.")

    # If GET request, render the login page
    next_url = request.GET.get("next", reverse("index"))
    return render(request, "users/login.html", {"next": next_url})

# Logout view
def logout_view(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect(("login"))

def reset_password_request(request):
    if request.method=='POST':
        email=request.POST.get('email')
        username=request.POST.get('username')
        if User.objects.filter(email=email,username=username).exists():
            found_user=User.objects.get(email=email,username=username)
            name=f'{found_user.firstname} {found_user.surname}' 
            email=found_user.email
            username=found_user.username
            token=this.generate_token()
            ResetTokens.objects.create(token=token,user=found_user)
            allowed_hosts = settings.ALLOWED_HOSTS[0]
            if allowed_hosts =='127.0.0.1':
                allowed_hosts=f'{allowed_hosts}:8000'
            context={
                "name": name,
                "link": f'{allowed_hosts}/users/password-reset-confirm/{email}/{username}/{token}/',
            }
            this.send_custom_email(email,"Expert User Password Reset","users/password_reset_email.html",context)
            messages.success(request,'Reset link has been sent to your email')
            return redirect(request.path)
        else:
            messages.error(request,'No user account found for the credentials provided')
            return redirect('/users/password-reset/')
    elif request.method=="GET":
        return render(request,'users/password_reset.html')  
def password_reset_confirm(request,email,username,token):
    
    if ResetTokens.objects.filter(token=token):
        user=User.objects.get(email=email,username=username)
        reset_token=ResetTokens.objects.get(token=token)
        if reset_token.user==user:
            time_difference = now() - reset_token.datetime  
            total_minutes = time_difference.total_seconds() / 60
            if total_minutes>30:
                messages.error(request, f"Dear {user.firstname} {user.surname}, this reset token has expired. Kindly request for new token")
                return redirect('/users/password-reset/')
            elif reset_token.used==True:
                messages.error(request, f"Dear {user.firstname} {user.surname}, this reset token has been used. Kindly request for new token")
                return redirect('/users/password-reset/')
            else:
                if request.method=="GET":
                    messages.success(request,f"Dear {user.firstname} {user.surname}, enter new password to continue")
                    return render(request,'users/password_reset_confirm.html')
                elif request.method=='POST':
                    new_pass=request.POST.get('new_password')
                    conf_pass=request.POST.get('cpassword')
                    if new_pass != conf_pass:
                        messages.error(request,'Passwords do not match')
                        return redirect(request.path)
                    else: 
                        ResetTokens.objects.filter(token=token,user=user).update(used=True)
                        user.set_password(new_pass)
                        user.save()
                        messages.success(request,"Your password has been reset successfully, kindly login")
                        return redirect('/users/login/?next=/')
                else:
                    return HttpResponse("Invalid Request")
        else:
            messages.error(request,'This token was not generated for this user')
            return redirect('/users/password-reset//')
    else:
        messages.error(request,'The received token does not exist. Kindly visit the reset request page to request for new token')
        return redirect('/users/password-reset//')

# ##################################################################################
 


@login_required
def index(request):
    context=None
    return render(request,'users/index.html',context)
@login_required 
def me(request):
    context={}
    context=this.refreshDB(request)
    context['countries']=countries.countries
    user = request.user
    pexp=ProfessionalExperience.objects.filter(user=user) if ProfessionalExperience.objects.filter(user=user).exists() else None
    context.update({
        'educations': Education.objects.filter(user=user) if Education.objects.filter(user=user).exists() else None,
        'research_interests': ResearchInterest.objects.filter(user=user) if ResearchInterest.objects.filter(user=user).exists() else None,
        'project': ResearchProject.objects.filter(user=user).first(),  # No need for an existence check since `.first()` returns None if empty
        'publications': Publication.objects.filter(user=user) if Publication.objects.filter(user=user).exists() else None,
        'professional_experience': pexp,
        'academic_achievements': AcademicAchievement.objects.filter(user=user) if AcademicAchievement.objects.filter(user=user).exists() else None,
        'awards': Award.objects.filter(user=user) if Award.objects.filter(user=user).exists() else None,
        'admin_notes': AdminNote.objects.filter(user=user) if AdminNote.objects.filter(user=user).exists() else None,
        'skills': Skill.objects.filter(user=user) if Skill.objects.filter(user=user).exists() else None,
    })
    

    if request.method=="GET":
        return render(request,'users/me.html',context)
    elif request.method=="POST":
        action=request.POST['action']
        if action =='basic':
            # Collect form data
            surname = request.POST.get('surname', '').strip()
            firstname = request.POST.get('firstname', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            country = request.POST.get('country', '').strip()
            office = request.POST.get('office', '').strip()
            introduction = request.POST.get('introduction', '').strip()
            role = request.POST.get('role', '').strip()
            supervisor = request.POST.get('supervisor', '').strip()
            start_on = request.POST.get('start_on', '').strip()
            expected_graduation = request.POST.get('expected_graduation', '').strip()

            # Validation
            errors = {}
            if not surname:
                errors['surname'] = "Surname is required."
            if not firstname:
                errors['firstname'] = "Firstname is required."
            if not username:
                errors['username'] = "Username is required."
            if not email:
                errors['email'] = "Email is required."
            if not phone:
                errors['phone'] = "Phone number is required."
            if not country:
                errors['country'] = "Country is required."
            if not start_on:
                errors['start_on'] = "Start date is required."
            if not expected_graduation:
                errors['expected_graduation'] = "Expected graduation date is required."
            
            # Check date validation
            try:
                expected_graduation_date = datetime.strptime(expected_graduation, '%Y-%m').date()
                start_on_date = datetime.strptime(start_on, '%Y-%m').date()
                today = now().date()

                if expected_graduation_date <= start_on_date:
                    errors['expected_graduation'] = "Expected graduation date must be later than the start date."
                if expected_graduation_date <= today:
                    errors['expected_graduation'] = "Expected graduation date must be later than today."
            except ValueError:
                errors['start_on'] = "Invalid date format for start date."
                errors['expected_graduation'] = "Invalid date format for expected graduation."

            # If errors exist, render the form with errors
            if errors:
                messages.error(request, "There were errors in your form. Please fix them and try again.")
                return render(request, 'your_template.html', {'user': user, 'errors': errors})

            # Update user fields
            user.surname = surname
            user.firstname = firstname
            user.username = username
            user.email = email
            user.phone = phone
            user.country = country
            user.office = office
            user.introduction = introduction
            user.role = role
            user.supervisor = supervisor
            user.start_on = start_on_date
            user.experted_graduation = expected_graduation_date
            user.save()

            # Success message and redirect
            messages.success(request, "User details updated successfully!")
            return redirect(request.path)  # Replace with your success URL
        elif action =='change_profile_picture':
            newpic=request.FILES['profile_picture']
            user.profile_picture=newpic
            user.save()
            messages.success(request, "User profile picture updated successfully!")
            return redirect(request.path) 
        elif action =='change_illustrations_picture':
            newpic=request.FILES['illustrations_picture']
            user.illustrations_picture=newpic
            user.save()
            messages.success(request, "User illustration picture updated successfully!")
            return redirect(request.path) 
        elif action =='change_cv':
            newpic=request.FILES['cv']
            user.cv=newpic
            user.save()
            messages.success(request, "User CV updated successfully!")
            return redirect(request.path) 
        
        # education
        elif action =='add-edu':
            degree = request.POST.get('degree')
            program = request.POST.get('program')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            institution = request.POST.get('institution')
            GPA = request.POST.get('GPA')
            city = request.POST.get('city')
            country = request.POST.get('country')
            # Create and save the project for the logged-in user
            Education.objects.create(
                degree=degree,
                program=program,
                user=request.user,
                institution=institution,
                GPA=GPA,
                start_date=datetime.strptime(start_date, '%Y-%m').date(),
                end_date=datetime.strptime(end_date, '%Y-%m').date(),
                city=city,
                country=country,
            )
            messages.success(request, "Education record added successfully!")
            return redirect(request.path)
        elif action == 'edit-edu':
            id = request.POST.get('id')
            edu = get_object_or_404(Education, id=int(id))

            degree = request.POST.get('degree')
            program = request.POST.get('program')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            institution = request.POST.get('institution')
            GPA = request.POST.get('gpa')
            city = request.POST.get('city')
            country = request.POST.get('country')

            # Convert date strings to date objects
            try:
                start_date = datetime.strptime(start_date, '%Y-%m').date() if start_date else None
                end_date = datetime.strptime(end_date, '%Y-%m').date() if end_date else None
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM.")
                return redirect(request.path)

            # Ensure end date is later than start date
            if start_date and end_date and end_date < start_date:
                messages.error(request, "End date must be later than start date.")
                return redirect(request.path)

            # Assign values to the education instance
            edu.degree = degree
            edu.program = program
            edu.institution = institution
            edu.GPA = GPA if GPA else None  # Ensure GPA is stored as None if empty
            edu.start_date = start_date
            edu.end_date = end_date
            edu.city = city
            edu.country = country

            edu.save()  # Save the changes

            messages.success(request, "Education record updated successfully!")
            return redirect(request.path)
        elif action == 'delete-edu':
            id = request.POST.get('id')
            try:
                edu = Education.objects.get(id=int(id))
                edu.delete()
                messages.success(request, "Education record deleted successfully!")
            except Education.DoesNotExist:
                messages.error(request, "Education record not found.")
            except ValueError:
                messages.error(request, "Invalid ID provided.")
            return redirect(request.path)
        elif action=='research_update':
            project, created = ResearchProject.objects.get_or_create(user=user, defaults={
                "by": user.username,
                "title": "",  # Will be updated from form
                "keywords": [],
                "description": [],
                "start_date": None,
                "end_date": None,
                "status": "ongoing",
            })
            errors = []
            # Validate topic
            project_topic = request.POST.get("project_topic", "").strip()
            if not project_topic:
                errors.append("Research topic cannot be empty.")
            else:
                project.title = project_topic
            # Process descriptions
            updated_descriptions = []
            for desc in project.description:
                new_value = request.POST.get(f"project_descriptions_{desc}", "").strip()
                if not new_value:
                    errors.append(f"Description '{desc}' cannot be empty.")
                elif new_value not in updated_descriptions:
                    updated_descriptions.append(new_value)
            # Add new description if provided
            new_description = request.POST.get("new_project_descriptions", "").strip()
            if new_description:
                if new_description in updated_descriptions:
                    errors.append(f"Description '{new_description}' is already in the list.")
                else:
                    updated_descriptions.append(new_description)

            # Process keywords
            updated_keywords = []
            for key in project.keywords:
                new_value = request.POST.get(f"project_keywords_{key}", "").strip()
                if not new_value:
                    errors.append(f"Keyword '{key}' cannot be empty.")
                elif new_value not in updated_keywords:
                    updated_keywords.append(new_value)

            # Add new keyword if provided
            new_keyword = request.POST.get("new_project_keyword", "").strip()
            if new_keyword:
                if new_keyword in updated_keywords:
                    errors.append(f"Keyword '{new_keyword}' is already in the list.")
                else:
                    updated_keywords.append(new_keyword)

            # If there are errors, return them as messages and reload the page
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect(request.path)  # Reload page

            # Save updates if no errors
            project.description = updated_descriptions
            project.keywords = updated_keywords
            project.save()

            messages.success(request, "Project updated successfully.")
            return redirect(request.path)  # Reload page

            # ///////////////////////////
        elif action =='update_skills':
        # ////////////////////////////
            errors = []
            updated_skills = []

            # Validate and update existing skills
            for skill in Skill.objects.filter(user=user):
                skill_name = request.POST.get(f"skill_name_{skill.id}", "").strip()
                category = request.POST.get(f"category_{skill.id}", "").strip()
                proficiency = request.POST.get(f"proficiency_{skill.id}", "").strip()

                if not skill_name:
                    errors.append("Skill name cannot be empty.")
                elif skill_name in updated_skills:
                    errors.append(f"Duplicate skill '{skill_name}' is not allowed.")
                else:
                    updated_skills.append(skill_name)
                    skill.name = skill_name
                    skill.category = category
                    skill.proficiency_level = proficiency
                    skill.save()

            # Process new skill
            new_skill_name = request.POST.get("new_skill_name", "").strip()
            new_category = request.POST.get("new_category", "").strip()
            new_proficiency = request.POST.get("new_proficiency", "").strip()

            if new_skill_name:
                if new_skill_name in updated_skills:
                    errors.append(f"Skill '{new_skill_name}' already exists.")
                else:
                    Skill.objects.create(
                        user=user,
                        name=new_skill_name,
                        category=new_category,
                        proficiency_level=new_proficiency
                    )
                    messages.success(request, f"New skill '{new_skill_name}' added.")

            # Show errors if any 
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect(request.path)

            messages.success(request, "Skills updated successfully.")
            return redirect(request.path)
        
        elif action == "delete_pub":
            pub_id =int(request.POST.get('publication_id'))
            publication = Publication.objects.get(id=pub_id) if Publication.objects.filter(id=pub_id).exists() else None
            if publication is None:
                messages.error(request, "The requested publication does not exist.")
            publication.delete()
            messages.success(request, "Publication deleted successfully.")
            return redirect(request.path)  # Change this to your actual view name

        elif action == "update_pub":
            pub_id =int(request.POST.get('publication_id'))
            publication = Publication.objects.get(id=pub_id) if Publication.objects.filter(id=pub_id).exists() else None
            if publication is None:
                messages.error(request, "The requested publication does not exist.")
            title = request.POST.get("title", "").strip()
            publication_date = request.POST.get("date", "").strip()
            abstract = request.POST.get("abstract", "").strip()
            link = request.POST.get("link", "").strip()
            visibility = request.POST.get("visibility") == "True"
            pdf_file = request.FILES.get("pdf")

            errors = []

            # Validate required fields
            if not title:
                errors.append("Title is required.")
            if not publication_date:
                errors.append("Publication date is required.")
            if not abstract:
                errors.append("Abstract is required.")

            # Validate date format
            try:
                publication_date = now().strptime(publication_date, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Invalid date format.")

            # Validate link (if provided)
            if link:
                validate_url = URLValidator()
                try:
                    validate_url(link)
                except ValidationError:
                    errors.append("Invalid URL format.")

            # Validate PDF file (if uploaded)
            if pdf_file:
                if not pdf_file.name.endswith(".pdf"):
                    errors.append("Only PDF files are allowed.")
                if pdf_file.size > 10 * 1024 * 1024:  # 10MB limit
                    errors.append("PDF file size must not exceed 10MB.")

            # If there are errors, return to the form with messages
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect(request.path) # Replace with your template

            # Update fields
            publication.title = title
            publication.publication_date = publication_date
            publication.abstract = abstract
            publication.link = link
            publication.visibility = visibility

            # Only update the PDF if a new file is uploaded
            if pdf_file:
                publication.pdf = pdf_file

            publication.save()
            messages.success(request, "Publication updated successfully.")
            return redirect(request.path)  # Change to your actual view name
        elif action == "add_new_pub":            
            title = request.POST.get("title", "").strip()
            publication_date = request.POST.get("date", "").strip()
            abstract = request.POST.get("abstract", "").strip()
            link = request.POST.get("link", "").strip()
            visibility = request.POST.get("visibility") == "True"  # Convert to boolean
            pdf = request.FILES.get("pdf")  # Get the uploaded PDF file

            # Validate required fields
            if not title or not publication_date or not abstract:
                messages.error(request, "Title, Date, and Abstract are required fields.")
                return redirect(request.path)  # Redirect to the same page

            # Validate date format (optional, Django handles this well)
            try:
                publication_date = timezone.datetime.strptime(publication_date, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format.")
                return redirect(request.path)

            # PDF validation (if a file is uploaded)
            if pdf:
                if not pdf.name.lower().endswith(".pdf"):  # Ensure it's a PDF
                    messages.error(request, "Only PDF files are allowed.")
                    return redirect(request.path)

                if pdf.size > 10 * 1024 * 1024:  # Limit to 10MB
                    messages.error(request, "File size must not exceed 10MB.")
                    return redirect(request.path)

            # Save the publication
            publication = Publication.objects.create(
                user=request.user,
                title=title,
                publication_date=publication_date,
                abstract=abstract,
                link=link,
                pdf=pdf if pdf else None,  # Assign only if there's a file
                visibility=visibility,
            )
            messages.success(request, "Publication added successfully!")
            return redirect(request.path)  # Redirect to a list page
        
        elif action == "add_new_award":
            title = request.POST.get("title", "").strip()
            description = request.POST.get("description", "").strip()
            date = request.POST.get("date", "").strip()
            organization = request.POST.get("organization", "").strip()

            # Validate required fields
            if not title or not date:
                messages.error(request, "Title and Date are required.")
            else:
                Award.objects.create(
                    user=request.user,
                    title=title,
                    description=description if description else None,
                    date=date,
                    organization=organization if organization else None
                )
                messages.success(request, "Award added successfully.")

            return redirect(request.path)

        elif action == "update_award":
            award_id = request.POST.get("award_id")
            title = request.POST.get("title", "").strip()
            description = request.POST.get("description", "").strip()
            date = request.POST.get("date", "").strip()
            organization = request.POST.get("organization", "").strip()

            # Check if the award exists
            award = Award.objects.filter(id=award_id, user=request.user).first()

            if not award:
                messages.error(request, "The requested award does not exist.")
            elif not title or not date:
                messages.error(request, "Title and Date are required.")
            else:
                award.title = title
                award.description = description if description else None
                award.date = date
                award.organization = organization if organization else None
                award.save()
                messages.success(request, "Award updated successfully.")

            return redirect(request.path)

        elif action == "delete_award":
            award_id = request.POST.get("award_id")

            # Check if the award exists
            award = Award.objects.filter(id=award_id, user=request.user).first()

            if not award:
                messages.error(request, "The requested award does not exist.")
            else:
                award.delete()
                messages.success(request, "Award deleted successfully.")

            return redirect(request.path)
        elif action == "add_new_experience":
            title = request.POST.get("title", "").strip()
            institution = request.POST.get("institution", "").strip()
            description = request.POST.get("description", "").strip()
            start_date = request.POST.get("start_date", "").strip()
            end_date = request.POST.get("end_date", "").strip()
            city = request.POST.get("city", "").strip()
            country = request.POST.get("country", "").strip()
            show_month = request.POST.get("show_month") == "true"  # Convert to boolean

            description_list = description.replace('\r', '').split('\n')  # Remove '\r' and split by '\n'
            description_list = [line.strip() for line in description_list if line.strip()]  

            if not title:
                messages.error(request, "Title is required.")
            else:
                experience = ProfessionalExperience.objects.create(
                    user=request.user,
                    title=title,
                    institution=institution,
                    description=description_list,  # Store as JSON
                    start_date=start_date or None,
                    end_date=end_date or None,
                    city=city,
                    country=country,
                    show_month=show_month
                )
                messages.success(request, "Experience added successfully.")

        # Update Experience
        elif action == "update_experience":
            experience_id = request.POST.get("experience_id")
            experience = get_object_or_404(ProfessionalExperience, id=experience_id, user=request.user)

            experience.title = request.POST.get("title", "").strip()
            experience.institution = request.POST.get("institution", "").strip()
            description = request.POST.get("description", "").strip()
            experience.start_date = request.POST.get("start_date", "").strip() or None
            experience.end_date = request.POST.get("end_date", "").strip() or None
            experience.city = request.POST.get("city", "").strip()
            experience.country = request.POST.get("country", "").strip()
            experience.show_month = request.POST.get("show_month") == "true"  # Convert to boolean

            # Convert to JSON list
            description_list = description.replace('\r', '').split('\n')  # Remove '\r' and split by '\n'
            experience.description = [line.strip() for line in description_list if line.strip()]  # Remove empty lines

            experience.save()
            messages.success(request, "Experience updated successfully.")

        # Delete Experience
        elif action == "delete_experience":
            experience_id = request.POST.get("experience_id")
            experience = get_object_or_404(ProfessionalExperience, id=experience_id, user=request.user)
            experience.delete()
            messages.success(request, "Experience deleted successfully.")

        return redirect(request.path)  # Refresh the page

    else:
        return HttpResponse('Invalid action value received')

