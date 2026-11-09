from rest_framework.pagination import PageNumberPagination


class PaginacaoPadrao(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"  # /api/livros/?page_size=100
    max_page_size = 200