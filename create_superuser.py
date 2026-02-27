import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Get credentials from environment variables (fallback to defaults if not set)
DJANGO_SU_NAME = os.environ.get('DJANGO_SU_NAME', 'admin')
DJANGO_SU_EMAIL = os.environ.get('DJANGO_SU_EMAIL', 'admin@example.com')
DJANGO_SU_PASSWORD = os.environ.get('DJANGO_SU_PASSWORD', 'admin123')

def create_superuser():
    if not User.objects.filter(username=DJANGO_SU_NAME).exists():
        print(f"Creating superuser '{DJANGO_SU_NAME}'...")
        User.objects.create_superuser(
            username=DJANGO_SU_NAME,
            email=DJANGO_SU_EMAIL,
            password=DJANGO_SU_PASSWORD
        )
        print("Superuser created successfully.")
    else:
        print(f"Superuser '{DJANGO_SU_NAME}' already exists.")

if __name__ == '__main__':
    create_superuser()
