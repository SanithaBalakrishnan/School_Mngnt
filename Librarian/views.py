from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from accounts.models import User, OfficeStaff, Librarian,Student, LibraryHistory, FeesHistory
from accounts.serializers import ChangePasswordSerializer, OfficeStaffSerializer, LibrarianSerializer, StudentSerializer, LibraryHistorySerializer, FeesHistorySerializer
from accounts.permissions import IsAdmin, IsOfficeStaff, IsLibrarian 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if not user:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    """
    Allow users to change their password.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            # Check if old password is correct
            if not user.check_password(old_password):
                return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

            # Set the new password
            user.set_password(new_password)
            user.must_change_password = False  # Mark password as changed
            user.save()

            return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Librarian actions
class LibrarianViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsLibrarian]

    @action(detail=False, methods=['get'])
    def view_students(self, request):
        """
        Librarian can view all student details.
        """
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_library_history(self, request):
        """
        Librarian can create library history for a particular student.
        """
        serializer = LibraryHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['put'])
    def update_library_history(self, request, pk=None):
        """
        Librarian can update library history for a particular record.
        """
        try:
            library_history = LibraryHistory.objects.get(pk=pk)
            serializer = LibraryHistorySerializer(library_history, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except LibraryHistory.DoesNotExist:
            return Response({'error': 'Library history not found.'}, status=404)

