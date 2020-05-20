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
	'''
	Modelo básico da aplicação. É a única tabela criada para lidar com os dados,
	e é obrigatório preencher os dados de open, high, low e close - caso contrário,
	é um candlestick incompleto e inválido. Os campos volume_btc, volume_currency 
	e weighted_price foram criados para acomodar os dados da planilha original, 
	mas no fim das contas não foram utilizados para esse projeto.
	'''

	class Meta:
		# Garantindo que não haverá dados contraditórios relativos ao mesmo intervalo de tempo
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

	objects = CandlestickManager()		# filtro: candlesticks padrão inseridos (representam intervalos de tempo arbitrários)				
	daily = CandlestickDayManager()		# filtro: candlestick representando um dia inteiro

	def __repr__(self):
		return f'<Candlestick {self.datetime}>'
