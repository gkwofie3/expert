from pyexpat import model
from datetime import datetime,timedelta,date
from django.db import models
from django.utils import timezone
import pytz
timezone.now()
now = datetime.now()
import os

class Lab(models.Model): 
    name = models.CharField(max_length=225, default='ExPERT Lab')
    logo = models.FileField(upload_to='lab')
    about = models.TextField()
    mission = models.TextField()
    vision = models.TextField()
    values = models.TextField()

    # Additional fields for a university research lab
    established_date = models.DateField(null=True, blank=True, help_text="Date the lab was established")
    head = models.CharField(max_length=225, help_text="Lab head or director's name")
    contact_email = models.EmailField(help_text="Primary contact email for the lab")
    contact_phone = models.CharField(max_length=15, null=True, blank=True, help_text="Primary contact phone number")
    location = models.CharField(max_length=225, help_text="Lab's physical location on campus")
    website = models.URLField(null=True, blank=True, help_text="Lab's official website")
    
    # Research-specific fields
    research_focus = models.TextField(help_text="Main research areas and focus of the lab")
    affiliated_department = models.CharField(max_length=225, help_text="Department the lab is affiliated with")

    # Facilities and resources
    equipment = models.TextField(help_text="List of major equipment or facilities available in the lab", null=True, blank=True)
    funding_sources = models.CharField(max_length=500, null=True, blank=True, help_text="Primary sources of funding")
    
    # Team and social media
    team_members = models.TextField(help_text="Key team members and their roles", null=True, blank=True)
    social_media_links = models.JSONField(null=True, blank=True, help_text="Social media links as JSON (e.g., {'twitter': 'link', 'linkedin': 'link'})")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
class Slider(models.Model):
    title = models.CharField(max_length=255,blank=True, null=True, help_text="Title of the slider item")
    description = models.TextField(help_text="Description or caption for the slider item", blank=True, null=True)
    image = models.ImageField(upload_to='slider', help_text="Image for the slider item")
    link = models.CharField(max_length=225,blank=True, null=True, help_text="Optional link associated with the slider item")
    align=models.TextField()
    display_title=models.BooleanField(default=True)
    index=models.IntegerField(verbose_name='Order number')
    def __str__(self):
        return self.title
class Sponsor(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the sponsor")
    logo = models.ImageField(upload_to='sponsors', help_text="Logo of the sponsor")
    website = models.TextField(blank=True, null=True, help_text="Sponsor's website URL")
    description = models.TextField(blank=True, null=True, help_text="Brief description about the sponsor")
    support_level = models.CharField(max_length=100, blank=True, null=True, help_text="Level of sponsorship (e.g., Platinum, Gold)")
    added_on = models.DateField(auto_now_add=True)
    index=models.IntegerField(verbose_name='Order Number In cardinal')


    def __str__(self):
        return self.name
from django.db import models


class Research(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    pic=models.ImageField(upload_to='main/researchs',null=True,default='/pubbg.jpg')
    bullet_points=models.JSONField(default=list, null=True)
    lead_researcher = models.TextField(null=True)
    collaborators = models.JSONField(null=True,blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True)
    funding_agency = models.CharField(max_length=255, blank=True, null=True)
    funding_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    outcomes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class New(models.Model):
    # Define choices for the news categories
    PUBLICATION = 'publication'
    EVENT = 'event'
    GRANT = 'grant'
    ACHIEVEMENT = 'achievement'
    COLLABORATION = 'collaboration'
    NEWS_CATEGORY_CHOICES = [
        (PUBLICATION, 'Publication'),
        (EVENT, 'Event'),
        (GRANT, 'Grant/Funding'),
        (ACHIEVEMENT, 'Achievement'),
        (COLLABORATION, 'Collaboration'),
    ]

    title = models.CharField(max_length=255)
    intro = models.TextField()
    body = models.TextField()
    conclusion = models.TextField()
    publication_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=255)
    number_of_times_read= models.IntegerField(default=1)
    featured_image_1 = models.ImageField(upload_to='news/image1/', blank=True, null=True)
    featured_image_2 = models.ImageField(upload_to='news/image2/', blank=True, null=True)
    featured_image_3 = models.ImageField(upload_to='news/image3/', blank=True, null=True)
    featured_video = models.FileField(upload_to='news/video/', blank=True, null=True)
    category = models.CharField(
        max_length=20,
        choices=NEWS_CATEGORY_CHOICES,
        default=PUBLICATION,  # Default category
    )
    newstags = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publication_date'] 
class NewsComment(models.Model):
    post = models.ForeignKey('New', on_delete=models.CASCADE, related_name="newscomments")  # Link to news post
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=False)  # Admin control for visibility

    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"


class Publication(models.Model):
    title = models.CharField(max_length=255)
    publication_date = models.DateField()
    abstract = models.TextField()
    pdf = models.FileField(upload_to='publications/', blank=True, null=True)
    link=models.URLField(blank=True, null=True)
    
class Teaching(models.Model):
    course_name = models.CharField(max_length=255)
    instructor = models.CharField(max_length=225)
    semester = models.CharField(max_length=20)
    syllabus = models.TextField()
    materials = models.FileField(upload_to='teaching/materials/', blank=True, null=True)

    def __str__(self):
        return f"{self.course_name} - {self.semester}"



class Database(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    dataset_file = models.FileField(upload_to='datasets/', blank=True, null=True)

    def __str__(self):
        return self.name
