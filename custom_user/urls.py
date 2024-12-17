from django.urls import path
from custom_user.views import (
    LoginView,
    ChangePasswordView,
    UserViewSet,
    StudentViewSet,
    LibraryHistoryViewSet,
    FeesHistoryViewSet,
)


urlpatterns = [
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    
    # User actions (Admin only)
    path('create-office-staff/', UserViewSet.as_view({'post': 'create_office_staff'}), name='create_office-staff'),
    path('create-librarian/', UserViewSet.as_view({'post': 'create_librarian'}), name='create-librarian'),
    path('update-user/<int:pk>/', UserViewSet.as_view({'put': 'update_user'}), name='update-user'),
    path('delete-user/<int:pk>/', UserViewSet.as_view({'delete': 'delete_user'}), name='delete-user'),

    # Student CRUD (Admin only)
    path('students/create/', StudentViewSet.as_view({'post': 'create_student'}), name='create-student'),
    path('students/', StudentViewSet.as_view({'get': 'list'}), name='list-students'),
    path('students/<int:pk>/', StudentViewSet.as_view({'get': 'retrieve', 'put': 'update_student', 'delete': 'delete_student'}), name='student-detail'),

    path('library-history/create/', LibraryHistoryViewSet.as_view({'post': 'create_library_history'}), name='create-library-history'),
    # List all library history records for a specific student
    path('library-history/student/<int:student_id>/', LibraryHistoryViewSet.as_view({'get': 'list_library_history_by_student'}), name='list-student-library-history'),
    # Default CRUD operations
    path('library-history/', LibraryHistoryViewSet.as_view({'get': 'list'}), name='list-library-history'),
    path('library-history/<int:pk>/', LibraryHistoryViewSet.as_view({
        'get': 'retrieve',
        'put': 'update_library_history',
        'delete': 'delete_library_history'
    }), name='library-history-detail'),
    
    # List all fees history
    path('fees-history/', FeesHistoryViewSet.as_view({'get': 'list'}), name='list-fees-history'),
    
    # Create fees history
    path('fees-history/create/', FeesHistoryViewSet.as_view({'post': 'create_fees_history'}), name='create-fees-history'),

    # Retrieve, update, delete specific fees history by ID
    path('fees-history/<int:pk>/', FeesHistoryViewSet.as_view({
        'get': 'retrieve',
        'put': 'update_fees_history',
        'delete': 'delete_fees_history'
    }), name='fees-history-detail'),

    # List fees history for a specific student
    path('fees-history/student/<int:student_id>/', FeesHistoryViewSet.as_view({
        'get': 'list_fees_history_by_student'
    }), name='list-student-fees-history'),



    path('change-password/', ChangePasswordView.as_view(), name='change-password'),


]
