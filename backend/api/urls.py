from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AcessoViewSet, TotalViewSet, DensidadeViewSet
from .auth_views import (
    CsrfView, LoginView, LogoutView, MeView, ChangePasswordView, UserViewSet,
)
from .reports_views import CityReportView

router = DefaultRouter()
router.register("acessos", AcessoViewSet, basename="acesso")
router.register("totais", TotalViewSet, basename="total")
router.register("densidades", DensidadeViewSet, basename="densidade")
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/csrf/", CsrfView.as_view(), name="csrf"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("reports/cidade/", CityReportView.as_view(), name="city-report"),
    *router.urls,
]
