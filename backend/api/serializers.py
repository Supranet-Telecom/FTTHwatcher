from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Acesso, Total, Densidade


class UserSerializer(serializers.ModelSerializer):
    """Leitura/edição de usuários. is_staff = 'é administrador'."""
    is_admin = serializers.BooleanField(source="is_staff", required=False)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email",
                  "is_admin", "is_active", "last_login", "date_joined"]
        read_only_fields = ["id", "last_login", "date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(source="is_staff", required=False, default=False)
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email",
                  "password", "is_admin", "is_active"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class AcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acesso
        fields = "__all__"


class TotalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Total
        fields = "__all__"


class DensidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Densidade
        fields = "__all__"


class AcessosPorEmpresaSerializer(serializers.Serializer):
    ano = serializers.IntegerField()
    mes = serializers.IntegerField()
    grupo_economico = serializers.CharField(allow_null=True)
    acessos = serializers.IntegerField()


class AcessosPorTecnologiaSerializer(serializers.Serializer):
    ano = serializers.IntegerField()
    mes = serializers.IntegerField()
    tecnologia = serializers.CharField(allow_null=True)
    acessos = serializers.IntegerField()


class AcessosPorUFSerializer(serializers.Serializer):
    ano = serializers.IntegerField()
    mes = serializers.IntegerField()
    uf = serializers.CharField()
    acessos = serializers.IntegerField()


class AcessosPorSegmentoSerializer(serializers.Serializer):
    ano = serializers.IntegerField()
    mes = serializers.IntegerField()
    empresa = serializers.CharField(allow_null=True)
    tipo_pessoa = serializers.CharField(allow_null=True)
    acessos = serializers.IntegerField()
