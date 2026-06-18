from django.contrib import admin
from .models import RawScholarship, Scholarship, ScholarshipAlert, Wishlist


@admin.register(RawScholarship)
class RawScholarshipAdmin(admin.ModelAdmin):
    list_display = (
        "product_id",
        "name",
        "foundation_name",
        "recruitment_start",
        "recruitment_end",
        "product_type",
        "url",
    )
    list_filter = ("product_type", "university_type", "academic_year_type")
    search_fields = ("name", "foundation_name", "product_id", "url")
    ordering = ("name",)


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = (
        'product_id', 
        'name', 
        'foundation_name', 
        'recruitment_start', 
        'recruitment_end', 
        'university_type',
        'academic_year_type', 
        'major_field',
        'region',
        'is_region_processed',
        'product_type',
        'support_details',
    )
    
    list_filter = (
        'university_type', 
        'academic_year_type', 
        'product_type', 
        'region', 
        'is_region_processed',
        'recommendation_required',
    )
    
    search_fields = (
        'name', 
        'foundation_name', 
        'grade_criteria_details', 
        'income_criteria_details',
        'specific_qualification_details',
        'residency_requirement_details',
        'major_field', 
    )

    fieldsets = (
        (None, {
            'fields': ('product_id', 'name', 'foundation_name', 'product_type', 'managing_organization_type')
        }),
        ('모집 기간', {
            'fields': ('recruitment_start', 'recruitment_end')
        }),
        ('대상 조건', {
            'fields': ('university_type', 'academic_year_type', 'major_field','region','is_region_processed',) 
        }),
        ('상세 기준', {
            'fields': ('grade_criteria_details', 'income_criteria_details', 'specific_qualification_details', 'residency_requirement_details', 'eligibility_restrictions')
        }),
        ('선발 및 지원', {
            'fields': ('selection_method_details', 'number_of_recipients_details', 'required_documents_details', 'support_details', 'recommendation_required')
        }),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "scholarship", "added_at")
    list_filter = ("added_at",)
    search_fields = ("user__username", "scholarship__name")
    autocomplete_fields = ("scholarship",)


@admin.register(ScholarshipAlert)
class ScholarshipAlertAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "wishlist", "remind_days_before", "last_sent_for_date", "created_at")
    list_filter = ("remind_days_before", "last_sent_for_date", "created_at")
    search_fields = ("user__username", "wishlist__scholarship__name")
    autocomplete_fields = ("wishlist",)
