from django.contrib import admin

from .models import Course, CourseMaterial, CourseSession, Enrollment


class CourseSessionInline(admin.TabularInline):
    model = CourseSession
    extra = 0
    fields = (
        "sequence",
        "title",
        "starts_at",
        "ends_at",
        "location",
        "meeting_url",
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subject",
        "instructor",
        "capacity",
        "status",
        "delivery_mode",
        "starts_at",
    )

    list_filter = (
        "status",
        "delivery_mode",
        "subject",
    )

    search_fields = (
        "title",
        "subject",
        "instructor__username",
        "instructor__first_name",
        "instructor__last_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [CourseSessionInline]


@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "sequence",
        "starts_at",
        "ends_at",
    )

    list_filter = ("course",)

    search_fields = (
        "title",
        "course__title",
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "status",
        "grade",
        "enrolled_at",
    )

    list_filter = (
        "status",
        "course",
    )

    search_fields = (
        "student__username",
        "student__first_name",
        "student__last_name",
        "course__title",
    )

    readonly_fields = ("enrolled_at",)


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "uploaded_by",
        "uploaded_at",
    )

    list_filter = ("course",)

    search_fields = (
        "title",
        "course__title",
    )

    readonly_fields = ("uploaded_at",)