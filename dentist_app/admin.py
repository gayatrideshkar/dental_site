from django.contrib import admin
from django.utils.html import format_html
from .models import Service, GalleryImage, ContactInfo, OpeningHour, Post, Certification

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'published', 'order')
    list_filter = ('published',)
    search_fields = ('title', 'short_description')
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('order', 'title')
    fields = ('title', 'slug', 'short_description', 'what_is', 'why_necessary', 'when_to_do', 'description', 'image', 'order', 'published')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category', 'uploaded_at', 'preview')
    list_filter = ('category', 'uploaded_at')
    list_editable = ('category',)
    search_fields = ('title', 'caption', 'alt_text')
    readonly_fields = ('preview',)
    date_hierarchy = 'uploaded_at'
    actions = ('mark_as_clinic', 'mark_as_before_after')
    fields = ('title', 'image', 'preview', 'category', 'caption', 'alt_text')

    def mark_as_clinic(self, request, queryset):
        updated = queryset.update(category=GalleryImage.Category.CLINIC)
        self.message_user(request, f"{updated} image(s) marked as Clinic.")
    mark_as_clinic.short_description = 'Mark selected images as Clinic'

    def mark_as_before_after(self, request, queryset):
        updated = queryset.update(category=GalleryImage.Category.BEFORE_AFTER)
        self.message_user(request, f"{updated} image(s) marked as Before & After.")
    mark_as_before_after.short_description = 'Mark selected images as Before & After'

    def preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height:60px;" />', obj.thumbnail.url)
        if obj.image:
            return format_html('<img src="{}" style="max-height:60px;" />', obj.image.url)
        return ''
    preview.short_description = 'Preview'


# Admin for contact info and hours
class OpeningHourInline(admin.TabularInline):
    model = OpeningHour
    extra = 0
    fields = ('order', 'day', 'periods')

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'phone_display', 'email')
    inlines = (OpeningHourInline,)
    fieldsets = (
        (None, {
            'fields': ('phone_display', 'phone_link', 'address_display', 'email', 'doctor_name')
        }),
    )


from django.utils.text import slugify

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'published_at')
    list_filter = ('published', 'published_at')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title', 'excerpt', 'content')
    fields = ('title', 'slug', 'excerpt', 'content', 'image', 'published_at', 'published')

    def save_model(self, request, obj, form, change):
        """Ensure slug uniqueness on save (auto-fix conflicts and notify the admin user)."""
        base = slugify(obj.slug) if obj.slug else slugify(obj.title)
        base = base or 'post'
        slug_candidate = base
        counter = 1
        while Post.objects.filter(slug=slug_candidate).exclude(pk=obj.pk).exists():
            slug_candidate = f"{base}-{counter}"
            counter += 1
        if obj.slug != slug_candidate:
            obj.slug = slug_candidate
            self.message_user(request, f"Slug adjusted to '{obj.slug}' to avoid conflicts.")
        super().save_model(request, obj, form, change)


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'order', 'preview')
    list_filter = ('published',)
    search_fields = ('title',)
    list_editable = ('order', 'published')
    readonly_fields = ('preview',)
    ordering = ('order', 'title')
    fields = ('title', 'image', 'preview', 'order', 'published')

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:80px;" />', obj.image.url)
        return ''
    preview.short_description = 'Preview'
