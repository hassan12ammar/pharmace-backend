from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from phonenumber_field.modelfields import PhoneNumberField


# Overriding the default UserManager for the user model
class EmailAccountManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})

    def create_user(self,email, password=None, **extra_fields):
        if not email:
            raise ValueError('user must have an email to register')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        
        user.save(using=self._db)
        return user

# Overriding the default User model
class CustomUser(AbstractUser, models.Model):
    username = models.NOT_PROVIDED # remove username field
    email = models.EmailField(max_length=255, unique=True, 
                              primary_key=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = EmailAccountManager()

    # returns the Email of the user to repreaent the user
    def __str__(self):
        return f"{self.email}"

    def natural_key(self):
        return self.email

    class Meta:
        app_label = 'auth_profile'


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, 
                                related_name='profile_user',
                                null=False, blank=False)
    # more info 
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to='profile_imgs', 
                            null=True, blank=True)
    # for address
    city = models.CharField(max_length=85)
    province = models.CharField(max_length=85)
    phone = PhoneNumberField(blank=True, null=True)

    @property
    def phone_number(self):
        return str(self.phone)

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        return f"{self.name} / {self.user.__str__()}"


