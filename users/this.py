from .models import Publication,User,Award,ResearchInterest
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def refreshDB(request):
    context={}
    users=User
    awards=Award.objects.all()
    context['users']=users
    context['awards']=awards
    context['user']=request.user
    context['user']=request.user
    return context

def send_custom_email(recipient_email, subject, template_name, context):
    # Render the HTML email template
    html_content = render_to_string(template_name, context)
    plain_text_content = strip_tags(html_content)  # Remove HTML tags for a plain-text fallback

    # Create email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text_content,  # Plain text version
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email]
    )
    
    email.attach_alternative(html_content, "text/html")  # Attach HTML content
    email.send()
def generate_token():
    import secrets
    random_string = secrets.token_hex(16)
    return(random_string)
