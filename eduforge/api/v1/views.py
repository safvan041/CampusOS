"""
API v1 views.
"""
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action


class BaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet for all API endpoints.
    """
    pass
