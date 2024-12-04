# financial_data/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Country, Indicator, FinancialData, FavoriteComparison, LastSearch
from django.contrib.auth.decorators import login_required
import logging
import json  # Import the json module
from django.contrib import messages

logger = logging.getLogger(__name__)

@login_required
def index(request):
    countries = Country.objects.all().order_by('name')
    indicators = Indicator.objects.all().order_by('name')

    # Log available indicators for debugging
    logger.info("Available indicators:")
    for ind in indicators:
        logger.info(f"ID: {ind.id}, Code: {ind.code}, Name: {ind.name}")

    context = {
        'countries': countries,
        'indicators': indicators
    }
    return render(request, 'financial_data/index.html', context)

@login_required
def get_financial_data(request, country_code, indicator):
    """API endpoint to get financial data for a specific country and indicator."""
    logger.info(f"Fetching data for country: {country_code}, indicator: {indicator}")

    try:
        # Get the country object
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

@login_required
def add_favorite(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            country1 = data.get('country1')
            country2 = data.get('country2')
            index = data.get('index')

            logger.info(f"Received favorite data: {country1}, {country2}, {index}")

            if not (country1 and country2 and index):
                logger.error("Invalid data received")
                return JsonResponse({'message': 'Invalid data'}, status=400)

            # Create the favorite comparison
            FavoriteComparison.objects.create(
                user=request.user,
                country1=country1,
                country2=country2,
                index=index
            )
            return JsonResponse({'message': 'Favorite added successfully'})

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Error saving favorite: {e}")
            return JsonResponse({'message': 'Internal server error'}, status=500)
    else:
        logger.error("Invalid request method")
        return JsonResponse({'message': 'Invalid request method'}, status=405)

@login_required
def list_favorites(request):
    favorites = FavoriteComparison.objects.filter(user=request.user).order_by('-created_at')
    favorite_list = []
    
    for fav in favorites:
        try:
            # Fetch the Indicator object based on the index code
            indicator = Indicator.objects.get(code=fav.index)
            indicator_name = indicator.name
        except Indicator.DoesNotExist:
            # Fallback to the index code if the name isn't found
            indicator_name = fav.index
        
        # Construct a readable name for the favorite
        favorite_name = f"{fav.country1} vs {fav.country2} -- {indicator_name}"
        
        favorite_list.append({
            'id': fav.id,
            'name': favorite_name
        })
    
    logger.info(f"Favorites for user {request.user.username}: {[fav['name'] for fav in favorite_list]}")
    return JsonResponse({'favorites': favorite_list})

@login_required
def load_favorite(request, favorite_id):
    favorite = get_object_or_404(FavoriteComparison, id=favorite_id, user=request.user)
    return JsonResponse({
        'country1': favorite.country1,
        'country2': favorite.country2,
        'index': favorite.index
    })

@login_required
def delete_favorite(request, favorite_id):
    if request.method == 'POST':
        favorite = get_object_or_404(FavoriteComparison, id=favorite_id, user=request.user)
        try:
            favorite.delete()
            logger.info(f"Favorite {favorite_id} deleted by user {request.user.username}.")
            return JsonResponse({'message': 'Favorite deleted successfully'})
        except Exception as e:
            logger.error(f"Error deleting favorite {favorite_id}: {e}")
            return JsonResponse({'message': 'Error deleting favorite'}, status=500)
    else:
        logger.error("Invalid request method for delete_favorite")
        return JsonResponse({'message': 'Invalid request method'}, status=405)
    
@login_required
def add_last_search(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            country1 = data.get('country1')
            country2 = data.get('country2')
            indicator = data.get('index')

            logger.info(f"Received last search data: {country1}, {country2}, {indicator}")

            if not (country1 and country2 and indicator):
                logger.error("Invalid data received for last search")
                return JsonResponse({'message': 'Invalid data'}, status=400)
            
            # Create the last search
            LastSearch.objects.create(
                user=request.user,
                country1=country1,
                country2=country2,
                indicator=indicator
            )
            
            # Ensure only the latest 5 searches are kept
            last_searches = LastSearch.objects.filter(user=request.user).order_by('-created_at')
            if last_searches.count() > 5:
                # Delete the oldest searches beyond the 5th
                for search in last_searches[5:]:
                    search.delete()
            
            return JsonResponse({'message': 'Last search added successfully'})
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Error saving last search: {e}")
            return JsonResponse({'message': 'Internal server error'}, status=500)
    else:
        logger.error("Invalid request method for add_last_search")
        return JsonResponse({'message': 'Invalid request method'}, status=405)

@login_required
def list_last_searches(request):
    last_searches = LastSearch.objects.filter(user=request.user).order_by('-created_at')[:5]
    last_search_list = []
    
    for search in last_searches:
        try:
            indicator_obj = Indicator.objects.get(code=search.indicator)
            indicator_name = indicator_obj.name
        except Indicator.DoesNotExist:
            indicator_name = search.indicator
        
        search_name = f"{search.country1} vs {search.country2} -- {indicator_name}"
        search_date = search.created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        last_search_list.append({
            'id': search.id,
            'name': search_name,
            'date': search_date
        })
    
    logger.info(f"Last searches for user {request.user.username}: {[s['name'] for s in last_search_list]}")
    return JsonResponse({'last_searches': last_search_list})

@login_required
def delete_all_last_searches(request):
    if request.method == 'POST':
        LastSearch.objects.filter(user=request.user).delete()
        # messages.success(request, "All your last searches have been deleted.")
        return redirect('financial_data:index')  # Replace 'index' with your actual dashboard URL name
    else:
        messages.error(request, "Invalid request method.")
        return redirect('financial_data:index')

@login_required
def export_financial_data(request, country_code, indicator_code):
    # Query the data based on the country_code and indicator_code
    financial_data = FinancialData.objects.filter(country__code=country_code, indicator__code=indicator_code)

    # Create a response object and set content type for CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{country_code}_{indicator_code}_financial_data.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Date', 'Value'])  # Write header row
    for data in financial_data:
        writer.writerow([data.date, data.value])  # Customize this based on your model fields

    return response
