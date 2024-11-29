import requests
from .models import Country, Indicator, FinancialData
from django.db import transaction

WORLD_BANK_BASE_URL = "http://api.worldbank.org/v2"

def fetch_countries():
    """Fetch list of countries from World Bank API"""
    url = f"{WORLD_BANK_BASE_URL}/country"
    params = {
        'format': 'json',
        'per_page': 300  # Get all countries in one request
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()[1]  # Second element contains the actual data
        return data
    return None

def fetch_indicators():
    """Return list of predefined indicators we want to track"""
    return [
        {
            'id': 'NY.GDP.MKTP.CD',
            'name': 'GDP (current US$)',
            'description': 'Gross Domestic Product at current US dollars'
        },
        {
            'id': 'FP.CPI.TOTL.ZG',
            'name': 'Inflation Rate',
            'description': 'Inflation, consumer prices (annual %)'
        },
        {
            'id': 'BN.CAB.XOKA.CD',
            'name': 'Current Account Balance',
            'description': 'Current account balance (BoP, current US$)'
        }
    ]

def fetch_world_bank_data(indicator_id, country_code, start_year=1960, end_year=2023):
    """Fetch financial data for a specific indicator and country"""
    url = f"{WORLD_BANK_BASE_URL}/country/{country_code}/indicator/{indicator_id}"
    params = {
        'format': 'json',
        'date': f'{start_year}:{end_year}',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data[1] if len(data) > 1 else []
    return None

@transaction.atomic
def populate_database():
    """Populate database with World Bank data"""
    # Fetch and save countries
    countries_data = fetch_countries()
    if countries_data:
        for country_data in countries_data:
            Country.objects.get_or_create(
                code=country_data['id'],
                defaults={
                    'name': country_data['name'],
                    'region': country_data['region']['value']
                }
            )
    
    # Create indicators
    indicators_data = fetch_indicators()
    for indicator_data in indicators_data:
        Indicator.objects.get_or_create(
            name=indicator_data['name'],
            defaults={'description': indicator_data['description']}
        )
    
    # Fetch financial data for each country and indicator
    for country in Country.objects.all():
        for indicator_data in indicators_data:
            financial_data = fetch_world_bank_data(
                indicator_data['id'],
                country.code
            )
            
            if financial_data:
                indicator = Indicator.objects.get(name=indicator_data['name'])
                for data_point in financial_data:
                    # Store all data points, including null values
                    value = data_point['value'] if data_point['value'] is not None else None
                    FinancialData.objects.get_or_create(
                        country=country,
                        indicator=indicator,
                        year=int(data_point['date']),
                        defaults={'value': value}
                    )