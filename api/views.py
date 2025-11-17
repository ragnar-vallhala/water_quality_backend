from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework import serializers
from .models import WaterUnit, WaterQuality, Maintenance, Maintainer
from .serializers import (
    WaterUnitSerializer,
    WaterQualitySerializer,
    MaintenanceSerializer,
    MaintainerSerializer,
    RegisterMaintainerSerializer
)
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# ------------------------------------------------------
#                     CSRF VIEW
# ------------------------------------------------------
@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"detail": "CSRF cookie set"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    data = MaintainerSerializer(user).data
    return Response(data)
# ------------------------------------------------------
#                       FILTERS
# ------------------------------------------------------

class WaterQualityFilter(filters.FilterSet):
    date = filters.DateFilter(field_name="date_time", lookup_expr="date")
    min_tds = filters.NumberFilter(field_name="tds", lookup_expr="gte")
    max_tds = filters.NumberFilter(field_name="tds", lookup_expr="lte")

    class Meta:
        model = WaterQuality
        fields = ['wu', 'tds', 'date']


class MaintenanceFilter(filters.FilterSet):
    date = filters.DateFilter(field_name="datetime", lookup_expr="date")
    problem_contains = filters.CharFilter(field_name="problem", lookup_expr="icontains")

    class Meta:
        model = Maintenance
        fields = ['wu', 'maintainer', 'date', 'problem_contains']


# ------------------------------------------------------
#               REGISTER NEW MAINTAINER
# ------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterMaintainerSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        res = Response({"message": "Maintainer registered", "maintainer_id": user.id})

        res.set_cookie(
            key="auth_token",
            value=token.key,
            httponly=True,
            secure=True,   # set to True for HTTPS
            samesite="None",
            max_age=60 * 60 * 24 * 7,
        )

        return res

    return Response(serializer.errors, status=400)

# ------------------------------------------------------
#               LOGOUT API
# ------------------------------------------------------
@api_view(['POST'])
def logout(request):
    res = Response({"message": "Logged out"})
    res.delete_cookie('auth_token')
    return res

# ------------------------------------------------------
#                     LOGIN API
# ------------------------------------------------------
class EmailAuthTokenSerializer(AuthTokenSerializer):
    username = serializers.EmailField(label="Email")  # override username as email

class LoginMaintainerView(ObtainAuthToken):
    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        maintainer = token.user

        # Prepare API response
        res = Response({
            "message": "Logged in",
            "maintainer_id": maintainer.id,
            "email": maintainer.email
        })

        # Set HTTP-only cookie
        res.set_cookie(
            key="auth_token",
            value=token.key,
            httponly=True,
            secure=True,        # ❗ set True in production (HTTPS)
            samesite='None',
            max_age=60 * 60 * 24 * 7  # 7 days
        )

        return res


# ------------------------------------------------------
#                     VIEWSETS
# ------------------------------------------------------

class WaterUnitViewSet(viewsets.ModelViewSet):
    queryset = WaterUnit.objects.all()
    serializer_class = WaterUnitSerializer


class WaterQualityViewSet(viewsets.ModelViewSet):
    queryset = WaterQuality.objects.all()
    serializer_class = WaterQualitySerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = WaterQualityFilter

    ordering_fields = ['date_time', 'tds', 'wu']
    ordering = ['-date_time']  # latest first

    def perform_create(self, serializer):
        serializer.save(date_time=timezone.now())


class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MaintenanceFilter

    ordering_fields = ['datetime', 'wu', 'maintainer']
    ordering = ['-datetime']

    def get_permissions(self):
        # Allow GET without authentication
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return []   # no permission classes
        # All other methods need authentication
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(
            datetime=timezone.now(),
            maintainer=self.request.user
        )


