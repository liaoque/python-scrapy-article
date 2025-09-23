# apps/ext_models/serializers.py
from rest_framework import serializers
from .models import MCls

class MClsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCls
        # fields = '__all__'
        fields = ('id', 'tid', 'created_at', 'content')

