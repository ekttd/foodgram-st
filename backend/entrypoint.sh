#!/bin/sh
set -e

echo "===> WAITING FOR POSTGRES..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
  sleep 1
done

echo "===> POSTGRES IS UP"

echo "===> APPLYING MIGRATIONS..."
python manage.py migrate

echo "===> CHECKING INGREDIENTS EXISTENCE..."

# Получаем только число, подавляя всё остальное
INGREDIENT_COUNT=$(python manage.py shell -c "import django; django.setup(); from recipes.models import Ingredient; print(Ingredient.objects.count())" 2>/dev/null | tail -n 1 | tr -d '\r')

echo "Found $INGREDIENT_COUNT ingredients in database."

if [ "$INGREDIENT_COUNT" -eq 0 ]; then
  echo "===> INGREDIENTS NOT FOUND, LOADING FIXTURE..."
  python manage.py loaddata /app/data/ingredients_fixture.json
else
  echo "===> INGREDIENTS ALREADY EXIST, SKIPPING FIXTURE LOAD"
fi

echo "===> COLLECTING STATIC FILES..."
python manage.py collectstatic --noinput

echo "===> STARTING GUNICORN..."
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
