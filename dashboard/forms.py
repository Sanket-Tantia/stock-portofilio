from django import forms
from .models import (
    Stock,
    Trade,
    SharesInfo
)

class AddStockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['ticker', 'isin_code', 'company_name', 'details', 'exchange']


class RecordTradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ['txn_date', 'stock_id', 'price', 'is_buy', 'shares']


class SharesInfoForm(forms.ModelForm):
    class Meta:
        model = SharesInfo
        fields = ['total_shares', 'stock_id', 'avg_price']