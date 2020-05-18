from django.db import models

# Create your models here.
class ClandlestickEndOfTheDayManager(models.Manager):
	'''
	Manager que retorna a última instância de candlestick de cada dia
	'''

	def get_queryset(self):
		return super().get_queryset().order_by('-datetime__date', '-datetime').distinct('datetime__date')

class Candlestick(models.Model):
	datetime = models.DateTimeField(unique=True, db_index=True)
	open = models.FloatField()
	high = models.FloatField()
	low = models.FloatField()
	close = models.FloatField()
	volume_btc = models.FloatField()
	volume_currency = models.FloatField()
	weighted_price = models.FloatField()

	objects = models.Manager()
	end_of_the_day = ClandlestickEndOfTheDayManager()

	def __repr__(self):
		return f'<Candlestick {self.datetime}>'
