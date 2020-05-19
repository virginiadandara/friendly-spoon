from django.db import models

# Create your models here.
class CandlestickStartOfTheDayManager(models.Manager):
	'''
	Manager que retorna a primeira instância de candlestick de cada dia, útil para o cálculo
	de índices como o IFR, por exemplo.
	'''

	def get_queryset(self):
		return super().get_queryset()\
			.order_by('+datetime__date', '+datetime').distinct('datetime__date')\
			.filter(type=Candlestick.REGULAR)

class CandlestickEndOfTheDayManager(models.Manager):
	'''
	Manager que retorna a última instância de candlestick de cada dia, útil para o cálculo
	de índices como a MME, por exemplo.
	'''

	def get_queryset(self):
		return super().get_queryset()\
			.order_by('-datetime__date', '-datetime').distinct('datetime__date')\
			.filter(type=Candlestick.REGULAR)

class CandlestickManager(models.Manager):
	'''
	Manager que retorna candlesticks não-diários
	'''
	def get_queryset(self):
		return super().get_queryset().filter(type=Candlestick.REGULAR)

class CandlestickDayManager(models.Manager):
	'''
	Manager que retorna apenas candlesticks do tipo diário
	'''
	def get_queryset(self):
		return super().get_queryset().filter(type=Candlestick.DAY)

class Candlestick(models.Model):
	REGULAR = 0
	DAY = 1
	TYPE_CHOICES = (
		(REGULAR, 'regular'),
		(DAY, 'day'),
	)

	datetime = models.DateTimeField(unique=True, db_index=True)
	open = models.FloatField()
	high = models.FloatField()
	low = models.FloatField()
	close = models.FloatField()
	volume_btc = models.FloatField()
	volume_currency = models.FloatField()
	weighted_price = models.FloatField()
	type = models.IntegerField(choices=TYPE_CHOICES, default=REGULAR)

	objects = CandlestickManager()
	daily = CandlestickDayManager()						 # filtro: candlestick representando um dia inteiro
	end_of_the_day = CandlestickEndOfTheDayManager()	 # filtro: último candlestick de cada dia
	start_of_the_day = CandlestickStartOfTheDayManager() # filtro: primeiro candlestick de cada dia

	def __repr__(self):
		return f'<Candlestick {self.datetime}>'
