from django.shortcuts import render
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
    permission_classes = [AllowAny]  

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


# ---------------------------ADMIN-----------------------------------------------------------------------

class UserViewSet(viewsets.ViewSet):
    """
    ViewSet for user management by Admin.
    Only Admins can create, update, or delete staff and librarian accounts.
    """

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_office_staff(self, request):
        """
        Admin creates Office Staff
        """
       
        if request.user.role != 'admin':
            return Response({'error': 'You do not have permission to perform this action.'}, status=403)

        serializer = OfficeStaffSerializer(data=request.data)
        if serializer.is_valid():
            office_staff = serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_librarian(self, request):
        """
        Admin creates Librarian
        """
        if request.user.role != 'admin':
            return Response({'error': 'You do not have permission to perform this action.'}, status=403)

        serializer = LibrarianSerializer(data=request.data)
        if serializer.is_valid():
            librarian = serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['put'], permission_classes=[IsAdmin])
    def update_user(self, request, pk=None):
        """
        Admin updates Office Staff or Librarian
        """
        try:
            user = User.objects.get(pk=pk)
            if user.role == 'office_staff':
                serializer = OfficeStaffSerializer(user.office_profile, data=request.data, partial=True)
            elif user.role == 'librarian':
                serializer = LibrarianSerializer(user.librarian_profile, data=request.data, partial=True)
            else:
                return Response({'error': 'Invalid role'}, status=400)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_user(self, request, pk=None):
        """
        Reconfirmation step before deleting a user.
        """
        if request.user.role != 'admin':
            return Response(
                {'error': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get the 'confirm' flag from the request
        confirm = request.query_params.get('confirm', 'false').lower() == 'true'

        if not confirm:
            # Return a message asking for confirmation
            return Response(
                {'message': 'Are you sure you want to delete this user? Add ?confirm=true to confirm.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        

class StudentViewSet(viewsets.ModelViewSet):
    """
    Admin can perform CRUD operations on student details.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]  # Ensure only admins can access

    @action(detail=False, methods=['post'], permission_classes=[IsAdmin])
    def create_student(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['put'], permission_classes=[IsAdmin])
    def update_student(self, request, pk=None):
        student = self.get_object()
        serializer = self.get_serializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['delete'], permission_classes=[IsAdmin])
    def delete_student(self, request, pk=None):
        student = self.get_object()
        student.delete()
        return Response({'message': 'Student deleted successfully'}, status=204)


class FeesHistoryViewSet(viewsets.ModelViewSet):
    """
    Admin can perform CRUD operations on fees history.
    """
    queryset = FeesHistory.objects.all()
    serializer_class = FeesHistorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]  # Ensure only admins can access

    @action(detail=False, methods=['post'], url_path='create', permission_classes=[IsAdmin])
    def create_fees_history(self, request):
        """
        Admin can create fees history for a student by student ID.
        """
        # Validate if the student ID exists in the request data
        student_id = request.data.get('student')
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=404)

        # Validate and save fees history
        serializer = FeesHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student)  # Associate fees history with the student
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)', permission_classes=[IsAdmin])
    def list_fees_history_by_student(self, request, student_id=None):
        """
        Retrieve all fees history records for a specific student.
        """
        try:
            # Check if the student exists
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=404)

        # Filter fees history by student
        fees_history = FeesHistory.objects.filter(student=student)
        serializer = self.get_serializer(fees_history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], permission_classes=[IsAdmin])
    def update_fees_history(self, request, pk=None):
        """
        Update a specific fees history record.
        """
        fees_history = self.get_object()
        serializer = self.get_serializer(fees_history, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['delete'], permission_classes=[IsAdmin])
    def delete_fees_history(self, request, pk=None):
        """
        Delete a specific fees history record.
        """
        fees_history = self.get_object()
        fees_history.delete()
        return Response({'message': 'Fees history deleted successfully'}, status=204)


class LibraryHistoryViewSet(viewsets.ModelViewSet):
    """
    Admin can perform CRUD operations on library history.
    """
    queryset = LibraryHistory.objects.all()
    serializer_class = LibraryHistorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]  # Ensure only admins can access

    @action(detail=False, methods=['post'], url_path='create', permission_classes=[IsAdmin])
    def create_library_history(self, request):
        """
        Admin can create library history for a student by student ID.
        """
        # Validate if the student ID exists in the request data
        student_id = request.data.get('student')
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=404)

        # Validate and save library history
        serializer = LibraryHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=student)  # Associate library history with the student
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)', permission_classes=[IsAdmin])
    def list_library_history_by_student(self, request, student_id=None):
        """
        Retrieve all library history records for a specific student.
        """
        try:
            # Check if the student exists
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=404)

        # Filter library history records by student
        library_history = LibraryHistory.objects.filter(student=student)
        serializer = self.get_serializer(library_history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], permission_classes=[IsAdmin])
    def update_library_history(self, request, pk=None):
        """
        Update a specific library history record.
        """
        library_history = self.get_object()
        serializer = self.get_serializer(library_history, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['delete'], permission_classes=[IsAdmin])
    def delete_library_history(self, request, pk=None):
        """
        Delete a specific library history record.
        """
        library_history = self.get_object()
        library_history.delete()
        return Response({'message': 'Library history deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

























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

