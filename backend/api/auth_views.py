"""
FTTH Watcher — Autenticação por sessão e gestão de usuários.
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    UserSerializer, UserCreateSerializer, ChangePasswordSerializer,
)


def _user_payload(user):
    """Dados mínimos do usuário logado para o frontend."""
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_admin": user.is_staff,
    }


@method_decorator(ensure_csrf_cookie, name="get")
class CsrfView(APIView):
    """GET para o frontend obter o cookie CSRF antes de fazer login."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "CSRF cookie set"})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Usuário ou senha inválidos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {"detail": "Usuário desativado."},
                status=status.HTTP_403_FORBIDDEN,
            )
        login(request, user)
        return Response(_user_payload(user))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Logout efetuado."})


class MeView(APIView):
    """Retorna o usuário logado — o frontend usa para saber o estado de auth."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_user_payload(request.user))


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Senha alterada com sucesso."})


class UserViewSet(viewsets.ModelViewSet):
    """CRUD de usuários — restrito a administradores (is_staff)."""
    queryset = User.objects.all().order_by("username")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        # Nunca deletar de fato — apenas desativar, e nunca a si mesmo.
        user = self.get_object()
        if user.id == request.user.id:
            return Response(
                {"detail": "Você não pode desativar a si mesmo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        user.save()
        return Response({"detail": "Usuário desativado."})
