from rest_framework import serializers

class ResumeSerializer(serializers.Serializer):
    resume=serializers.FileField()
    job_description=serializers.CharField()
