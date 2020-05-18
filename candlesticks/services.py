import pandas as pd

from candlesticks.models import Candlestick

class MediaMovelExponencial:
	def __init__(self, period, start, stop):
		self.period = period
		self.start = start
		self.stop = stop

	def execute(self):
		self._get_queryset()
		self._calculate()
		return pd.Series(self.result)

	def _get_queryset(self):
		self.qs = Candlestick.end_of_the_day.filter(datetime__gte=self.start, datetime__lt=self.stop)

	def _calculate(self):
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
		k = 2 / (1 + self.period)
		queryset = sorted(self.qs, key=lambda cs: cs.datetime)
		cs = queryset[0]
		mme = cs.close
		out[cs.datetime] = mme
		for cs in queryset[1:]:
			mme += (cs.close - mme) * k
			out[cs.datetime] = mme
		self.result = out
		
