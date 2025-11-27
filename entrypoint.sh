#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Wedding Management Application...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created. Please update it with your settings.${NC}"
fi

# Wait for database
echo -e "${YELLOW}⏳ Waiting for database...${NC}"
while ! nc -z db 5432; do
    sleep 0.1
done
echo -e "${GREEN}✅ Database is ready${NC}"

# Wait for Redis
echo -e "${YELLOW}⏳ Waiting for Redis...${NC}"
while ! nc -z redis 6379; do
    sleep 0.1
done
echo -e "${GREEN}✅ Redis is ready${NC}"

# Run migrations
echo -e "${YELLOW}📦 Running database migrations...${NC}"
python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}🎨 Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Create superuser if not exists
echo -e "${YELLOW}👤 Creating superuser...${NC}"
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='${DJANGO_SUPERUSER_USERNAME:-admin}',
        email='${DJANGO_SUPERUSER_EMAIL:-admin@example.com}',
        password='${DJANGO_SUPERUSER_PASSWORD:-admin123}'
    )
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
EOF

echo -e "${GREEN}✅ Application is ready!${NC}"
echo -e "${GREEN}🌐 Starting server...${NC}"

# Start Gunicorn
exec gunicorn wedding_management.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --reload \
    --access-logfile - \
    --error-logfile -
