from django.contrib import admin
from .models import User,Student,LibraryHistory,FeesHistory,OfficeStaff,Librarian

admin.site.register(User)
admin.site.register(OfficeStaff)
admin.site.register(Librarian)
admin.site.register(Student)
admin.site.register(LibraryHistory)
admin.site.register(FeesHistory)
