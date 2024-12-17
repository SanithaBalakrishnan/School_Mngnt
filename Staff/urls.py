from django.urls import path
from Staff.views import (
    LoginView,
    ChangePasswordView,
    StaffViewSet,
)

urlpatterns = [
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),



# Staff actions
    path('students/', StaffViewSet.as_view({'get': 'list_students'}), name='staff-list-students'),
    path('create-fees-history/', StaffViewSet.as_view({'post': 'create_fees_history'}), name='staff-create-fees-history'),
    path('view-fees-history/<int:pk>/', StaffViewSet.as_view({'get': 'view_fees_history'}), name='staff-view-fees-history'),
    path('update-fees-history/<int:pk>/', StaffViewSet.as_view({'put': 'update_fees_history'}), name='staff-update-fees-history'),
    path('delete-fees-history/<int:pk>/', StaffViewSet.as_view({'delete': 'delete_fees_history'}), name='staff-delete-fees-history'),
    path('view-library-history/<int:pk>/', StaffViewSet.as_view({'get': 'view_library_history'}), name='staff-view-library-history'),
]