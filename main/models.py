from django.db import models
from  django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
class MPic(models.Model):
    id = models.BigAutoField(primary_key=True)
    pic = models.CharField(max_length=100, blank=True, null=True)
    pic_icon = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'm_pic'

class MGroup(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.CharField(max_length=200, blank=True, null=True)
    pic = models.ForeignKey(MPic, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        managed = True
        db_table = 'm_group'
        
class MLocation(models.Model):
    id = models.BigAutoField(primary_key=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    group = models.ForeignKey(MGroup, on_delete=models.SET_NULL, null=True, blank=True)
    pic = models.ForeignKey(MPic, on_delete=models.SET_NULL, null=True, blank=True)
    lat = models.CharField(max_length=100, blank=True, null=True)
    long = models.CharField(max_length=100, blank=True, null=True)
    banjir = models.CharField(max_length=100, blank=True, null=True)
    kekeringan = models.CharField(max_length=100, blank=True, null=True)
    cuacaEkstrim = models.CharField(max_length=100, blank=True, null=True)
    longsor = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'm_location'

class UserPIC(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pic = models.ForeignKey(MPic, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_pic'

    def __str__(self):
        return f"{self.user.username} - {self.pic.pic}"

class UserDetail(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(MLocation, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=100, blank=True, null=True, default='contributor')
    
    class Meta:
        managed = True
        db_table = 'user_detail'

class TMatlevIndicator(models.Model):
    id = models.BigAutoField(primary_key=True)
    pillar = models.CharField(max_length=10, blank=True, null=True)
    number = models.CharField(max_length=10, blank=True, null=True)
    indicator = models.TextField(blank=True, null=True)
    year = models.CharField(max_length=10, blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 't_matlev_indicator'
    
class TMatlevKriteria(models.Model):
    id = models.BigAutoField(primary_key=True)
    indicator = models.ForeignKey(TMatlevIndicator, on_delete=models.SET_NULL, null=True, blank=True)
    number = models.CharField(max_length=10, blank=True, null=True)
    kriteria = models.TextField(blank=True, null=True)
    max_level = models.IntegerField(blank=True, null=True, default=3)
    level_get = models.IntegerField(blank=True, null=True, default=0)
    level_weight = models.IntegerField(blank=True, null=True, default=0)
    level_sum = models.IntegerField(blank=True, null=True, default=0)
    year = models.CharField(max_length=10, blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 't_matlev_kriteria'

class TMatlevKriteriaLevelGet(models.Model):
    id = models.BigAutoField(primary_key=True)
    kriteria = models.ForeignKey(TMatlevKriteria, on_delete=models.SET_NULL, null=True, blank=True)
    pic = models.ForeignKey(MPic, on_delete=models.SET_NULL, null=True, blank=True)
    level_get = models.IntegerField(blank=True, null=True, default=0)
    
    class Meta:
        managed = True
        db_table = 't_matlev_kriteria_levelget'

class TMatlevKriteriaDetail(models.Model):
    id = models.BigAutoField(primary_key=True)
    kriteria = models.ForeignKey(TMatlevKriteria, on_delete=models.SET_NULL, null=True, blank=True)
    maturity = models.TextField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    evidence = models.TextField(blank=True, null=True)
    data_type = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    keterangan = models.TextField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    last_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(blank = True, null=True)
    
    class Meta:
        managed = True
        db_table = 't_matlev_kriteria_detail'

class TMatlevKriteriaPic(models.Model):
    id = models.BigAutoField(primary_key=True)
    maturity = models.ForeignKey(TMatlevKriteriaDetail, on_delete=models.SET_NULL, null=True, blank=True)
    pic = models.ForeignKey(MPic, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        managed = True
        db_table = 't_matlev_kriteria_pic'

class TMatlevKriteriaColumn(models.Model):
    id = models.BigAutoField(primary_key=True)
    maturity = models.ForeignKey(TMatlevKriteriaDetail, on_delete=models.SET_NULL, null=True, blank=True)
    sub_column = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    column_name = models.TextField(blank=True, null=True)
    column_type = models.CharField(max_length=30, blank=True, null=True)
    hints = models.TextField(blank=True, null=True)
    show_table = models.BooleanField(default=False)
    negative_input = models.BooleanField(default=False)
    equation = models.TextField(blank=True, null=True)
    emission_category = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 't_matlev_kriteria_column'

class TMatlevKriteriaColumnOption(models.Model):
    id = models.BigAutoField(primary_key=True)
    column = models.ForeignKey(TMatlevKriteriaColumn, on_delete=models.SET_NULL, null=True, blank=True)
    option = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 't_matlev_kriteria_column_option'

class TRMatlev(models.Model):
    id = models.BigAutoField(primary_key=True)
    indicator = models.ForeignKey(TMatlevIndicator, on_delete=models.SET_NULL, null=True, blank=True)
    kriteria = models.ForeignKey(TMatlevKriteria, on_delete=models.SET_NULL, null=True, blank=True)
    maturity = models.ForeignKey(TMatlevKriteriaDetail, on_delete=models.SET_NULL, null=True, blank=True)
    pic = models.ForeignKey(MPic, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True,default=timezone.now)

    
    class Meta:
        managed = True
        db_table = 'tr_matlev'
    
    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)
        
        if self.maturity:
            self.maturity.last_update = timezone.now()
            self.maturity.last_user = self.user
            self.maturity.save(update_fields=['last_update','last_user'])

class TRMatlevColumn(models.Model):
    id = models.BigAutoField(primary_key=True)
    matlev = models.ForeignKey(TRMatlev, on_delete=models.SET_NULL, null=True, blank=True)
    column = models.ForeignKey(TMatlevKriteriaColumn, on_delete=models.SET_NULL, null=True, blank=True)
    value = models.TextField(blank=True, null=True)
    value_files = models.FileField(upload_to='uploads/', max_length=500,blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'tr_matlev_column'

class TREmission(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.CharField(max_length=200, blank=True, null=True)
    year = models.CharField(max_length=10, blank=True, null=True)
    pic = models.ForeignKey(MPic, on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(MGroup, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(MLocation, on_delete=models.SET_NULL, null=True, blank=True)
    information = models.CharField(max_length=200, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'tr_emission'

class ActivityLog(models.Model):
    # Jenis Aktivitas
    ACTIVITY_CHOICES = [
        ('VIEW', 'View'),
        ('CREATE', 'Create'),
        ('EDIT', 'Edit'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('DOWNLOAD', 'Download'),
    ]

    # Jenis Aplikasi (sesuaikan dengan urlpatterns Anda)
    APP_CHOICES = [
        ('DASHBOARD', 'Dashboard'),
        ('DATA', 'Data'),
        ('MASTER', 'Master'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="User"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name="Timestamp"
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES,
        verbose_name="Activity Type"
    )
    app = models.CharField(
        max_length=20,
        choices=APP_CHOICES,
        verbose_name="Application"
    )
    path = models.CharField(
        max_length=255,
        verbose_name="URL Path"
    )
    method = models.CharField(
        max_length=10,
        verbose_name="HTTP Method"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP Address"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="User Agent"
    )
    extra_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Additional Data"
    )

    class Meta:
        db_table = 't_activity_logs'
        ordering = ['-timestamp']
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['app']),
        ]

    def __str__(self):
        return f"{self.user} - {self.activity_type} - {self.path}"