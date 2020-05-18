from statistics import mean
from datetime import timedelta

import pandas as pd

from candlesticks.models import Candlestick

class MediaMovelExponencial:
	'''
	Calcula a média móvel exponencial de um período dado. Apenas os valores de 
	fechamento de cada DIA são usados.

	Uso:
	result = MediaMovelExponencial(20, '2018-01-01', '2018-04-01').execute()

	Retorna um pandas.Series ordenado por data.
	'''

	def __init__(self, period, start, stop):
		'''
		Parâmetros
		----------
		period: int
			O período / tipo da média exponencial (MME 20, 50, 100, 200, etc.)
		start: str, datetime
			Objeto que possa ser interpretado como date / datetime indicando a data de início (inclusive)
		stop: str, datetime
			Objeto que possa ser interpretado como date / datetime, indicando a data de fim (exclusive)
		'''

		self.period = period
		self.start = pd.to_datetime(start) - timedelta(days=self.period)
		self.stop = pd.to_datetime(stop)

	def execute(self):
		'''
		Método principal (público) que ordena as operações realizadas para calcular a MME.

		Retorno
		----------
		out: pandas.Series
		Série com valores da MME para o período solicitado, ordenado pela data.
		'''

		self._get_queryset()
		self._get_base_value()
		self._calculate()
		return pd.Series(self.result).sort_index()

	def _get_base_value(self):
		self.base_mme = mean(map(lambda c: c.close, self.qs[:self.period]))

	def _get_queryset(self):
		self.qs = Candlestick.end_of_the_day.filter(datetime__gte=self.start, datetime__lt=self.stop)
		self.qs = sorted(self.qs, key=lambda cs: cs.datetime)

	def _calculate(self):
		out = {}
		k = 2 / (1 + self.period)
		mme = self.base_mme
		for cs in self.qs[self.period:]:
			mme += (cs.close - mme) * k
			out[cs.datetime.date()] = mme
		self.result = out
