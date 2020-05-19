from django.db import models

# Create your models here.
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
	class Meta:
		unique_together = ('datetime', 'type')

	REGULAR = 0
	DAY = 1
	TYPE_CHOICES = (
		(REGULAR, 'regular'),
		(DAY, 'day'),
	)

	datetime = models.DateTimeField(db_index=True)
	open = models.FloatField()
	high = models.FloatField()
	low = models.FloatField()
	close = models.FloatField()
	volume_btc = models.FloatField(null=True)
	volume_currency = models.FloatField(null=True)
	weighted_price = models.FloatField(null=True)
	type = models.IntegerField(choices=TYPE_CHOICES, default=REGULAR)

	objects = CandlestickManager()
	daily = CandlestickDayManager()						 # filtro: candlestick representando um dia inteiro

	def __repr__(self):
		return f'<Candlestick {self.datetime}>'
