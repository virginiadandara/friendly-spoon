from django.db import models

# Create your models here.
class Candlestick(models.Model):
	datetime = models.DateTimeField(unique=True, db_index=True)
	open = models.FloatField()
	high = models.FloatField()
	low = models.FloatField()
	close = models.FloatField()
	volume_btc = models.FloatField()
	volume_currency = models.FloatField()
	weighted_price = models.FloatField()

	def __repr__(self):
		return f'<Candlestick {self.timestamp}>'
