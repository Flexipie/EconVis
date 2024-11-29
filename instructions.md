# INSTRUCTIONS.md

cd /Users/flexipie/Desktop/Code/Projects/FinanceVis/macrovis

python manage.py runserver

http://127.0.0.1:8000

# make migrations
python manage.py makemigrations
python manage.py migrate

# fetch data
python manage.py fetch_worldbank_data


# Clear Data
python manage.py shell

from financial_data.models import FinancialData
FinancialData.objects.all().delete()
exit()