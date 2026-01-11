
from rest_framework.pagination import CursorPagination


class VehiclePagination(CursorPagination):
    page_size = 20
    ordering = "-updated_at"

