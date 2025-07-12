from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, surname, firstname, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required.")
        if not surname:
            raise ValueError("The Surname field is required.")
        if not firstname:
            raise ValueError("The Firstname field is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, surname=surname, firstname=firstname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, surname, firstname, password=None):
        extra_fields = {'is_admin': True, 'is_superuser': True, 'is_staff': True}
        return self.create_user(email, surname, firstname, password, **extra_fields)


# Main User model
class User(AbstractBaseUser, PermissionsMixin):
    # Basic info for authentication
    email = models.EmailField(unique=True, max_length=255)
    surname = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    username = models.CharField(max_length=255, default="admin")
    country = models.CharField(max_length=255, default='USA')
    office = models.CharField(max_length=255, default='Expert Lab')
    introduction = models.TextField(default=' ')
    phone = models.CharField(max_length=15, blank=True, null=True)
    cv = models.FileField(upload_to='users/cv', null=True, blank=True)
    profile_picture = models.ImageField(upload_to='users/profile_pics', default='default/user.jpg', null=True, blank=True)
    illustrations_picture = models.ImageField(upload_to='users/illustrations_pics', default='default/user.jpg', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # To allow admin-level access
    is_admin = models.BooleanField(default=False)
    theme = models.CharField(max_length=20, default="light")  # UI theme preferences
    role = models.CharField(max_length=20, choices=[
        ('principal', 'Principal'),
        ('undergraduate', 'Undergraduate'),
        ('phd', 'PhD Student'),
        ('master', 'Master\'s Student'),
        ('postdoc', 'Postdoc'),
        ('phdalumni', 'PhD Alumnus'),
        ('msalumni', "Master's Alumnus"),
        ('ugalumni', "Undergraduate Alumnus")
    ], default='researcher')
    
    # Academic and professional details
    department = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)

    thesis = models.TextField(blank=True, null=True)
    master_thesis = models.TextField(blank=True, null=True)
    supervisor = models.CharField(max_length=255, blank=True, null=True)
    start_on = models.DateField(blank=True, null=True)
    experted_graduation = models.DateField(default=timezone.now,blank=True, null=True)
    
    # Contact details and social media
    website = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    personal_email = models.EmailField(blank=True, null=True)

    # Admin-related fields (only for admin users)
    notifications = models.IntegerField(default=0)
    messages = models.IntegerField(default=0)
    # Project and research status (PhD, Masters, Postdoc)
    project_status = models.CharField(max_length=255, blank=True, null=True)  # Ongoing/Completed
    funding_source = models.CharField(max_length=255, blank=True, null=True)
    grant_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Resolve reverse accessor clashes
    groups = models.ManyToManyField('auth.Group', related_name='user_set_custom', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='user_permissions_custom', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['surname', 'firstname']

    objects = UserManager()

    def __str__(self):
        return f"{self.firstname} {self.surname} ({self.email})"

    def get_full_name(self):
        return f"{self.firstname} {self.surname}"

    def get_short_name(self):
        return self.firstname

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class ResearchInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='research_interests')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Publication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='publications')
    title = models.CharField(max_length=255)
    publication_date = models.DateField(default=timezone.now)
    abstract = models.TextField()
    pdf = models.FileField(upload_to='publications/', blank=True, null=True)
    link=models.URLField(blank=True, null=True)    
    visibility=models.BooleanField(default=False)

    def __str__(self):
        return self.title
class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='education')
    degree = models.CharField(max_length=255)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    program = models.CharField(max_length=255, blank=True, null=True)
    institution = models.TextField(blank=True, null=True)
    GPA = models.CharField(max_length=224,blank=True, null=True)
    city=models.CharField(max_length=255)
    country=models.CharField(max_length=255)
    show_month=models.BooleanField(default=True)
    def __str__(self):
        return f'{self.user} {self.degree} {self.program}'


class ResearchProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='research_projects')
    by = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    keywords = models.JSONField(null=True)
    description = models.JSONField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[('ongoing', 'Ongoing'), ('completed', 'Completed')], default='ongoing')

    def __str__(self):
        return self.title

class AcademicAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='academic_achievements')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title


class Award(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='awards')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

class AdminNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='admin_notes')
    title = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
class ProfessionalExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='professional_experience')
    title = models.CharField(max_length=255)
    city = models.CharField(max_length=255,default="")
    country = models.CharField(max_length=255, default="")
    show_month=models.BooleanField(default=True)
    institution = models.CharField(max_length=255,null=True)
    description = models.JSONField(blank=True, null=True, default=dict)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title


class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='skills')
    name = models.CharField(max_length=100)
    category=models.CharField(max_length=100,choices=[
            ('Software', 'Software'),
            ('Hardware', 'Hardware'),
            ('Tools', 'Tools'),
        ],
        default='beginner')
    proficiency_level = models.CharField(
        max_length=50, 
        choices=[
            ('beginner', 'Beginner'), 
            ('intermediate', 'Intermediate'), 
            ('advanced', 'Advanced'), 
            ('expert', 'Expert')
        ],
        default='beginner'
    )

    def __str__(self):
        return f"{self.name} ({self.proficiency_level.capitalize()})"
class ResetTokens(models.Model):
    token=models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='resettokens')
    datetime=models.DateTimeField(auto_now_add=True)
    used=models.BooleanField(default=False)