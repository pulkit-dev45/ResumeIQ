from django.shortcuts import redirect, render
from rest_framework.views import APIView
from rest_framework import status
from django.utils.decorators import method_decorator
import json
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import AllowAny
from django.conf import settings
import re
import os
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User
from rest_framework.response import Response
from .serializers import ResumeSerializer
from .utils import parsedResume , send_welcome_email,send_purchase_email,custom_ratelimit_error
from django.http import JsonResponse
from django_ratelimit.exceptions import Ratelimited


from rest_framework.authentication import SessionAuthentication
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)    
import google.generativeai as genai
genai.configure(api_key=settings.GEMINI_API_KEY)
model=genai.GenerativeModel("gemini-2.5-flash")

def home(request):
    credits = request.user.profile.credits if request.user.is_authenticated else 0
    return render(request, 'h4.html', {'credits': credits})
@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='post')  
class Resumeanalyzing(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    @csrf_exempt
    def post(self,request):
        user=request.user
        if not user.is_authenticated:
            free_uses=request.session.get("free_uses",2)
            if free_uses<=0:
                return Response({"error":"Free limits over,No credits Remaining"})
        else:
            profile=user.profile
            if profile.credits<=0:
                return Response({"error": "No credits left. Upgrade plan."})
        serializer=ResumeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        try:
            resumeFile=serializer.validated_data["resume"]
            jd_text=serializer.validated_data["job_description"]
            ext = os.path.splitext(resumeFile.name)[1].lower()
            if ext not in ['.pdf', '.docx']:
                return Response({"error": "Only PDF and DOCX files allowed"})

            # size check (5MB max)
            if resumeFile.size > 10 * 1024 * 1024:
                return Response({"error": "File too large (max 10MB)"})
            # content type check (extra safety)
            if resumeFile.content_type not in [
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]:
                return Response({"error": "Invalid file type"})           
            resume_text=parsedResume(resumeFile)

            basic_prompt = f"""
            Analyze the resume against the job description.

            Resume:
            {resume_text}

            Job Description:
            {jd_text}

            STRICT RULE:
            Return ONLY valid JSON. No extra text.
            IMPORTANT:
            - Do NOT include any explanation
            - Do NOT include ```json
            - Return ONLY raw JSON object
            Format:
            {{
                "score": number,
                "missing_skills": ["skill1", "skill2"],
                "suggestions": ["suggestion1", "suggestion2"]
            }}
            """
            medium_prompt = f"""
            Analyze the resume against the job description in more detail.

            Resume:
            {resume_text}

            Job Description:
            {jd_text}

            Return ONLY valid JSON.

            Format:
            {{
                "score": number,
                "missing_skills": ["skill1", "skill2", "skill3"],
                "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
                "strengths": ["strength1", "strength2"],
                "improvement_areas": ["area1", "area2"]
            }}

            Rules:
            - Give more detailed suggestions
            - Mention strengths clearly
            - Identify improvement areas
            """

            advanced_prompt = f"""
            You are an expert ATS resume analyzer.

            Analyze the resume deeply against the job description.

            Resume:
            {resume_text}

            Job Description:
            {jd_text}

            Return ONLY valid JSON.

            Format:
            {{
                "overall_score": number,
                "section_scores": {{
                    "skills": number,
                    "experience": number,
                    "projects": number,
                    "education": number
                }},
                "missing_keywords": ["keyword1", "keyword2"],
                "strengths": ["strength1", "strength2"],
                "weak_points": ["weak1", "weak2"],
                "suggestions": ["detailed suggestion1", "detailed suggestion2"],
                "improved_bullets": ["rewritten resume line 1", "rewritten resume line 2"],
                "recommended_roles": ["role1", "role2"]
            }}

            Rules:
            - Be detailed and professional
            - Give actionable suggestions
            - Rewrite resume points in a better way
            - Suggest job roles based on skills
            """

            if not user.is_authenticated:
                prompt=basic_prompt
            else:
                profile=user.profile
                if profile.plan == "free":
                    prompt = basic_prompt
                elif profile.plan == "starter":
                    prompt = medium_prompt
                elif profile.plan == "pro":
                    prompt = advanced_prompt

            ai_response = model.generate_content(prompt)
            raw_text = ai_response.text.strip()
            print(ai_response)
            print("raw",raw_text)
            # JSON extract
            match = re.search(r'\{[\s\S]*\}', raw_text, re.DOTALL)

            if match:
                json_text = match.group()
                try:
                    result = json.loads(json_text)
                except:
                    return Response({
                        "error": "Invalid AI JSON",
                        "raw": raw_text
                    })
            else:
                return Response({
                    "error": "No JSON found",
                    "raw": raw_text
                })
            if not user.is_authenticated:
                request.session["free_uses"] = free_uses - 1
            else:
                profile.credits-=1
                profile.save()
            return Response(result)
        except Exception as e:
            print("AI ERROR:", str(e))  # 🔥 debug ke liye

            error_msg = str(e).lower()

            if "quota" in error_msg:
                return Response({ "error": "Daily AI limit reached.Try again tomorrow."}, status=503)
            return Response({"error": "Service temporarily unavailable. Please try again later."}, status=503)
@method_decorator(csrf_exempt, name='dispatch')        
class Register(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        password2 = request.data.get("password2")

        if not username:
            return Response({"error": "Username required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=400)

        if password != password2:
            return Response({"error": "Passwords do not match"}, status=400)

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        login(request,user)
        send_welcome_email(user)
        return Response({"message": "Register successfully"}, status=201)
@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='post')        
class Login(APIView):
    def post(self, request):
        username_or_email = request.data.get("username")
        password = request.data.get("password")
        if not username_or_email or not password:
            return Response({"error": "Both fields are required"})
        if "@" in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                return Response({"error": "Invalid credentials"})
        else:
            username = username_or_email
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"})
        login(request, user)
        return Response({
            "message": "Login successful",
            "username": user.username,
            "email": user.email
        })
    
class logout_view(APIView):
    def post(self,request):
        logout(request)
        return Response({"message":"Logged out"})
    
class CreateOrder(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        amount = int(request.data.get("amount"))
        client=razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        ))
        order=client.order.create({
            "amount":amount*100,
            "currency": "INR",
            "payment_capture": 1
        })
        return Response(order)
    
class VerifyPayments(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        client = razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        ))
        data = {
            "razorpay_order_id": request.data.get("razorpay_order_id"),
            "razorpay_payment_id": request.data.get("razorpay_payment_id"),
            "razorpay_signature": request.data.get("razorpay_signature"),
        }

        try:
            client.utility.verify_payment_signature(data)

            user = request.user
            profile = user.profile

            # 🔥 USE ORDER ID TO DETERMINE PLAN (NOT amount)
            order_id = data["razorpay_order_id"]

            # fetch order from razorpay
            order = client.order.fetch(order_id)

            paid_amount = order["amount"]  # THIS IS TRUSTED (in paise)

            if paid_amount == 4900:
                profile.credits += 5
                profile.plan = "starter"

            elif paid_amount == 9900:
                profile.credits += 10
                profile.plan = "pro"
            profile.save()
            send_purchase_email(user)
            return Response({"status": "payment success"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
def login_view(request):
    return render(request,"login.html")
def signup_view(request):
    return render(request,"signup.html")
def terms(request):
    return render(request,"terms.html")
def privacy(request):
    return render(request,"privacy.html")
def refund(request):
    return render(request,"refund.html")