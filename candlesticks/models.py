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

	@classmethod
	def media_movel_exponencial(cls, period, queryset):
		'''
		Calcula a média móvel exponencial de um queryset dado. Todos os 
		candlesticks contidos no queryset são usados (e não apenas o do fim do 
		dia).

		Parâmetros
		----------
		period: int
			O período / tipo da média exponencial (MME 20, 50, 100, 200, etc.)
		queryset: iterable
			Objeto list-alike contento vários objetos do tipo Candlestick

		Retorno
		----------
		out: dict
			Dicionário com as médias móveis exponenciais no período da queryset.
		'''

		out = {}
		k = 2 / (1 + period)
		queryset = sorted(queryset, key=lambda cs: cs.datetime)
		cs = queryset[0]
		mme = cs.close
		out[cs.datetime] = mme
		for cs in queryset[1:]:
			mme += (cs.close - mme) * k
			out[cs.datetime] = mme
		return out
