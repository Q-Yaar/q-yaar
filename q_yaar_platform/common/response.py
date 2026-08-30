from rest_framework.response import Response
from rest_framework import serializers

from django.db.models.query import QuerySet

from .base_error_codes import BaseErrorCode


def get_standard_response(error: BaseErrorCode, response: dict) -> Response:
    response_body = (
        error.to_json()
        if error.code not in [BaseErrorCode.SUCCESS, BaseErrorCode.CREATED, BaseErrorCode.NO_CONTENT]
        else response
    )
    return Response(response_body, error.http_status_code)


def get_paginated_response(
    instance,
    error: BaseErrorCode,
    queryset: QuerySet,
    serializer_class: serializers.ModelSerializer,
    context: dict | None = None,
) -> Response:
    if error.code not in [BaseErrorCode.SUCCESS, BaseErrorCode.CREATED, BaseErrorCode.NO_CONTENT]:
        return Response(error.to_json(), error.http_status_code)
    else:
        paginated_queryset = instance.paginate_queryset(queryset)
        return instance.get_paginated_response(
            serializer_class(paginated_queryset, many=True, context=context or {}).data
        )
