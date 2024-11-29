from django.core.management.base import BaseCommand
from financial_data.models import Country, Indicator, FinancialData
import requests
import time

class Command(BaseCommand):
    help = 'Fetch financial data from World Bank API'

    def handle(self, *args, **options):
        # Extended list of countries
        countries = [
            # G7 Countries
            {'code': 'USA', 'name': 'United States'},
            {'code': 'GBR', 'name': 'United Kingdom'},
            {'code': 'DEU', 'name': 'Germany'},
            {'code': 'FRA', 'name': 'France'},
            {'code': 'JPN', 'name': 'Japan'},
            {'code': 'ITA', 'name': 'Italy'},
            {'code': 'CAN', 'name': 'Canada'},
            
            # BRICS Countries
            {'code': 'CHN', 'name': 'China'},
            {'code': 'IND', 'name': 'India'},
            {'code': 'BRA', 'name': 'Brazil'},
            {'code': 'RUS', 'name': 'Russia'},
            {'code': 'ZAF', 'name': 'South Africa'},
            
            # European Countries
            {'code': 'ESP', 'name': 'Spain'},
            {'code': 'NLD', 'name': 'Netherlands'},
            {'code': 'CHE', 'name': 'Switzerland'},
            {'code': 'SWE', 'name': 'Sweden'},
            {'code': 'NOR', 'name': 'Norway'},
            {'code': 'DNK', 'name': 'Denmark'},
            {'code': 'FIN', 'name': 'Finland'},
            {'code': 'POL', 'name': 'Poland'},
            
            # Asian Tigers & Major Asian Economies
            {'code': 'KOR', 'name': 'South Korea'},
            {'code': 'SGP', 'name': 'Singapore'},
            {'code': 'HKG', 'name': 'Hong Kong'},
            {'code': 'TWN', 'name': 'Taiwan'},
            {'code': 'IDN', 'name': 'Indonesia'},
            {'code': 'THA', 'name': 'Thailand'},
            {'code': 'MYS', 'name': 'Malaysia'},
            {'code': 'VNM', 'name': 'Vietnam'},
            
            # Oceania
            {'code': 'AUS', 'name': 'Australia'},
            {'code': 'NZL', 'name': 'New Zealand'},
            
            # Latin America
            {'code': 'MEX', 'name': 'Mexico'},
            {'code': 'ARG', 'name': 'Argentina'},
            {'code': 'CHL', 'name': 'Chile'},
            {'code': 'COL', 'name': 'Colombia'},
            {'code': 'PER', 'name': 'Peru'},
            
            # Middle East
            {'code': 'SAU', 'name': 'Saudi Arabia'},
            {'code': 'ARE', 'name': 'United Arab Emirates'},
            {'code': 'ISR', 'name': 'Israel'},
            {'code': 'TUR', 'name': 'Turkey'},
            {'code': 'EGY', 'name': 'Egypt'}
        ]

        # Extended list of indicators with World Bank codes
        indicators = [
            # Core Economic Indicators
            {'code': 'NY.GDP.MKTP.CD', 'name': 'GDP (current US$)'},
            {'code': 'NY.GDP.PCAP.CD', 'name': 'GDP per capita (current US$)'},
            {'code': 'NY.GDP.MKTP.KD.ZG', 'name': 'GDP growth (annual %)'},
            
            # Inflation and Prices
            {'code': 'FP.CPI.TOTL.ZG', 'name': 'Inflation Rate'},
            {'code': 'NFPI.TOTL', 'name': 'Food Price Index'},
            
            # Employment
            {'code': 'SL.UEM.TOTL.ZS', 'name': 'Unemployment Rate'},
            {'code': 'SL.TLF.CACT.ZS', 'name': 'Labor Force Participation Rate'},
            {'code': 'SL.EMP.TOTL.SP.ZS', 'name': 'Employment to Population Ratio'},
            
            # External Sector
            {'code': 'BN.CAB.XOKA.CD', 'name': 'Current Account Balance'},
            {'code': 'NE.EXP.GNFS.ZS', 'name': 'Exports of goods and services (% of GDP)'},
            {'code': 'NE.IMP.GNFS.ZS', 'name': 'Imports of goods and services (% of GDP)'},
            {'code': 'BX.KLT.DINV.WD.GD.ZS', 'name': 'Foreign Direct Investment (% of GDP)'},
            
            # Government and Debt
            {'code': 'GC.DOD.TOTL.GD.ZS', 'name': 'Government Debt to GDP'},
            {'code': 'GC.TAX.TOTL.GD.ZS', 'name': 'Tax Revenue (% of GDP)'},
            
            # Financial Sector
            {'code': 'FR.INR.LEND', 'name': 'Lending Interest Rate'},
            {'code': 'CM.MKT.LCAP.GD.ZS', 'name': 'Stock Market Capitalization to GDP'},
            
            # Social and Development
            {'code': 'SI.POV.GINI', 'name': 'GINI Index'},
            {'code': 'SP.DYN.LE00.IN', 'name': 'Life Expectancy'},
            {'code': 'SE.XPD.TOTL.GD.ZS', 'name': 'Education Expenditure (% of GDP)'}
        ]

        # Create or update countries
        for country_data in countries:
            Country.objects.update_or_create(
                code=country_data['code'],
                defaults={'name': country_data['name']}
            )
            self.stdout.write(f"Added/Updated country: {country_data['name']}")

        # Create or update indicators
        for indicator_data in indicators:
            Indicator.objects.update_or_create(
                code=indicator_data['code'],
                defaults={'name': indicator_data['name']}
            )
            self.stdout.write(f"Added/Updated indicator: {indicator_data['name']}")

        # Fetch data with improved error handling and rate limiting
        for country in countries:
            country_obj = Country.objects.get(code=country['code'])
            for indicator in indicators:
                indicator_obj = Indicator.objects.get(code=indicator['code'])
                self.fetch_indicator_data(country_obj, indicator_obj)
                time.sleep(1.5)  # Increased delay to be more conservative with API limits

        self.stdout.write(self.style.SUCCESS('Successfully fetched all data'))

    def fetch_indicator_data(self, country, indicator):
        url = f"http://api.worldbank.org/v2/countries/{country.code}/indicators/{indicator.code}"
        params = {
            'format': 'json',
            'per_page': 100,
            'date': '1960:2023'
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if len(data) < 2:
                self.stdout.write(self.style.WARNING(f"No data found for {country.code} - {indicator.code}"))
                return

            # Clear existing data for this country and indicator
            FinancialData.objects.filter(country=country, indicator=indicator).delete()

            # Add new data
            batch_data = []
            for entry in data[1]:
                if entry['value'] is not None:
                    batch_data.append(FinancialData(
                        country=country,
                        indicator=indicator,
                        year=int(entry['date']),
                        value=float(entry['value']) if entry['value'] is not None else None
                    ))
            
            # Bulk create for better performance
            if batch_data:
                FinancialData.objects.bulk_create(batch_data)

            self.stdout.write(f"Updated data for {country.code} - {indicator.code}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data for {country.code} - {indicator.code}: {str(e)}"))