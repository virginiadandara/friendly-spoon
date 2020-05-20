from statistics import mean
from datetime import timedelta
from functools import cached_property

import pandas as pd
from django.db.models import F

from candlesticks.models import Candlestick

class MediaMovelExponencial:
	'''
	Calcula a média móvel exponencial de um período dado. Apenas os valores de 
	fechamento de cada DIA são usados.

	Uso:
	result = MediaMovelExponencial(20, '2018-01-01', '2018-04-01').execute()

	Retorna um pandas.Series ordenado por data.
	'''

	def __init__(self, start, stop, period=20):
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
		Método principal (público) que ordena as operações realizadas para c
		alcular a MME.

		Retorno
		----------
		out: pandas.Series
		Série com valores da MME para o período solicitado, ordenado pela data.
		'''

		self._calculate()
		return pd.Series(self.result).sort_index()

	@cached_property
	def base_mme(self):
		return mean(map(lambda c: c.close, self.qs[:self.period]))

	@cached_property
	def qs(self):
		return Candlestick.daily.filter(datetime__gte=self.start, datetime__lt=self.stop)\
			.order_by('datetime')

	def _calculate(self):
		out = {}
		k = 2 / (1 + self.period)
		mme = self.base_mme
		for cs in self.qs[self.period:]:
			mme += (cs.close - mme) * k
			out[cs.datetime.date()] = mme
		self.result = out


class IndiceForcaRelativa:
	def __init__(self, date_start, date_stop, period=14):
		self.start = pd.to_datetime(date_start)
		self.stop = pd.to_datetime(date_stop)
		self.period = period
		self.limit = period + (self.stop - self.start).days + 1

	def execute(self):
		out = {}
		for i in range(len(self.positive) - self.period):
			curr = self.positive[i] 	# candlestick atual
			if curr['datetime'] < self.start: break
			pos_data = [cs['close'] for cs in self.positive[i:i+self.period]]
			neg_data = [cs['close'] for cs in self.negative[i:i+self.period]]
			U = mean(pos_data)
			D = mean(neg_data)
			out[curr['datetime'].date()] = 100 - 100 / (1 + U / D)
		return pd.Series(out)

	@cached_property
	def fields(self):
		# campos extraídos da tabela candlestick
		return ['datetime', 'close']

	@cached_property
	def diff(self):
		# campo que representa a diferença entre o valor na abertura e o valor no fechamento
		return F('close') - F('open')

	@cached_property
	def negative(self):
		# candlesticks diários que tiveram queda de preço
		return Candlestick.daily.values(*self.fields, diff=self.diff)\
			.filter(diff__lt=0, datetime__lt=self.stop)\
			.order_by('-datetime')[:self.limit]

	@cached_property
	def positive(self):
		# candlesticks diários que tiveram aumento de preço
		return Candlestick.daily.values(*self.fields, diff=self.diff)\
			.filter(diff__gt=0, datetime__lt=self.stop)\
			.order_by('-datetime')[:self.limit]
