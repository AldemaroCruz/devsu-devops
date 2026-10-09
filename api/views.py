from rest_framework import viewsets
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.order_by("id")

    def create(self, request, *args, **kwargs):
        if self.get_queryset().filter(dni=request.data.get("dni", "")).exists():
            return Response({"detail": "User already exists"}, status=400)
        return super().create(request, *args, **kwargs)
