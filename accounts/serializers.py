from rest_framework import serializers
from accounts.models import User, OfficeStaff, Librarian, Student, LibraryHistory, FeesHistory

DEFAULT_PASSWORD = "ChangeMe@123"

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """
        Validate that the new password and confirm password match.
        """
        new_password = data.get('new_password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()

        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "New password and confirm password do not match."})

        return data


class OfficeStaffSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = OfficeStaff
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'profile_image', 'qualification', 'address', 'pincode', 'about', 'status']

    def create(self, validated_data):
        # Extract user-related data
        user_data = {
            "email": validated_data.pop("email"),
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "phone_number": validated_data.pop("phone_number"),
            "role": "office_staff",
        }
        email = user_data.pop("email")

        user = User.objects.create_user(
            email=email,
            password=DEFAULT_PASSWORD,  # Set default password
            **user_data
        )
        # Create OfficeStaff instance
        office_staff = OfficeStaff.objects.create(user=user, **validated_data)
        return office_staff

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = {
            'email': instance.user.email,
            'first_name': instance.user.first_name,
            'last_name': instance.user.last_name,
            'phone_number': instance.user.phone_number,
            'role': instance.user.role,
        }
        return representation

class LibrarianSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = Librarian
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'profile_image', 'qualification', 'address', 'pincode', 'status']

    def create(self, validated_data):
        # Extract user-related data
        user_data = {
            "email": validated_data.pop("email"),
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "phone_number": validated_data.pop("phone_number"),
            "role": "librarian",
        }
        # Remove 'email' from user_data before unpacking it
        email = user_data.pop("email")

        user = User.objects.create_user(
            email=email,
            password=DEFAULT_PASSWORD,  # Set default password
            **user_data
        )
        # Create Librarian instance
        librarian = Librarian.objects.create(user=user, **validated_data)
        return librarian

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = {
            'email': instance.user.email,
            'first_name': instance.user.first_name,
            'last_name': instance.user.last_name,
            'phone_number': instance.user.phone_number,
            'role': instance.user.role,
        }
        return representation


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'full_name', 'date_of_birth', 'class_name', 'division', 'address', 'gender', 'guardian', 'phone_number', 'state', 'district', 'pincode', 'academic_year','admission_date']


class FeesHistorySerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),  # Ensure student ID exists
        error_messages={'does_not_exist': 'Student with the given ID does not exist.'}
    )

    class Meta:
        model = FeesHistory
        fields = ['id', 'student', 'fee_type', 'academic_year', 'amount', 'payment_date', 'payment_status', 'remarks']

    def validate_amount(self, value):
        """
        Ensure the amount is a positive number.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def create(self, validated_data):
        """
        Create a fees history record for a student.
        """
        return FeesHistory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update a fees history record.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance




class LibraryHistorySerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),  # Ensure student ID exists
        error_messages={'does_not_exist': 'Student with the given ID does not exist.'}
    )

    class Meta:
        model = LibraryHistory
        fields = ['id', 'student', 'book_name', 'book_category', 'borrow_date', 'return_date', 'status']

    def create(self, validated_data):
        """
        Create a library history record for a student.
        """
        return LibraryHistory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update a library history record.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
