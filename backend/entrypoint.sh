#!/bin/sh
set -e


while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

python manage.py migrate

INGREDIENT_COUNT=$(python manage.py shell -c "import django; django.setup(); from recipes.models import Ingredient; print(Ingredient.objects.count())" 2>/dev/null | tail -n 1 | tr -d '\r')

if [ "$INGREDIENT_COUNT" -eq 0 ]; then
  python manage.py loaddata /app/data/ingredients_fixture.json
else
  echo "===> INGREDIENTS ALREADY EXIST, SKIPPING FIXTURE LOAD"
fi

python manage.py collectstatic --noinput

gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
