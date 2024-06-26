from django.conf import settings
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer, UserReadSerializer, ResetPasswordSerializer
from main.permissions import IsActive, IsSameUserOrStaff, IsInAdminGroupOrStaff
from .models import User
from drf_spectacular.utils import extend_schema
from django.core.cache import cache
import secrets
from django.core.mail import send_mail
import logging

transaction_logger = logging.getLogger("transactions")


class UserListCreateView(generics.GenericAPIView):
    """Create and Read Users"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsInAdminGroupOrStaff]

    def get_serializer_class(self):
        return UserReadSerializer if self.request.method == "GET" else UserSerializer

    def get_queryset(self):
        return User.objects.all()

    @extend_schema(operation_id="list_users")
    def get(self, request):
        users = self.get_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        transaction_logger.info(
            f"{request.user.email} created user {serializer.data['email']}"
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDetailView(generics.GenericAPIView):
    """Read and Update User(id)"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive, IsSameUserOrStaff]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserReadSerializer
        else:
            return UserSerializer

    def get_object(self):
        obj = generics.get_object_or_404(User, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        transaction_logger.info(
            f"{request.user.email} updated user {serializer.data['email']} fields {serializer.validated_data.keys()}"
        )
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        transaction_logger.info(
            f"{request.user.email} updated user {serializer.data['email']} fields {serializer.validated_data.keys()}"
        )
        return Response(serializer.data)


class UserMeDetails(generics.RetrieveAPIView):
    """Read User(me)"""

    serializer_class = UserReadSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsActive]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserResetPassword(generics.GenericAPIView):
    """Reset Password"""

    def post(self, request):
        try:
            user = User.objects.get(email=request.data.get("email"))

            # Check if user is active
            if not user.is_active:
                raise User.DoesNotExist

            # Generate a random token and store it in Redis
            token = secrets.token_urlsafe(nbytes=32)
            cache.set(
                f"password_reset_{token}",
                user.pk,
                timeout=settings.PASSWORD_RESET_TOKEN_TIMEOUT,
            )

            # Send email with reset link containing the token
            send_mail(
                "Cyberprepa Password Reset",
                f"Click on the following link to reset your password: {settings.FRONTEND_URL}/reset-password?token="
                + token,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            # Log transaction
            transaction_logger.info(f"{user.email} requested a password reset")
        except User.DoesNotExist:
            # Do not expose if user does not exist
            pass
        except Exception as e:
            transaction_logger.critical(
                f"An error occurred while trying to reset a password: {e}"
            )
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserResetPasswordConfirm(generics.GenericAPIView):
    """Confirm Password Reset"""

    serializer_class = ResetPasswordSerializer

    def post(self, request):
        try:
            # Validate request data through serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Get token and password from serializer
            token = serializer.validated_data.get("token")
            password = serializer.validated_data.get("password")

            # Get user id from token
            user_id = cache.get(f"password_reset_{token}")

            if user_id is not None:
                user = User.objects.get(pk=user_id)
                user.set_password(password)
                user.save()

                # Log transaction
                transaction_logger.info(f"{user.email} reset their password")

                # Delete token from cache
                cache.delete(f"password_reset_{token}")

                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
                )

        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            transaction_logger.critical(
                f"An error occurred while trying to confirm reset a password: {e}"
            )
            return Response(
                {"detail": "An error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
