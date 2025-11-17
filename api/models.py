from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# --------------------------
# 1. Maintainer (Custom User)
# --------------------------
class MaintainerManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Email required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Maintainer(AbstractBaseUser):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    
    is_active = True
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = MaintainerManager()

    def __str__(self):
        return self.name

    @property
    def is_staff(self):
        return self.is_admin


# --------------------------
# 2. Water Unit
# --------------------------
class WaterUnit(models.Model):
    location = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# --------------------------
# 3. Water Quality
# --------------------------
class WaterQuality(models.Model):
    wu = models.ForeignKey(WaterUnit, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    tds = models.FloatField()

    def __str__(self):
        return f"{self.wu.name} - {self.tds}"


# --------------------------
# 4. Maintenance
# --------------------------
class Maintenance(models.Model):
    wu = models.ForeignKey(WaterUnit, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    problem = models.CharField(max_length=255)
    description = models.TextField()
    maintainer = models.ForeignKey(Maintainer, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.wu.name} - {self.problem}"

