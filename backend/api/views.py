from urllib.parse import urlencode

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum
from .models import Acesso, Total, Densidade
from .serializers import (
    AcessoSerializer, TotalSerializer, DensidadeSerializer,
    AcessosPorEmpresaSerializer, AcessosPorTecnologiaSerializer, AcessosPorUFSerializer,
    AcessosPorSegmentoSerializer,
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
        if ibge_in := params.get("ibge__in"):
            codes = [c.strip() for c in ibge_in.split(",") if c.strip()]
            if codes:
                qs = qs.filter(ibge__in=codes)
        if tecnologia := params.get("tecnologia"):
            qs = qs.filter(tecnologia__icontains=tecnologia)
        if grupo := params.get("grupo_economico"):
            qs = qs.filter(grupo_economico__icontains=grupo)
        if municipio := params.get("municipio"):
            qs = qs.filter(municipio__icontains=municipio)
        if tipo_produto := params.get("tipo_produto"):
            qs = qs.filter(tipo_produto__iexact=tipo_produto)
        return qs

    def _aggregate(self, request, group_fields, serializer_cls, rename=None):
        """
        Agrega por group_fields somando acessos, com cache no Redis.
        A chave é a rota + os parâmetros de query ordenados, então cada
        combinação de filtros/página tem sua própria entrada de cache.
        Como os dados só mudam quando o ETL roda, o TTL é longo.
        """
        ttl = settings.AGGREGATE_CACHE_TTL
        key = "agg:" + request.path + "?" + urlencode(sorted(request.query_params.items()))

        cached = cache.get(key)
        if cached is None:
            qs = self._apply_base_filters(Acesso.objects.all())
            data = qs.values(*group_fields).annotate(acessos=Sum("acessos")).order_by(*group_fields)
            page = self.paginate_queryset(data)
            if rename:
                for row in page:
                    for src, dst in rename.items():
                        row[dst] = row.pop(src)
            serializer = serializer_cls(page, many=True)
            cached = self.get_paginated_response(serializer.data).data
            cache.set(key, cached, ttl)

        resp = Response(cached)
        # Header para o navegador cachear também — evita nem chegar ao servidor.
        resp["Cache-Control"] = f"public, max-age={ttl}"
        return resp

    @action(detail=False, url_path="por-empresa")
    def por_empresa(self, request):
        return self._aggregate(
            request, ["ano", "mes", "empresa"],
            AcessosPorEmpresaSerializer, rename={"empresa": "grupo_economico"},
        )

    @action(detail=False, url_path="por-tecnologia")
    def por_tecnologia(self, request):
        return self._aggregate(
            request, ["ano", "mes", "tecnologia"], AcessosPorTecnologiaSerializer,
        )

    @action(detail=False, url_path="por-segmento")
    def por_segmento(self, request):
        """Acessos quebrados por empresa e tipo_pessoa (PF vs PJ)."""
        return self._aggregate(
            request, ["ano", "mes", "empresa", "tipo_pessoa"], AcessosPorSegmentoSerializer,
        )

    @action(detail=False, url_path="por-uf")
    def por_uf(self, request):
        return self._aggregate(
            request, ["ano", "mes", "uf"], AcessosPorUFSerializer,
        )


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
