from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Country, Indicator, FinancialData
import logging

logger = logging.getLogger(__name__)

def index(request):
    countries = Country.objects.all().order_by('name')
    # Get all indicators from the database
    indicators = Indicator.objects.all().values('code', 'name').order_by('name')
    
    context = {
        'countries': countries,
        'indicators': [{'id': ind['code'], 'name': ind['name']} for ind in indicators]
    }
    return render(request, 'financial_data/index.html', context)

def get_financial_data(request, country_code, indicator):
    """API endpoint to get financial data for a specific country and indicator."""
    logger.info(f"Fetching data for country: {country_code}, indicator: {indicator}")
    
    try:
        # Get the country and indicator objects
        country = Country.objects.get(code=country_code)
        indicator_obj = Indicator.objects.get(code=indicator)
        
        # Get the financial data
        data = list(FinancialData.objects.filter(
            country=country,
            indicator=indicator_obj
        ).order_by('year').values('year', 'value'))

        logger.info(f"Found {len(data)} data points")
        return JsonResponse(data, safe=False)

    except Country.DoesNotExist:
        logger.warning(f"Country not found: {country_code}")
        return JsonResponse([], safe=False)
    except Indicator.DoesNotExist:
        logger.warning(f"Indicator not found: {indicator}")
        return JsonResponse([], safe=False)
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}", exc_info=True)
        return JsonResponse([], safe=False)