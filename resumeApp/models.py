from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    PLANS=[
        ("free","Free"),
        ("starter","Starter"),
        ("pro","Pro")
    ]
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    credits=models.PositiveIntegerField(default=2)
    plan=models.CharField(choices=PLANS,default="free",max_length=20)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}--{self.plan}"