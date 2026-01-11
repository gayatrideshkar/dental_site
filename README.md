# Dental Site (Django)

## Setup (Windows PowerShell)

1. Activate your virtual environment (if you have one):

   ```powershell
   .\venv\Scripts\Activate.ps1
   # or if using .venv:
   .\.venv\Scripts\Activate.ps1
   ```

2. Install requirements:

   ```powershell
   pip install -r requirements.txt
   ```

3. Run migrations:

   ```powershell
   python manage.py migrate
   ```

4. Create a superuser (optional):

   ```powershell
   python manage.py createsuperuser
   ```

5. Start the development server:

   ```powershell
   python manage.py runserver
   ```

Open http://127.0.0.1:8000/ to view the site.

Pages added:
- Home: /
- About: /about/
- Treatments: /treatments/
- Gallery: /gallery/
- Testimonials: /testimonials/
- Contact: /contact/

Media & gallery admin
- Create a superuser and log in to the admin to add gallery images:
  - python manage.py createsuperuser
  - Visit http://127.0.0.1:8000/admin/ and add images under Gallery images.
- Uploaded images are served from /media/ while DEBUG=True.
- In the Gallery admin, set the category to **Clinic** or **Before & After**.

Notes: Uploaded images are stored in the `media/gallery/` folder. If you want sample images added programmatically, tell me and I can add a small script to create demo entries.
