from rest_framework.pagination import PageNumberPagination


class GCodeFilePagination(PageNumberPagination):
    # Preserve the mobile API's default and page-number response contract.
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100
