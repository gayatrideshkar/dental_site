from django.db import models
from django.urls import reverse

class Service(models.Model):
    """A simple Service model for treatments offered by the clinic."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.CharField(max_length=255, blank=True)
    # Editable sections for the service detail page
    what_is = models.TextField(blank=True, help_text='What it is (displayed under the "What it is" label)')
    why_necessary = models.TextField(blank=True, help_text='Why it\'s necessary (displayed under the label)')
    when_to_do = models.TextField(blank=True, help_text='When to do it (displayed under the label)')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Simple post model for site posts used on the posts page (formerly posts)."""
    title = models.CharField(max_length=200)
    # Allow blank slug and remove DB-level uniqueness so titles can be duplicated in admin.
    slug = models.SlugField(max_length=200, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    published = models.BooleanField(default=True)
    published_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', 'title']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Ensure the slug is set and unique.

        Behavior:
        - If the slug is empty, generate one from the title.
        - If a slug is provided manually, sanitize it and ensure uniqueness.
        - If there's a conflict, append -1, -2 etc until unique (excluding this instance).
        This prevents integrity errors when saving via the admin.
        """
        from django.utils.text import slugify

        # Base candidate: provided slug (sanitized) or derived from title
        if self.slug:
            base = slugify(self.slug) or slugify(self.title) or 'post'
        else:
            base = slugify(self.title) or 'post'

        slug_candidate = base
        counter = 1
        # ensure uniqueness, ignoring this instance when updating
        while Post.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
            slug_candidate = f"{base}-{counter}"
            counter += 1
        self.slug = slug_candidate

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('services_detail', args=[self.slug])


class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('clinic', 'Clinic'),
        ('before_after', 'Before & After'),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    thumbnail = models.ImageField(upload_to='gallery/thumbnails/', blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='clinic')
    order = models.PositiveSmallIntegerField(default=0)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Gallery image'
        verbose_name_plural = 'Gallery images'

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    class Category(models.TextChoices):
        CLINIC = 'clinic', 'Clinic'
        BEFORE_AFTER = 'before_after', 'Before & After'

    title = models.CharField(max_length=150, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to='gallery/')
    thumbnail = models.ImageField(upload_to='gallery/thumbnails/', blank=True, null=True)
    category = models.CharField(max_length=32, choices=Category.choices, default=Category.CLINIC)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Save original image and create a resized main image and thumbnail."""
        processed = kwargs.pop('_processed', False)
        super().save(*args, **kwargs)

        # Only process if we haven't already and if file is a raster image
        if processed:
            return

        if not self.image:
            return

        name = self.image.name.lower()
        if name.endswith('.svg') or name.endswith('.gif'):
            # Skip vector and animated gifs for now
            return

        try:
            from PIL import Image
            import os
            from io import BytesIO
            from django.core.files.base import ContentFile

            img_path = self.image.path
            img = Image.open(img_path)

            # Convert to RGB (drop alpha) to ensure JPEG compatibility
            if img.mode in ("RGBA", "P"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
                img = bg

            # Resize main image if too large
            max_size = (1600, 1600)
            if img.width > max_size[0] or img.height > max_size[1]:
                img.thumbnail(max_size, Image.LANCZOS)
                buf = BytesIO()
                img.save(buf, format='JPEG', quality=85, optimize=True)
                self.image.save(self.image.name, ContentFile(buf.getvalue()), save=False)

            # Create thumbnail
            thumb = img.copy()
            thumb.thumbnail((900, 600), Image.LANCZOS)
            thumb_buf = BytesIO()
            thumb_name = f"thumb_{os.path.basename(self.image.name)}"
            thumb.save(thumb_buf, format='JPEG', quality=80, optimize=True)
            self.thumbnail.save(thumb_name, ContentFile(thumb_buf.getvalue()), save=False)

            # Save again but mark as processed to avoid recursion
            super().save(_processed=True)
        except Exception as e:
            # Don't break on image processing errors; thumbnail will be empty
            pass

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Gallery image'
        verbose_name_plural = 'Gallery images'

    def __str__(self):
        return self.title or f"GalleryImage {self.pk}"


# Contact models to make contact details editable in admin
class ContactInfo(models.Model):
    phone_display = models.CharField(max_length=64, blank=True, help_text='Human-readable phone number')
    phone_link = models.CharField(max_length=64, blank=True, help_text='tel:+... number')
    address_display = models.TextField(blank=True, help_text='Address to show on the contact page')
    email = models.EmailField(blank=True)
    doctor_name = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Contact information'
        verbose_name_plural = 'Contact information'

    def __str__(self):
        return f"Contact info"


class OpeningHour(models.Model):
    DAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    contact = models.ForeignKey(ContactInfo, related_name='hours', on_delete=models.CASCADE)
    day = models.CharField(max_length=12, choices=DAYS)
    order = models.PositiveSmallIntegerField(default=0)
    periods = models.TextField(blank=True, help_text='One period per line, e.g. "10 am–1 pm"')

    class Meta:
        ordering = ['order']
        verbose_name = 'Opening hour'
        verbose_name_plural = 'Opening hours'

    def __str__(self):
        return f"{self.day}: {self.periods or 'Closed'}"


class Certification(models.Model):
    """Model for certifications, qualifications, and other images to display on the About page."""
    title = models.CharField(max_length=200, help_text='Name of the certification or qualification')
    image = models.ImageField(upload_to='certifications/', help_text='Upload certification image, logo, or badge')
    order = models.PositiveSmallIntegerField(default=0, help_text='Display order')
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'

    def __str__(self):
        return self.title
