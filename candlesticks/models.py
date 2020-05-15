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
		'''
		Calcula a média móvel exponencial do queryset. Todos os candlesticks 
		contidos no queryset são usados (e não apenas o do fim do dia).

		Parâmetros
		----------
		period: int
			O período / tipo da média exponencial (MME 20, 50, 100, 200, etc.)

		Retorno
		----------
		out: list
			Lista com as médias móveis exponenciais no período da queryset.
		'''
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
	'''
	Model Manager que retorna uma Queryset do tipo CandlestickQuerySet,
	capaz de calcular índices como a média móvel exponencial.
	'''

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
