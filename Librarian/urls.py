from django.urls import path
from Librarian.views import (
    LoginView,
    ChangePasswordView,
    LibrarianViewSet,
)


urlpatterns = [
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),


# Librarian actions
    path('view-students/', LibrarianViewSet.as_view({'get': 'view_students'}), name='librarian-view-students'),
    path('create-library-history/', LibrarianViewSet.as_view({'post': 'create_library_history'}), name='librarian-create-library-history'),
    path('update-library-history/<int:pk>/', LibrarianViewSet.as_view({'put': 'update_library_history'}), name='librarian-update-library-history'),

]