import os
import certifi
import yfinance as yf
import pandas as pd
from curl_cffi.requests import Session as CurlSession

# Fix for SSL certificate issues (curl 77)
# Use curl_cffi Session directly and disable verification if needed
# Also add a realistic User-Agent to avoid rate limiting (429)
session = CurlSession(
    verify=False,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
)

def get_stock_info(ticker):
    """
    Fetch basic info for a given ticker. Handles .SA suffix automatically for Brazilian stocks.
    """
    ticker = ticker.upper().strip()
    
    # Try the original ticker first
    info = _fetch_from_yf(ticker)
    
    # If not found and it looks like a Brazilian ticker (e.g., 4 letters + numbers)
    # automatically try appending .SA
    if not info['valid'] and not ticker.endswith('.SA'):
        import re
        if re.match(r'^[A-Z]{4}[0-9]{1,2}$', ticker):
            info = _fetch_from_yf(f"{ticker}.SA")
            
    return info

def _fetch_from_yf(ticker):
    try:
        # Pass the curl_cffi session to yfinance
        stock = yf.Ticker(ticker, session=session)
        
        # Using fast_info or checking for regularMarketPrice as yf info can be slow/unreliable
        details = stock.info
        if not details or ('regularMarketPrice' not in details and 'currentPrice' not in details):
            return {'ticker': ticker, 'valid': False}
            
        parsed_info = {
            'ticker': ticker,
            'name': details.get('longName', details.get('shortName', ticker)),
            'price': details.get('currentPrice', details.get('regularMarketPrice')),
            'currency': details.get('currency', 'BRL' if ticker.endswith('.SA') else 'USD'),
            'change_pct': details.get('regularMarketChangePercent'),
            'valid': True
        }
        
        # Calculate Dividend Yield precisely for FIIs and unreliable YF Info
        # Always prioritize manual trailing 12m sum to fix FII bugs (e.g. MXRF11 showing 1200%)
        dy = None
        try:
            dividends = stock.dividends
            if not dividends.empty and parsed_info['price']:
                one_year_ago = pd.Timestamp.now(tz=dividends.index.tz) - pd.DateOffset(years=1)
                last_year_divs = dividends[dividends.index >= one_year_ago]
                total_last_year = last_year_divs.sum()
                if total_last_year > 0:
                    dy = total_last_year / parsed_info['price']
        except Exception as e:
            print(f"Fallback dividend error for {ticker}: {e}")
            pass
            
        if dy is None:
            dy = details.get('dividendYield', details.get('trailingAnnualDividendYield'))
            
        parsed_info['dividend_yield'] = dy or 0.0
        parsed_info['description'] = details.get('longBusinessSummary', details.get('description', ''))
        
        # Fundamental Indicators (Infomoney Style)
        def fmt_large(val, prefix=''):
            if val is None: return None
            try:
                val = float(val)
                if val >= 1_000_000_000: return f"{prefix}{val/1_000_000_000:.2f} B"
                if val >= 1_000_000: return f"{prefix}{val/1_000_000:.2f} M"
                return f"{prefix}{val:.2f}"
            except:
                return val

        parsed_info['pe_ratio'] = details.get('trailingPE', details.get('forwardPE'))
        parsed_info['price_to_book'] = details.get('priceToBook')
        parsed_info['eps'] = details.get('trailingEps') # LPA
        parsed_info['book_value'] = details.get('bookValue') # VPA
        parsed_info['market_cap'] = fmt_large(details.get('marketCap'), 'R$ ')
        parsed_info['fifty_two_week_high'] = details.get('fiftyTwoWeekHigh')
        parsed_info['fifty_two_week_low'] = details.get('fiftyTwoWeekLow')
        parsed_info['average_volume'] = fmt_large(details.get('averageVolume', details.get('regularMarketVolume')))
        parsed_info['sector'] = details.get('sector', 'N/A')
        parsed_info['industry'] = details.get('industry', 'N/A')

        return parsed_info
        
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return {'ticker': ticker, 'valid': False}

def get_historical_data(ticker, period='1mo', interval=None):
    """
    Fetch historical data for a given ticker. Handles .SA suffix automatically for Brazilian stocks.
    """
    ticker = ticker.upper().strip()
    
    # Se o intervalo não for fornecido, determinar baseado no período
    if not interval:
        if period in ['1d', '5d']:
            interval = '15m'
        elif period in ['1mo', '3mo']:
            interval = '1d'
        elif period in ['6mo', 'ytd', '1y']:
            interval = '1d'
        elif period in ['5y', 'max']:
            interval = '1wk'
        else:
            interval = '1d'
            
    # Try fetching as is
    data = _fetch_hist_from_yf(ticker, period, interval)
    
    # If failed and it looks like a B3 ticker, try with .SA
    if data is None and not ticker.endswith('.SA'):
        import re
        if re.match(r'^[A-Z]{4}[0-9]{1,2}$', ticker):
            data = _fetch_hist_from_yf(f"{ticker}.SA", period, interval)
    
    return data

def _fetch_hist_from_yf(ticker, period, interval):
    try:
        # Pass the curl_cffi session to yf.Ticker
        stock = yf.Ticker(ticker, session=session)
        df = stock.history(period=period, interval=interval)
        if df.empty:
            return None
        
        # Reset index to get Date as a column
        df = df.reset_index()
        # Convert Date to string for JSON serialization
        # Ensure 'Date' column exists (sometimes it's 'Datetime' for small intervals)
        date_col = 'Date' if 'Date' in df.columns else 'Datetime'
        df[date_col] = df[date_col].dt.strftime('%Y-%m-%d')
        
        return df[[date_col, 'Close']].rename(columns={date_col: 'Date'}).to_dict(orient='records')
    except Exception as e:
        print(f"Error fetching historical data for {ticker}: {e}")
        return None
