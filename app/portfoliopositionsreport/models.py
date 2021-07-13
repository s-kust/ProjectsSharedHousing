from django.db import models

ROW_TYPE_CHOICES = [("Stocks_ETFs", "Stocks or ETFs"), ("Forex", "Forex")]

class Portfolio(models.Model):
    last_update_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        Portfolio.objects.all().delete()
        # self.pk = self.id = 1
        return super().save(*args, **kwargs)

class PortfolioRow(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker_1 = models.CharField(max_length=8)
    ticker_2 = models.CharField(max_length=8)
    row_type = models.CharField(
        max_length=12,
        choices=ROW_TYPE_CHOICES,
        default="Stocks_ETFs",
    )
    note = models.CharField(max_length=100)
    file_1 = models.ImageField(upload_to='media', null=True)
    file_2 = models.ImageField(upload_to='media', null=True)

    def __str__(self):
        return '%s - %s - %s - %s - %s - %s' % (self.ticker_1, self.ticker_2,\
            self.row_type, self.note, self.file_1, self.file_2)
    