from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError

GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

# Validator to limit file size
def validate_file_size(value):
    max_file_size = 2 * 1024 * 1024  # 2 MB
    if value.size > max_file_size:
        raise ValidationError("The maximum file size allowed is 2MB.")


class UserManager(BaseUserManager):
    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        if not email and not phone_number:
            raise ValueError('You must provide either an email address or a phone number')
        if email:
            email = self.normalize_email(email)
        if phone_number:
            phone_number = ''.join(filter(str.isdigit, phone_number))  # Normalize phone number
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    

    def create_superuser(self, email=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if email is None:
            raise ValueError('Superuser must have an email address.')

        return self.create_user(email=email, phone_number=phone_number, password=password, **extra_fields)

        

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('office_staff', 'Office Staff'),
        ('librarian', 'Librarian'),
    ]

    email = models.EmailField(unique=True, null=True, blank=True, db_index=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True, db_index=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=True)  # Enforce password reset


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email or self.phone_number})"

    def clean(self):
        if not self.email and not self.phone_number:
            raise ValidationError('At least one of email or phone number must be provided.')

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")
    additional_permissions = models.TextField(blank=True, null=True)


class OfficeStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="office_profile")
    profile_image = models.ImageField(upload_to='s-profile-images/', null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True, help_text="Educational qualification")
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True)
    pincode = models.CharField(max_length=10, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    about = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')


class Librarian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="librarian_profile")
    # library_section = models.CharField(max_length=100)
    qualification = models.CharField(max_length=255, null=True, blank=True, help_text="Educational qualification")
    profile_image = models.ImageField(upload_to='c-profile-images/', null=True, blank=True, validators=[validate_file_size])
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True)
    pincode = models.CharField(max_length=10, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,default='M')
    status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')



class Student(models.Model):
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    class_name = models.CharField(max_length=50, null=True, help_text="Class name, e.g., '9th' or '10th'")
    division = models.CharField(max_length=10, null=True, blank=True, help_text="Division or section, e.g., 'A', 'B', etc.")
    address = models.TextField(null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    guardian = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    state = models.CharField(max_length=30, null=True)
    district = models.CharField(max_length=30, null=True)
    pincode = models.CharField(max_length=10, null=True)
    academic_year = models.CharField(max_length=9, null=True, blank=True, help_text="Academic year in format YYYY-YYYY")
    admission_date = models.DateField(null=True, blank=True, help_text="Date of admission")

    def __str__(self):
        return self.full_name


# Library History Model
class LibraryHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='library_history')
    book_name = models.CharField(max_length=255)
    book_category = models.CharField(max_length=50, choices=[('fiction', 'Fiction'),('non_fiction', 'Non-Fiction'),('novel', 'Novel'),('biography', 'Biography'),('science', 'Science'),('history', 'History'),('others', 'Others')], null=True, blank=True, help_text="Category of the book")
    borrow_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('borrowed', 'Borrowed'),('returned', 'Returned')])

    def __str__(self):
        return f"{self.book_name} - {self.status}"

    # def __str__(self):
    #     return f"{self.book_name} - {self.student.full_name}"

# Fees History Model
class FeesHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees_history')
    fee_type = models.CharField(max_length=255)
    academic_year = models.CharField(
        max_length=9, 
        null=True, 
        blank=True, 
        help_text="Academic year in format YYYY-YYYY"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_status = models.CharField(
        max_length=20, 
        choices=[
            ('paid', 'Paid'),
            ('pending', 'Pending'),
            ('partial', 'Partial'),
        ],
        default='pending',
        help_text="Status of the fee payment"
    )
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.fee_type} ({self.payment_status})"


    # def __str__(self):
    #     return f"{self.fee_type} - {self.student.full_name}"
