from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Country, Indicator, FinancialData
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
def index(request):
    countries = Country.objects.all().order_by('name')
    # Get all indicators from the database
    indicators = Indicator.objects.all().order_by('name')
    
    # Log available indicators for debugging
    logger.info("Available indicators:")
    for ind in indicators:
        logger.info(f"ID: {ind.id}, Code: {ind.code}, Name: {ind.name}")
    
    # Convert indicators to dictionary format
    indicators_data = [
        {
            'id': ind.id,
            'code': ind.code,
            'name': ind.name
        } for ind in indicators
    ]
    
    context = {
        'countries': countries,
        'indicators': indicators_data
    }
    return render(request, 'financial_data/index.html', context)

@login_required
def get_financial_data(request, country_code, indicator):
    """API endpoint to get financial data for a specific country and indicator."""
    logger.info(f"Fetching data for country: {country_code}, indicator: {indicator}")
    
    try:
        # Get the country and indicator objects
        country = Country.objects.get(code=country_code)
        
        # Try to get indicator by code first, then by ID if that fails
        try:
            indicator_obj = Indicator.objects.get(code=indicator)
        except Indicator.DoesNotExist:
            try:
                indicator_obj = Indicator.objects.get(id=indicator)
            except (Indicator.DoesNotExist, ValueError):
                logger.warning(f"Indicator not found: {indicator}")
                return JsonResponse({'error': 'Indicator not found'}, status=404)
        
        # Get the financial data
        data = list(FinancialData.objects.filter(
            country=country,
            indicator=indicator_obj
        ).order_by('year').values('year', 'value'))

        logger.info(f"Found {len(data)} data points")
        if not data:
            logger.warning(f"No data found for country {country_code} and indicator {indicator}")
        return JsonResponse(data, safe=False)

    except Country.DoesNotExist:
        logger.warning(f"Country not found: {country_code}")
        return JsonResponse({'error': 'Country not found'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)