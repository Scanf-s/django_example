from rest_framework.pagination import PageNumberPagination


class BookPagination(PageNumberPagination):
    page_size = 10  # 기본 페이지 크기
    page_size_query_param = "page_size"  # query param으로 수정 가능
    max_page_size = 100  # 최대 페이지 크기
