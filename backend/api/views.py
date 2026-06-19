from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Acesso, Total, Densidade
from .serializers import (
    AcessoSerializer, TotalSerializer, DensidadeSerializer,
    AcessosPorEmpresaSerializer, AcessosPorTecnologiaSerializer, AcessosPorUFSerializer,
)
from .filters import AcessoFilter, DensidadeFilter


class AcessoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Acesso.objects.all()
    serializer_class = AcessoSerializer
    filterset_class = AcessoFilter
    ordering_fields = ["ano", "mes", "uf", "municipio", "acessos"]

    def _apply_base_filters(self, qs):
        """Aplica filtros comuns (ano, uf) aceitos pelos endpoints agregados."""
        params = self.request.query_params
        if ano_gte := params.get("ano__gte"):
            qs = qs.filter(ano__gte=ano_gte)
        if ano_lte := params.get("ano__lte"):
            qs = qs.filter(ano__lte=ano_lte)
        if ano := params.get("ano"):
            qs = qs.filter(ano=ano)
        if uf := params.get("uf"):
            qs = qs.filter(uf__iexact=uf)
        if ibge := params.get("ibge"):
            qs = qs.filter(ibge=ibge)
        if tecnologia := params.get("tecnologia"):
            qs = qs.filter(tecnologia__icontains=tecnologia)
        if grupo := params.get("grupo_economico"):
            qs = qs.filter(grupo_economico__icontains=grupo)
        return qs

    @action(detail=False, url_path="por-empresa")
    def por_empresa(self, request):
        qs = self._apply_base_filters(Acesso.objects.all())
        data = (
            qs
            .values("ano", "mes", "grupo_economico")
            .annotate(acessos=Sum("acessos"))
            .order_by("ano", "mes", "grupo_economico")
        )
        page = self.paginate_queryset(data)
        serializer = AcessosPorEmpresaSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="por-tecnologia")
    def por_tecnologia(self, request):
        qs = self._apply_base_filters(Acesso.objects.all())
        data = (
            qs
            .values("ano", "mes", "tecnologia")
            .annotate(acessos=Sum("acessos"))
            .order_by("ano", "mes", "tecnologia")
        )
        page = self.paginate_queryset(data)
        serializer = AcessosPorTecnologiaSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="por-uf")
    def por_uf(self, request):
        qs = self._apply_base_filters(Acesso.objects.all())
        data = (
            qs
            .values("ano", "mes", "uf")
            .annotate(acessos=Sum("acessos"))
            .order_by("ano", "mes", "uf")
        )
        page = self.paginate_queryset(data)
        serializer = AcessosPorUFSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class TotalViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    # totais has a composite PK — list only, no retrieve.
    queryset = Total.objects.all()
    serializer_class = TotalSerializer
    filterset_fields = ["ano", "mes"]
    ordering_fields = ["ano", "mes"]


class DensidadeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Densidade.objects.all()
    serializer_class = DensidadeSerializer
    filterset_class = DensidadeFilter
    ordering_fields = ["ano", "mes", "uf", "densidade"]
