from django.contrib import admin
from .models import UserScholarship


@admin.register(UserScholarship)
class UserScholarshipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "region",
        "district",
        "university_name",
        "major_field",
        "academic_year_type",
        "income_level",
    )
    list_filter = (
        "region",
        "university_type",
        "academic_year_type",
        "is_multi_cultural_family",
        "is_single_parent_family",
        "is_multiple_children_family",
        "is_national_merit",
    )
    search_fields = ("user__username", "name", "university_name", "major_field")
