from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from dentist_app.models import GalleryImage
from PIL import Image, ImageDraw, ImageFont
import io
import random

class Command(BaseCommand):
    help = 'Seed the gallery with sample images for layout testing.'

    def handle(self, *args, **options):
        samples = [
            ('landscape', (1200, 800), GalleryImage.Category.CLINIC),
            ('portrait', (600, 900), GalleryImage.Category.BEFORE_AFTER),
            ('square', (800, 800), GalleryImage.Category.CLINIC),
            ('wide', (1600, 700), GalleryImage.Category.BEFORE_AFTER),
            ('tall', (700, 1400), GalleryImage.Category.CLINIC),
            ('small', (300, 200), GalleryImage.Category.BEFORE_AFTER),
            ('medium', (900, 600), GalleryImage.Category.CLINIC),
            ('banner', (1400, 400), GalleryImage.Category.BEFORE_AFTER),
        ]

        created = 0
        for name, size, category in samples:
            # Create a simple placeholder image with the size text
            img = Image.new('RGB', size, color=(random.randint(100,255), random.randint(100,255), random.randint(100,255)))
            draw = ImageDraw.Draw(img)
            text = f"{name} {size[0]}x{size[1]}"
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None
            # Compute text size in a Pillow-version-compatible way
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except AttributeError:
                # Fallback for older Pillow versions
                text_w, text_h = font.getsize(text) if font else (0, 0)
            draw.text(((size[0]-text_w)/2, (size[1]-text_h)/2), text, fill=(30,30,30), font=font)

            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=85)
            buf.seek(0)

            fname = f'gallery/sample_{name}_{size[0]}x{size[1]}.jpg'

            gi = GalleryImage(title=f'Sample {name}', category=category)
            gi.image.save(fname, ContentFile(buf.read()), save=True)
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} sample gallery images.'))
