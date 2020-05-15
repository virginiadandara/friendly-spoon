from functools import cached_property
from statistics import mean

from django.db import models

# Create your models here.
class CandlestickQuerySet(models.QuerySet):
	'''
	QuerySet customizado capaz de calcular índices especificos para
	um dado conjunto de candlesticks.
	'''
	def media_movel_exponencial(self, period):
		out = []
		k = 2 / (1 + period)
		queryset = self.order_by('datetime')
		values = list(map(lambda c: c.close, queryset))
		mme = mean(values[:period])
		out.append(mme)
		for close in values[period:]:
			mme += (close - mme) * k
			out.append(mme)
		return out

class CandlestickManager(models.Manager):
	def get_queryset(self):
		return CandlestickQuerySet(self.model, using=self._db)

class Candlestick(models.Model):
	datetime = models.DateTimeField(unique=True, db_index=True)
	open = models.FloatField()
	high = models.FloatField()
	low = models.FloatField()
	close = models.FloatField()
	volume_btc = models.FloatField()
	volume_currency = models.FloatField()
	weighted_price = models.FloatField()

	objects = CandlestickManager()

	def __repr__(self):
		return f'<Candlestick {self.datetime}>'
