from rest_framework import serializers
from .models import Acesso, Total, Densidade


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
