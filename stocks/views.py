import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Favorite, PortfolioItem
from .services import get_stock_info, get_historical_data

def dashboard(request):
    """
    Main dashboard showing a search bar and user's favorites.
    """
    favorites = []
    if request.user.is_authenticated:
        # Premium color palette for the charts
        color_palette = [
            '#3b82f6', # Blue
            '#10b981', # Green
            '#f59e0b', # Yellow/Orange
            '#ef4444', # Red
            '#8b5cf6', # Purple
            '#ec4899', # Pink
            '#06b6d4'  # Cyan
        ]
        
        fav_objects = Favorite.objects.filter(user=request.user)
        for i, fav in enumerate(fav_objects):
            # We could cache this info to avoid multiple yfinance calls
            info = get_stock_info(fav.ticker)
            if info['valid']:
                # Assign a color from the palette based on the index
                info['color'] = color_palette[i % len(color_palette)]
                favorites.append(info)
    
    return render(request, 'stocks/dashboard.html', {
        'favorites': favorites,
    })

def search_stock(request):
    """
    Search for a stock ticker.
    """
    query = request.GET.get('q', '').upper().strip()
    if not query:
        return render(request, 'stocks/search_results.html', {'error': 'Por favor, insira um ticker.'})
    
    info = get_stock_info(query)
    if not info['valid']:
        return render(request, 'stocks/search_results.html', {'error': f'Ação "{query}" não encontrada.'})
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, ticker=query).exists()
    
    return render(request, 'stocks/search_results.html', {
        'stock': info,
        'is_favorite': is_favorite,
        'query': query
    })

def stock_detail(request, ticker):
    """
    Show detailed info and historical chart for a specific stock.
    """
    ticker = ticker.upper()
    info = get_stock_info(ticker)
    if not info['valid']:
        return render(request, 'stocks/detail.html', {'error': f'Ação "{ticker}" não encontrada.'})
    
    info['dividend_yield_display'] = info.get('dividend_yield', 0.0) * 100
    
    historical_data = get_historical_data(ticker)
    
    is_favorite = False
    portfolio_quantity = 0.0
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, ticker=ticker).exists()
        portfolio_item = PortfolioItem.objects.filter(user=request.user, ticker=ticker).first()
        if portfolio_item:
            portfolio_quantity = float(portfolio_item.quantity)
    
    return render(request, 'stocks/detail.html', {
        'stock': info,
        'historical_data_json': json.dumps(historical_data),
        'is_favorite': is_favorite,
        'portfolio_quantity': portfolio_quantity
    })

@require_POST
def toggle_favorite(request):
    """
    Toggle a ticker in the user's favorite list.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Você precisa estar logado.'}, status=403)
    
    ticker = request.POST.get('ticker', '').upper()
    name = request.POST.get('name', '')
    
    if not ticker:
        return JsonResponse({'error': 'Ticker não fornecido.'}, status=400)
    
    favorite, created = Favorite.objects.get_or_create(user=request.user, ticker=ticker)
    
    if not created:
        favorite.delete()
        action = 'removed'
    else:
        favorite.name = name
        favorite.save()
        action = 'added'
    
    return JsonResponse({'status': 'success', 'action': action})

def api_stock_history(request, ticker):
    """
    API endpoint to fetch historical data for the interactive chart.
    """
    period = request.GET.get('period', '1mo')
    
    # Valid periods broadly accepted by yfinance
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', 'ytd', '1y', '5y', 'max']
    if period not in valid_periods:
        period = '1mo'
        
    historical_data = get_historical_data(ticker, period=period)
    
    if historical_data is None:
        return JsonResponse({'error': 'Failed to fetch data'}, status=400)
        
    return JsonResponse({'data': historical_data, 'period': period})

@login_required
def portfolio_view(request):
    """
    Shows the user's stock portfolio, total value and estimated passive income.
    """
    portfolio_items = PortfolioItem.objects.filter(user=request.user)
    
    total_value = 0
    total_annual_income = 0
    items_with_dividends = []
    items_without_dividends = []
    
    for item in portfolio_items:
        info = get_stock_info(item.ticker)
        if info['valid']:
            current_price = info.get('price', 0.0)
            dy = info.get('dividend_yield', 0.0) # Decimal (e.g. 0.12 for 12%)
            
            quantity = float(item.quantity)
            value = quantity * current_price
            
            # For the annual income prediction, we multiply total value by the annual Yield.
            annual_income = value * dy
            
            total_value += value
            total_annual_income += annual_income
            
            item_data = {
                'ticker': item.ticker,
                'name': info['name'],
                'quantity': quantity,
                'current_price': current_price,
                'total_value': value,
                'dy_percent': dy * 100,
                'annual_income': annual_income,
                'monthly_income': annual_income / 12.0,
                'currency': info['currency']
            }
            
            if dy > 0:
                items_with_dividends.append(item_data)
            else:
                items_without_dividends.append(item_data)
            
    context = {
        'items_with_dividends': items_with_dividends,
        'items_without_dividends': items_without_dividends,
        'has_items': bool(items_with_dividends or items_without_dividends),
        'total_value': total_value,
        'income_annual': total_annual_income,
        'income_semiannual': total_annual_income / 2.0,
        'income_quarterly': total_annual_income / 4.0,
        'income_monthly': total_annual_income / 12.0,
    }
            

    
    return render(request, 'stocks/portfolio.html', context)

@require_POST
def add_to_portfolio(request):
    """
    Adds a stock to portfolio or updates its quantity by accumulating the value.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Você precisa estar logado.'}, status=403)
        
    try:
        data = json.loads(request.body)
        ticker = data.get('ticker', '').upper()
        # Parse as Decimal safely
        quantity_str = str(data.get('quantity', 0))
        quantity = Decimal(quantity_str)
    except (ValueError, json.JSONDecodeError, TypeError, Exception):
        return JsonResponse({'error': 'Dados inválidos.'}, status=400)
        
    if not ticker:
        return JsonResponse({'error': 'Ticker inválido.'}, status=400)
        
    info = get_stock_info(ticker)
    if not info['valid']:
        return JsonResponse({'error': 'Ação não encontrada.'}, status=404)
        
    if quantity == 0:
        return JsonResponse({'error': 'A quantidade deve ser diferente de zero.'}, status=400)
        
    portfolio_item, created = PortfolioItem.objects.get_or_create(
        user=request.user, 
        ticker=ticker,
        defaults={'name': info['name'], 'quantity': Decimal('0')}
    )
    
    # Accumulate the quantity instead of overwriting
    portfolio_item.quantity += quantity
    
    # If the user subtracted all shares (or more than they had), remove it entirely
    if portfolio_item.quantity <= 0:
        portfolio_item.delete()
        return JsonResponse({'status': 'success', 'message': 'Ativo removido da carteira.'})
        
    portfolio_item.save()
    
    action_verb = "adicionadas à" if quantity > 0 else "subtraídas da"
    return JsonResponse({'status': 'success', 'message': f'{int(abs(quantity))} cotas {action_verb} carteira.'})
