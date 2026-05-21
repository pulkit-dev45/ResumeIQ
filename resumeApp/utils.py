from django.conf import settings
import PyPDF2
from django.http import JsonResponse
from docx import Document
def parsedResume(file):
    filename=file.name.lower()
    if filename.endswith(".pdf"):
        return parsingResume(file)
    elif filename.endswith('.docx'):
        return parsingDocx(file)
    else:
        raise ValueError("Unsupported file format")
    

def parsingResume(file):
    reader=PyPDF2.PdfReader(file)
    text=""
    for page in reader.pages:
        text+=page.extract_text() or ""
    return text


def parsingDocx(file):
    doc=Document(file)
    para=""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return para


from django.core.mail import send_mail

def send_welcome_email(user):
    try:
        send_mail(
            subject="🚀 Welcome to Resume AI – Let’s build your future!",
            message=f"""
    Hey {user.username} 👋

    Welcome to Resume AI 🎉

    We’re super excited to have you on board.

    Here’s what you can do now:
    ✔ Upload your resume
    ✔ Get AI-powered ATS score
    ✔ Improve your chances of getting hired

    We built this tool to help you crack interviews faster and smarter 🚀

    If you ever need help, just reach out — we’ve got your back.

    Let’s build your career together 💼🔥

    – Team ResumeIQ
    """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Email failed: {e}")



def send_purchase_email(user):
    send_mail(
        subject=f"🎉 Payment Successful – Welcome to {user.profile.plan} Plan!",
        message=f"""
Hey {user.username} 👋

Thank you for purchasing our {user.profile.plan} plan 🚀

Your account has been updated successfully.

✨ Plan Activated: {user.profile.plan}
💳 Your total Credits: {user.profile.credits}

Now you can start analyzing resumes without limits 🔥

We’re excited to help you grow your career 💼

If you need any help, just reply to this email.

– Team ResumeIQ
""",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )

def custom_ratelimit_error(request, exception):
    return JsonResponse({
        "error": "Too many login attempts. Try again later."
    }, status=429)