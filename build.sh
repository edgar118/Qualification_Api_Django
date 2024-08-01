set -0 errexit

pip install -r requirements.txt

python manage.py collecstatic --no-input
python manage.py migrate