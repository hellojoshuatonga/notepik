# Python
from collections import OrderedDict

# Rest framework
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CategoryInfoPagination(PageNumberPagination):
    """
    Custom pagination class for category additional informations
    """
    def get_paginated_response(self, data, notes_count=None):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('notes_count', notes_count),
            ('results', data),
            ]))
