# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class CustomUser(AbstractUser):
#     ROLE_CHOICES = [
#         ('player', 'Player'),
#         ('developer', 'Developer'),
#         ('designer', 'Designer'),
#     ]
    
#     REQUEST_STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#     ]

#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='player')
#     is_verified = models.BooleanField(default=False)
#     requested_role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
#     request_status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='pending')
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import datetime

class CustomUser(AbstractUser):
    ROLE_PLAYER = 'player'
    ROLE_DEVELOPER = 'developer'
    ROLE_DESIGNER = 'designer'
    ROLE_SYSTEM_ADMIN = 'admin'
    ROLE_DEV_DES = 'dev/des'

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    ROLE_CHOICES = [
        (ROLE_PLAYER, 'Player'),
        (ROLE_DEVELOPER, 'Developer'),
        (ROLE_DESIGNER, 'Designer'),
        (ROLE_SYSTEM_ADMIN, 'Admin'),
        (ROLE_DEV_DES, 'Dev/Des'),
    ]
    
    REQUEST_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_PLAYER)
    is_verified = models.BooleanField(default=False)
    requested_role = models.CharField(max_length=10, null=True, blank=True, default=None)
    request_status = models.CharField(max_length=10, choices=REQUEST_STATUS_CHOICES, default=STATUS_PENDING)
    avatar = models.ImageField(upload_to="avatar", default='default/gojo.jpg')
    points = models.IntegerField(default=0)
    total_online_time = models.DurationField(default=datetime.timedelta())

    def clean(self):
        """Đảm bảo dữ liệu hợp lệ trước khi lưu"""
        if self.requested_role and self.requested_role not in dict(self.ROLE_CHOICES):
            raise ValidationError({'requested_role': 'Vai trò yêu cầu không hợp lệ.'})

        if self.request_status not in dict(self.REQUEST_STATUS_CHOICES):
            raise ValidationError({'request_status': 'Trạng thái yêu cầu không hợp lệ.'})

        if self.request_status == self.STATUS_PENDING and not self.requested_role:
            raise ValidationError({'requested_role': 'Không thể để trống requested_role khi trạng thái là "pending".'})

    def __str__(self):
        requested_info = f", Requested: {self.requested_role}" if self.requested_role else ""
        status_display = self.get_request_status_display()
        return f"{self.username} ({self.role}) - Status: {status_display}{requested_info}"

    @property
    def is_request_pending(self):
        return self.request_status == self.STATUS_PENDING

    def has_pending_request(self):
        """Kiểm tra xem user có yêu cầu nào chưa được xử lý không"""
        return self.request_status == self.STATUS_PENDING and self.requested_role is not None

    def approve_request(self):
        """Chấp nhận yêu cầu thay đổi vai trò"""
        if self.request_status != self.STATUS_PENDING:
            raise ValidationError("Không thể phê duyệt yêu cầu vì yêu cầu không phải ở trạng thái 'pending'.")

        if not self.requested_role:
            raise ValidationError("Không thể phê duyệt vì không có requested_role.")
        
        self.role = self.requested_role
        self.is_verified = True
        self.request_status = self.STATUS_APPROVED
        self.requested_role = None  # Reset requested_role sau khi phê duyệt
        self.save()

    def reject_request(self):
        """Từ chối yêu cầu thay đổi vai trò"""
        if not self.has_pending_request():
            raise ValidationError("Không có yêu cầu nào hợp lệ để từ chối.")
        
        self.request_status = self.STATUS_REJECTED
        self.requested_role = None
        self.save()

    def reset_role_request(self):
        """Đặt lại trạng thái yêu cầu về 'pending'"""
        if self.is_request_pending:
            raise ValidationError("Yêu cầu đã ở trạng thái 'pending'.")
        
        if not self.has_pending_request():
            raise ValidationError("Không có yêu cầu nào hợp lệ để đặt lại trạng thái.")

        self.request_status = self.STATUS_PENDING
        self.requested_role = None
        self.save()

