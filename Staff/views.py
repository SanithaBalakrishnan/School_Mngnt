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



class StaffViewSet(viewsets.ViewSet):
    """
    Staff can view students, fees history, and library history but cannot create or delete staff or librarian accounts.
    """

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsOfficeStaff])
    def list_students(self, request):
        """
        Staff can view all students.
        """
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

   

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsOfficeStaff])
    def create_fees_history(self, request):
        """
        Staff can create fees history for a student by student ID.
        """
        serializer = FeesHistorySerializer(data=request.data)

        if serializer.is_valid():
            fees_history = serializer.save()  # The serializer now handles all validations and saving
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsOfficeStaff])
    def view_fees_history(self, request, pk=None):
        """
        Staff can view fees history of a student.
        """
        fees_history = FeesHistory.objects.filter(student__id=pk)
        serializer = FeesHistorySerializer(fees_history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], permission_classes=[IsAuthenticated, IsOfficeStaff])
    def update_fees_history(self, request, pk=None):
        """
        Staff can update fees history for a student.
        """
        fees_history = FeesHistory.objects.get(id=pk)
        serializer = FeesHistorySerializer(fees_history, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsOfficeStaff])
    def delete_fees_history(self, request, pk=None):
        """
        Staff can delete fees history of a student.
        """
        fees_history = FeesHistory.objects.get(id=pk)
        fees_history.delete()
        return Response({'message': 'Fees history deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsOfficeStaff])
    def view_library_history(self, request, pk=None):
        """
        Staff can view library history of a student.
        """
        library_history = LibraryHistory.objects.filter(student__id=pk)
        serializer = LibraryHistorySerializer(library_history, many=True)
        return Response(serializer.data)
