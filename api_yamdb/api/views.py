from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title


from .filters import TitleFilter
from .permissions import (
    AdminOrReadOnly,
    AuthorAdminModeratorPermission,
    IsAdmin,
    IsSuperuser
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleCreateAndUpdate,
    TitleGet,
    TokenSerializer,
    UserSerializer,
    UserMeSerializer,
    UserSignUpSerializer
)

User = get_user_model()


class SignUpView(views.APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username=serializer.data['username'])
            confirmation_code = default_token_generator.make_token(user)
            send_mail(
                subject='Код подтверждения',
                message=f'Ваш код: {confirmation_code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email, ]
            )
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class GetTokenView(views.APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            try:
                user = get_object_or_404(User, username=username)
            except Http404:
                return Response(
                    'Пользователя с таким username не существует',
                    status=status.HTTP_404_NOT_FOUND
                )
            if default_token_generator.check_token(
                user, serializer.validated_data['confirmation_code']
            ):
                token = str(AccessToken.for_user(user))
                user_data = {
                    'username': user.username,
                    'token': token
                }
                return Response(
                    user_data,
                    status=status.HTTP_200_OK
                )
            return Response(
                'Неверный код подтверждения',
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin | IsSuperuser, ]
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter, ]
    search_fields = ('username',)
    pagination_class = PageNumberPagination

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated, ]
    )
    def user_me(self, request):
        user = request.user
        if request.method == 'GET':
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_200_OK
            )
        serializer = UserMeSerializer(user, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListDeleteCreateViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    pass


class GenreViewSet(ListDeleteCreateViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ('name', 'slug')
    pagination_class = PageNumberPagination
    lookup_field = 'slug'


class CategoryViewSet(ListDeleteCreateViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ('name', 'slug')
    pagination_class = PageNumberPagination
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    TitleObjects = Title.objects.all()
    queryset = TitleObjects.annotate(Avg('reviews__score')).order_by('name')
    permission_classes = [AdminOrReadOnly, ]
    pagination_class = PageNumberPagination
    filterset_class = TitleFilter
    filter_backends = [DjangoFilterBackend, ]

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'destroy']:
            return TitleCreateAndUpdate
        return TitleGet


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        AuthorAdminModeratorPermission,
        IsAuthenticatedOrReadOnly,
    ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        AuthorAdminModeratorPermission,
        IsAuthenticatedOrReadOnly,
    ]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title)
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title)
        serializer.save(author=self.request.user, review=review)
