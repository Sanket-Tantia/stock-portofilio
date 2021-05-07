from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.http import HttpResponse
from django import template
# import yfinance as yf
from datetime import datetime, timedelta
import pytz
import decimal

from django.contrib import messages

# redirect after form submit
from django.http import HttpResponseRedirect

# query functions
from django.db.models import Count, Q, Sum

from .forms import AddStockForm, RecordTradeForm, SharesInfoForm

from .models import Stock, Trade, SharesInfo

from .stock_manager import NSE

# def format_datetime(datetime_obj, date_format="%Y-%m-%d") -> str:
#     if type(datetime_obj).__name__ == 'datetime':
#         return datetime_obj.strftime(date_format)
#     raise ValueError("Value provided must be datetime")

# def get_current_trading_day(last_trading_day_of_week=4) -> datetime:
#     current_dayofweek = datetime.now().weekday()
#     if current_dayofweek <= last_trading_day_of_week:
#         return now
#     else:
#         last_trading_day = datetime.now() - timedelta(current_dayofweek -
#                                                       last_trading_day_of_week)
#         return last_trading_day

# def format_yfinance_data(ticker_day_data):
#     if not ticker_day_data.empty:
#         return ticker_day_data.to_dict(orient='records')[0]

# def get_stock_daily_data(ticker_symbol: str, start_date: str, end_date: str):
#     ticker_obj = yf.Ticker(ticker_symbol)
#     # print(ticker_obj)
#     # print(start_date, end_date)
#     ticker_day_data = ticker_obj.history(
#         start=start_date, end=end_date, interval="1d")
#     return format_yfinance_data(ticker_day_data)

# def get_stock_info(ticker_symbol):
    # ticker_obj = yf.Ticker(ticker_symbol)
    # stock_info = ticker_obj.info
    # # print(stock_info, type(stock_info))
    # if stock_info.__contains__('symbol'):
    #     stock_info['isin'] = '' if ticker_obj.get_isin() == '-' else ticker_obj.get_isin()
    #     return stock_info
    # else:
    #     return {}

@login_required(login_url="/login/")
def home(request):
    context = {}
    context['active_stocks'] = Stock.objects.filter(is_active=1).count()
    all_stocks = []
    # print(list(Stock.objects.filter(is_active=1).select_related('sharesInfo').all()))
    for each_stock in Stock.objects.filter(is_active=1).select_related('sharesInfo').all():
        stock_data = {}
        ticker_symbol = each_stock.ticker
        print(ticker_symbol)
        daily_data = NSE.get_stock_daily_price(ticker_symbol)
        # existing shares info
        total_shares = each_stock.sharesInfo.total_shares
        avg_price = each_stock.sharesInfo.avg_price
        # my closing price
        current_price = daily_data['lastPrice']
        # print(total_shares, avg_price, current_price)
        if total_shares:
            existing_investment = decimal.Decimal(avg_price)*decimal.Decimal(total_shares)
            current_investment = decimal.Decimal(current_price)*decimal.Decimal(total_shares)
            PL = current_investment-existing_investment
            if existing_investment <= 0:
                 PL_perc = 'infinite'
            else:
                PL_perc = ((current_investment-existing_investment)/existing_investment)*100
        else:
            PL = 0
            PL_perc = 0
        stock_data.update(daily_data)
        stock_data['ticker'] = ticker_symbol
        stock_data['total_shares'] = total_shares
        stock_data['PL'] = PL
        stock_data['PL_perc'] = PL_perc
        all_stocks.append(stock_data)
    context['all_stocks'] = all_stocks

    recent_trades = []
    queryset = Trade.objects.filter(txn_date__gte=datetime.now(pytz.timezone('Asia/Kolkata'))-timedelta(days=7))
    for each_trade in queryset:
        recent_trades.append({
            'price': each_trade.price,
            'is_buy': 'Bought' if each_trade.is_buy else 'Sold',
            'txn_date': each_trade.txn_date,
            'stock_name': each_trade.stock_id.company_name,
            'shares': each_trade.shares
        })
    context['recent_trades'] = recent_trades

    html_template = loader.get_template('deskapp/dashboard.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def add_stock(request):
    context = {}
    context["is_ticker_invalid"] = "None"
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        context['ticker'] = ticker
        if ticker:
            stock_info = NSE.get_stock_info(ticker)
            if not stock_info:
                context["is_ticker_invalid"] = "True"
            else:
                # context['ticker'] = stock_info.get('symbol', '')
                # context["is_ticker_invalid"] = "False"
                # context["isin_code"] = stock_info.get('isinCode', '')
                # context["company_name"] = stock_info.get('companyName', '')
                # context["exchange"] = stock_info.get('exchange', '')
                # context["series"] = stock_info.get('series', '')

                add_stock_form = AddStockForm(
                    {
                    'ticker': stock_info.get('symbol', ''),
                    "isin_code":stock_info.get('isinCode', ''),
                    "company_name":stock_info.get('companyName', ''),
                    "exchange":stock_info.get('exchange', ''),
                    "details":stock_info.get('details', 'Yooo'),
                })
                
                if add_stock_form.is_valid():
                    add_stock_form.save()
                    print(add_stock_form.cleaned_data.get('ticker'))
                    shares_info_form = SharesInfoForm({
                        'stock_id': add_stock_form.cleaned_data.get('ticker'),
                        'total_shares': 0,
                        'avg_price': 0
                    })
                    # print(shares_info_form)
                    if shares_info_form.is_valid():
                        # print(shares_info_form.cleaned_data.get('stock_id'))
                        shares_info_form.save()
                        return redirect('home')
                    else:
                        print("Shares info form not valid", shares_info_form.errors)
                else:
                    print("Stock form not valid", add_stock_form.errors)

    context['all_stock_codes'] = NSE.get_all_stock_codes()
    return render(request, "deskapp/add_stock.html", context)

@login_required(login_url="/login/")
def record_trade(request):
    context = {}
    if request.method == 'POST':
        post_body = request.POST.copy()
        post_body['is_buy'] = False if post_body['is_buy'] == '0' else True
        
        record_trade_form = RecordTradeForm(post_body or None)
        
        if record_trade_form.is_valid():
            stock_id = record_trade_form.cleaned_data.get('stock_id')
            is_buy = record_trade_form.cleaned_data.get('is_buy')
            trade_shares = decimal.Decimal(record_trade_form.cleaned_data.get('shares'))
            trade_price = decimal.Decimal(record_trade_form.cleaned_data.get('price'))
            try:
                shares_info_obj = SharesInfo.objects.get(pk=stock_id)
                if is_buy:
                    existing_investment = shares_info_obj.total_shares * shares_info_obj.avg_price
                    new_investment = existing_investment + trade_shares*trade_price
                    shares_info_obj.total_shares += trade_shares
                    shares_info_obj.avg_price = new_investment/shares_info_obj.total_shares
                    shares_info_obj.save()
                    record_trade_form.save()
                    return redirect('home')
                else:
                    if shares_info_obj.total_shares < trade_shares:
                        print("No enough shares to make this trade")
                    else:
                        existing_investment = shares_info_obj.total_shares * shares_info_obj.avg_price
                        new_investment = existing_investment - trade_shares*trade_price
                        shares_info_obj.total_shares -= trade_shares
                        shares_info_obj.avg_price = new_investment/shares_info_obj.total_shares
                        if shares_info_obj.avg_price<0:
                            shares_info_obj.avg_price = 0
                        shares_info_obj.save()
                        record_trade_form.save()
                        return redirect('home')
            except SharesInfo.DoesNotExist:
                print("stock not added properly, share info does not exist")
        else:
            print("Record form not valid", record_trade_form.errors)
        

    all_stocks = [{
        'stock_name':i.company_name,
        'stock_code': i.ticker
    } for i in Stock.objects.all()]
    
    context['all_stocks'] = all_stocks


    return render(request, "deskapp/transaction.html", context)
