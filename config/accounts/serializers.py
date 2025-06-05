from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = User
        # Ensure all fields needed for user creation are listed, plus custom ones.
        # 'name' is our custom field. 'email' is made required.
        fields = ('username', 'password', 'password2', 'email', 'name')
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'name': {'required': False, 'allow_blank': True} # Assuming name is optional
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # ModelSerializer's default validators handle username uniqueness if UniqueValidator is on the model field.
        # However, explicit check can provide clearer error messages or handle complex cases.
        # User.username is unique by default from AbstractUser.
        # For email, AbstractUser.email is not unique by default. We need to enforce this.
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with that email already exists."})
        return attrs

    def create(self, validated_data):
        # Create the user instance.
        # Note: AbstractUser does not have 'name' by default, but our custom User model does.
        # It also doesn't have 'registered_on' as a creation parameter here, it's auto_now_add/default.
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'], # create_user handles hashing
            name=validated_data.get('name', '')
        )
        # set_password is not needed if password is passed to create_user
        # user.set_password(validated_data['password'])
        # user.save() # create_user already saves
        return user

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # These are fields from our custom User model or AbstractUser
        fields = ('id', 'username', 'email', 'name', 'registered_on', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
        read_only_fields = ('id', 'registered_on', 'is_staff', 'is_superuser', 'last_login', 'date_joined')

# Login serializer is handled by SimpleJWT's TokenObtainPairSerializer
# We can customize it if needed, but for now, default is fine.
