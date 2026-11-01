from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q


class Course(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        OPEN = "open", "در حال ثبت‌نام"
        CLOSED = "closed", "ثبت‌نام بسته"
        COMPLETED = "completed", "پایان‌یافته"

    class DeliveryMode(models.TextChoices):
        ONLINE = "online", "آنلاین"
        IN_PERSON = "in_person", "حضوری"

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="taught_courses",
        verbose_name="مدرس",
        limit_choices_to={"role": "instructor"},
    )

    title = models.CharField(
        verbose_name="عنوان دوره",
        max_length=200,
    )

    subject = models.CharField(
        verbose_name="موضوع",
        max_length=100,
    )

    description = models.TextField(
        verbose_name="توضیحات",
    )

    capacity = models.PositiveIntegerField(
        verbose_name="ظرفیت",
        validators=[MinValueValidator(1)],
    )

    starts_at = models.DateTimeField(
        verbose_name="زمان شروع دوره",
    )

    ends_at = models.DateTimeField(
        verbose_name="زمان پایان دوره",
    )

    fee = models.DecimalField(
        verbose_name="هزینه",
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    delivery_mode = models.CharField(
        verbose_name="نوع برگزاری",
        max_length=20,
        choices=DeliveryMode.choices,
        default=DeliveryMode.ONLINE,
    )

    status = models.CharField(
        verbose_name="وضعیت دوره",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_at = models.DateTimeField(
        verbose_name="تاریخ ایجاد",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name="آخرین ویرایش",
        auto_now=True,
    )

    class Meta:
        verbose_name = "دوره"
        verbose_name_plural = "دوره‌ها"
        ordering = ["-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=Q(capacity__gte=1),
                name="course_capacity_at_least_one",
            ),
            models.CheckConstraint(
                condition=Q(fee__gte=0),
                name="course_fee_not_negative",
            ),
            models.CheckConstraint(
                condition=Q(ends_at__gt=F("starts_at")),
                name="course_end_after_start",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = "زمان پایان باید بعد از زمان شروع باشد."

        if self.instructor_id and self.instructor.role != "instructor":
            errors["instructor"] = "کاربر انتخاب‌شده باید نقش مدرس داشته باشد."

        if errors:
            raise ValidationError(errors)

    @property
    def enrolled_count(self):
        """تعداد ثبت‌نام‌های فعال و تکمیل‌شده دوره."""
        return self.enrollments.exclude(
            status=Enrollment.Status.CANCELLED
        ).count()

    @property
    def seats_left(self):
        """تعداد ظرفیت باقی‌مانده."""
        return max(self.capacity - self.enrolled_count, 0)

    def __str__(self):
        return self.title


class CourseSession(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="دوره",
    )

    sequence = models.PositiveSmallIntegerField(
        verbose_name="شماره جلسه",
        validators=[MinValueValidator(1)],
    )

    title = models.CharField(
        verbose_name="عنوان جلسه",
        max_length=200,
    )

    description = models.TextField(
        verbose_name="توضیحات",
        blank=True,
    )

    starts_at = models.DateTimeField(
        verbose_name="زمان شروع جلسه",
    )

    ends_at = models.DateTimeField(
        verbose_name="زمان پایان جلسه",
    )

    location = models.CharField(
        verbose_name="محل برگزاری",
        max_length=200,
        blank=True,
    )

    meeting_url = models.URLField(
        verbose_name="لینک جلسه آنلاین",
        blank=True,
    )

    class Meta:
        verbose_name = "جلسه دوره"
        verbose_name_plural = "جلسات دوره"
        ordering = ["starts_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["course", "sequence"],
                name="unique_session_number_per_course",
            ),
            models.CheckConstraint(
                condition=Q(sequence__gte=1),
                name="session_number_at_least_one",
            ),
            models.CheckConstraint(
                condition=Q(ends_at__gt=F("starts_at")),
                name="session_end_after_start",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = "زمان پایان باید بعد از زمان شروع باشد."

        if self.course_id:
            if self.starts_at and self.starts_at < self.course.starts_at:
                errors["starts_at"] = "جلسه نمی‌تواند قبل از شروع دوره باشد."

            if self.ends_at and self.ends_at > self.course.ends_at:
                errors["ends_at"] = "جلسه نمی‌تواند بعد از پایان دوره باشد."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.course.title} - جلسه {self.sequence}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "ثبت‌نام‌شده"
        CANCELLED = "cancelled", "لغوشده"
        COMPLETED = "completed", "تکمیل‌شده"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="course_enrollments",
        verbose_name="دانشجو",
        limit_choices_to={"role": "student"},
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="enrollments",
        verbose_name="دوره",
    )

    status = models.CharField(
        verbose_name="وضعیت ثبت‌نام",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    grade = models.DecimalField(
        verbose_name="نمره",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="نمره از ۰ تا ۱۰۰ ثبت می‌شود.",
    )

    evaluation = models.TextField(
        verbose_name="ارزیابی مدرس",
        blank=True,
    )

    enrolled_at = models.DateTimeField(
        verbose_name="زمان ثبت‌نام",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "ثبت‌نام دوره"
        verbose_name_plural = "ثبت‌نام‌های دوره"
        ordering = ["-enrolled_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course_enrollment",
            ),
            models.CheckConstraint(
                condition=(
                    Q(grade__isnull=True)
                    | (Q(grade__gte=0) & Q(grade__lte=100))
                ),
                name="enrollment_grade_between_0_and_100",
            ),
        ]

    def clean(self):
        super().clean()

        if self.student_id and self.student.role != "student":
            raise ValidationError(
                {"student": "کاربر انتخاب‌شده باید نقش دانشجو داشته باشد."}
            )

    def __str__(self):
        return f"{self.student} - {self.course}"


class CourseMaterial(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="materials",
        verbose_name="دوره",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_materials",
        verbose_name="بارگذاری‌کننده",
    )

    title = models.CharField(
        verbose_name="عنوان فایل",
        max_length=200,
    )

    file = models.FileField(
        verbose_name="فایل آموزشی",
        upload_to="course_materials/%Y/%m/",
    )

    uploaded_at = models.DateTimeField(
        verbose_name="زمان بارگذاری",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "محتوای دوره"
        verbose_name_plural = "محتواهای دوره"
        ordering = ["-uploaded_at"]

    def clean(self):
        super().clean()

        if (
            self.course_id
            and self.uploaded_by_id
            and self.course.instructor_id != self.uploaded_by_id
        ):
            raise ValidationError(
                {
                    "uploaded_by": (
                        "بارگذاری‌کننده باید مدرس همین دوره باشد."
                    )
                }
            )

    def __str__(self):
        return self.title