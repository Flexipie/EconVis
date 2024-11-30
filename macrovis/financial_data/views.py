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
        
        # Return data in the format expected by the frontend
        response_data = {
            'country': country.name,
            'indicator': indicator_obj.name,
            'values': data
        }
        return JsonResponse(response_data)

    except Country.DoesNotExist:
        logger.warning(f"Country not found: {country_code}")
        return JsonResponse({'error': 'Country not found'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required
def advanced_filters(request):
    """View for the advanced filtering page"""
    countries = Country.objects.all().order_by('name')
    indicators = Indicator.objects.all().order_by('name')
    context = {
        'countries': countries,
        'indicators': indicators,
    }
    return render(request, 'financial_data/advanced_filters.html', context)

@login_required
def filter_data(request):
    """API endpoint for advanced filtering"""
    try:
        # Get filter parameters from request
        indicator_id = request.GET.get('indicator')
        start_year = request.GET.get('start_year')
        end_year = request.GET.get('end_year')
        min_value = request.GET.get('min_value')
        max_value = request.GET.get('max_value')
        countries = request.GET.getlist('countries[]')
        aggregation = request.GET.get('aggregation')  # 'avg', 'sum', 'min', 'max'

        # Start with base query
        query = FinancialData.objects.select_related('country', 'indicator')

        # Apply filters
        if indicator_id:
            query = query.filter(indicator_id=indicator_id)
        if countries:
            query = query.filter(country__code__in=countries)
        if start_year:
            query = query.filter(year__gte=start_year)
        if end_year:
            query = query.filter(year__lte=end_year)
        if min_value:
            query = query.filter(value__gte=float(min_value))
        if max_value:
            query = query.filter(value__lte=float(max_value))

        # Apply aggregation if requested
        if aggregation:
            from django.db.models import Avg, Sum, Min, Max
            agg_functions = {
                'avg': Avg('value'),
                'sum': Sum('value'),
                'min': Min('value'),
                'max': Max('value')
            }
            
            # Group by country and year
            query = query.values('country__name', 'year').annotate(
                value=agg_functions.get(aggregation)
            ).order_by('country__name', 'year')
        else:
            # If no aggregation, just get the regular data
            query = query.values(
                'country__name',
                'year',
                'value'
            ).order_by('country__name', 'year')

        data = list(query)
        return JsonResponse({
            'data': data,
            'count': len(data)
        })

    except Exception as e:
        logger.error(f"Error in filter_data: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def compare_countries(request):
    """API endpoint to compare multiple countries"""
    try:
        indicator_id = request.GET.get('indicator')
        countries = request.GET.getlist('countries[]')
        year = request.GET.get('year')

        if not all([indicator_id, countries, year]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        # Use raw SQL for more complex comparison
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.name as country_name,
                    fd.value,
                    fd.year,
                    (
                        SELECT AVG(value)
                        FROM financial_data fd2
                        WHERE fd2.indicator_id = %s
                        AND fd2.year = %s
                    ) as average_value
                FROM financial_data fd
                JOIN country c ON fd.country_id = c.id
                WHERE fd.indicator_id = %s
                AND fd.year = %s
                AND c.code = ANY(%s)
                ORDER BY fd.value DESC
            """, [indicator_id, year, indicator_id, year, countries])
            
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return JsonResponse({
            'data': data,
            'count': len(data)
        })

    except Exception as e:
        logger.error(f"Error in compare_countries: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)