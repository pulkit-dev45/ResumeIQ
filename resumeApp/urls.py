from django.contrib import admin
from django.urls import path , include
from . import views
urlpatterns = [
    path('',views.home,name="home"),
    path('analyze-resume/',views.Resumeanalyzing.as_view(),name="resumecheck"),
    path('create-order/',views.CreateOrder.as_view(),name="create-order"),
    path('verify-payments/',views.VerifyPayments.as_view(),name="verify-payments"),
    path('signup/',views.signup_view, name="signup"),

    path('login/',views.login_view,name="login"),
    path('login/api/',views.Login.as_view(),name="login-api"),
    path('register/api/',views.Register.as_view(),name="register-api"),
    path('logout/api/',views.logout_view.as_view(),name="logout-api"),
    path('terms/',views.terms,name="terms"),
    path('privacy/',views.privacy,name="privacy"),
    path('refund/',views.refund,name="refund"),

]
