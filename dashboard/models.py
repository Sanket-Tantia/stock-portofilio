from django.db import models

# Create your models here.
class Stock(models.Model):
    ticker = models.CharField(primary_key=True, max_length=255)
    isin_code = models.CharField(max_length=255, null=False, unique=True)
    company_name = models.CharField(max_length=255, null=False)
    details = models.TextField(blank=True)
    exchange = models.CharField(max_length=255, null=False)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_related_name = 'stock'

    def __str__(self):
        return self.name


class Trade(models.Model):
    stock_id = models.ForeignKey(Stock, on_delete=models.DO_NOTHING)
    price = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=4)
    is_buy = models.BooleanField(default=False)
    txn_date = models.DateField(null=False, blank=False)
    shares = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=4)

    class Meta:
        default_related_name = 'trade'

    def __str__(self):
        return self.name


class SharesInfo(models.Model):
    stock_id = models.OneToOneField(Stock, primary_key=True, on_delete=models.DO_NOTHING)
    total_shares = models.DecimalField(null=False, default=0, max_digits=10, decimal_places=4)
    avg_price = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=4)

    class Meta:
        default_related_name = 'sharesInfo'

    def __str__(self):
        return self.name