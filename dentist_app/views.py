from django.shortcuts import render

def index(request):
    # Render the new Home page with a small gallery preview
    clinic_preview = GalleryImage.objects.filter(category=GalleryImage.Category.CLINIC)[:3]
    ba_preview = GalleryImage.objects.filter(category=GalleryImage.Category.BEFORE_AFTER)[:3]

    # Ensure sample services exist and fetch the top published services for the home page
    _ensure_sample_services()
    top_services = Service.objects.filter(published=True).order_by('order')[:6]

    return render(request, "home.html", {"clinic_preview": clinic_preview, "ba_preview": ba_preview, "top_services": top_services})

def about(request):
    return render(request, "about.html")

def treatments(request):
    # list of example treatment categories
    treatments_list = ["Cleaning", "Teeth Whitening", "Fillings", "Crowns", "Braces"]
    return render(request, "treatments.html", {"treatments": treatments_list})

from .models import GalleryImage

def gallery(request):
    # Query all images and separate into clinic and before/after groups
    clinic_images = GalleryImage.objects.filter(category=GalleryImage.Category.CLINIC).order_by('-uploaded_at')
    ba_images = GalleryImage.objects.filter(category=GalleryImage.Category.BEFORE_AFTER).order_by('-uploaded_at')
    return render(request, "gallery.html", {"clinic_images": clinic_images, "ba_images": ba_images})

def posts(request):
    from django.urls import reverse
    from .models import Post
    # Use phone from ContactInfo if present
    try:
        contact_obj = ContactInfo.objects.first()
        call_link = contact_obj.phone_link if contact_obj and contact_obj.phone_link else 'tel:+919422178603'
    except Exception:
        call_link = 'tel:+919422178603'

    book_link = reverse('contact')

    qs = Post.objects.filter(published=True).order_by('-published_at')[:12]
    posts = []
    for p in qs:
        posts.append({
            'title': p.title,
            'excerpt': p.excerpt,
            'date': p.published_at.strftime('%B %d, %Y') if p.published_at else '',
            'image_url': p.image.url if p.image else None,
            'book_link': book_link,
            'call_link': call_link,
        })

    return render(request, "posts.html", {"posts": posts, "book_link": book_link, "call_link": call_link})

from urllib.parse import quote_plus
import qrcode
from django.conf import settings
import os
from pathlib import Path
import datetime
import re


def contact(request):
    # Contact details for the sample contact page
    phone_display = "+91 9422178603"
    phone_link = "tel:+919422178603"
    address_display = "Sharada Dental Clinic, Khamla Rd, Near Tajshree Honda, Ramakrishna Nagar, Deo Nagar, Nagpur, Maharashtra 440015"
    # Google Maps search link for the address
    maps_query = quote_plus("Sharada Dental Clinic, Khamla Rd, Near Tajshree Honda, Ramakrishna Nagar, Deo Nagar, Nagpur, Maharashtra 440015")
    gmap_url = f"https://www.google.com/maps/search/?api=1&query={maps_query}"
    # Get contact info from the database if present
    from .models import ContactInfo, OpeningHour

    contact_obj = ContactInfo.objects.first()
    if contact_obj:
        phone_display = phone_display or contact_obj.phone_display
        phone_link = phone_link or contact_obj.phone_link
        address_display = contact_obj.address_display or address_display
        email = contact_obj.email or email
        doctor_name = contact_obj.doctor_name or doctor_name

        # Load opening hours from related OpeningHour rows
        raw_hours = []
        hours_qs = contact_obj.hours.all().order_by('order')
        for h in hours_qs:
            if not h.periods:
                periods = []
            else:
                periods = [p.strip() for p in h.periods.splitlines() if p.strip()]
            raw_hours.append((h.day, periods))
    else:
        raw_hours = [
            ("Monday", ["10 am–1 pm", "5 pm–8 pm"]),
            ("Tuesday", ["10 am–1 pm", "5 pm–8 pm"]),
            ("Wednesday", ["10 am–1 pm", "5 pm–8 pm"]),
            ("Thursday", ["10 am–1 pm", "5 pm–8 pm"]),
            ("Friday", ["10 am–1 pm", "5 pm–8 pm"]),
            ("Saturday", ["10 am–1 pm", "5 pm–8 pm"]),
            ("Sunday", []),
        ]

    # Generate QR code image locally under MEDIA_ROOT/qr (saved once) using address hash-based filename
    qr_dir = Path(settings.MEDIA_ROOT) / 'qr'
    qr_dir.mkdir(parents=True, exist_ok=True)
    import hashlib
    address_hash = hashlib.sha1(address_display.encode('utf-8')).hexdigest()[:10]
    qr_filename = f'maps_{address_hash}.png'
    qr_path = qr_dir / qr_filename
    if not qr_path.exists():
        img = qrcode.make(gmap_url)
        img.save(qr_path)
    qr_url = settings.MEDIA_URL + f'qr/{qr_filename}'

    # Helpers to parse periods like "10 am–1 pm" or "5 pm–8 pm" and check current open status
    def _parse_period(period_str):
        s = period_str.replace('\u202f', ' ').replace('\u2009', ' ').replace('–', '-').replace('—', '-')
        s = s.strip()
        if s.lower() == 'closed':
            return None
        if '-' not in s:
            return None
        left, right = [p.strip() for p in s.split('-', 1)]
        # Ensure am/pm tokens present on both sides where possible
        left_has = re.search(r'(?i)(am|pm)$', left)
        right_has = re.search(r'(?i)(am|pm)$', right)
        if right_has and not left_has:
            left = f"{left} {right_has.group(1)}"
        if left_has and not right_has:
            right = f"{right} {left_has.group(1)}"
        # Normalize e.g. '5pm' -> '5 pm'
        left = re.sub(r'(?i)(\d)(am|pm)$', r'\1 \2', left)
        right = re.sub(r'(?i)(\d)(am|pm)$', r'\1 \2', right)
        fmts = ['%I %p', '%I:%M %p']
        start = end = None
        for fmt in fmts:
            try:
                start = datetime.datetime.strptime(left, fmt).time()
                break
            except Exception:
                pass
        for fmt in fmts:
            try:
                end = datetime.datetime.strptime(right, fmt).time()
                break
            except Exception:
                pass
        if not start or not end:
            return None
        return (start, end)

    def _is_now_in_periods(periods):
        now = datetime.datetime.now().time()
        for p in periods:
            parsed = _parse_period(p)
            if not parsed:
                continue
            start, end = parsed
            if start <= now <= end:
                return True
        return False

    today_name = datetime.datetime.now().strftime('%A')
    opening_hours = []
    for day, periods in raw_hours:
        is_today = (day == today_name)
        is_open = is_today and _is_now_in_periods(periods)
        opening_hours.append({
            'day': day,
            'periods': periods,
            'is_today': is_today,
            'is_open': is_open,
        })

    context = {
        "phone_display": phone_display,
        "phone_link": phone_link,
        "address_display": address_display,
        "gmap_url": gmap_url,
        "qr_url": qr_url,
        "email": email,
        "doctor_name": doctor_name,
        "opening_hours": opening_hours,
    }
    return render(request, "contact.html", context)


from .models import Service
from django.shortcuts import get_object_or_404
from django.http import Http404


def _ensure_sample_services():
    """Create sample services when none exist so the site shows example content.
    This is handy for demo sites — real content should be added/edited via admin.
    """
    if Service.objects.exists():
        return

    sample = [
        {
            'title': 'Scaling & Polishing',
            'slug': 'scaling-polishing',
            'short_description': 'Gentle cleaning to remove plaque and restore brightness.',
            'description': 'Example: A typical scaling & polishing session removes hardened plaque and stains to leave the teeth feeling smooth and looking brighter. This is a short sample paragraph that you can replace from the admin later.',
            'order': 1,
        },
        {
            'title': 'Root Canal Treatment',
            'slug': 'root-canal-treatment',
            'short_description': 'Advanced endodontic care to relieve pain and save teeth.',
            'description': 'Example: Root canal treatment removes infection from inside the tooth and seals it to prevent reinfection. Replace this text from the admin with the actual procedure details and post-op instructions.',
            'order': 2,
        },
        {
            'title': 'Dental Implants',
            'slug': 'dental-implants',
            'short_description': 'Long-lasting tooth replacement solutions for confident smiles.',
            'description': 'Example: Dental implants replace missing teeth with titanium posts and natural-looking crowns. Use the admin to provide implant materials and recovery timelines for patients.',
            'order': 3,
        },
        {
            'title': 'Braces & Aligners',
            'slug': 'braces',
            'short_description': 'Orthodontic care for children and adults to align teeth.',
            'description': 'Example: Braces and clear aligners gradually move teeth into a desired position. Replace this example paragraph with appliance types, treatment lengths, and follow-up schedules in the admin.',
            'order': 4,
        },
        {
            'title': 'Teeth Whitening',
            'slug': 'teeth-whitening',
            'short_description': 'Brighten your smile with safe and effective whitening.',
            'description': 'Example: In-clinic whitening sessions safely brighten teeth in about an hour. Update this content to include product names and expected shade improvement.',
            'order': 5,
        },
    ]
    for item in sample:
        Service.objects.create(**item)


def services_list(request):
    _ensure_sample_services()
    services = Service.objects.filter(published=True).order_by('order')
    return render(request, "services_list.html", {"services": services})


def services_detail(request, slug):
    # Ensure sample services exist even if the list page hasn't been visited yet
    _ensure_sample_services()
    service = get_object_or_404(Service, slug=slug, published=True)
    return render(request, "services_detail.html", {"service": service})
