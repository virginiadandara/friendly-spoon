from statistics import mean, StatisticsError
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
	result = MediaMovelExponencial('2018-01-01', '2018-04-01', 20).execute()

	Retorna um pandas.Series ordenado por data, começando em 2018-01-01 e 
	terminando em 2018-03-31 (o último dia da data é exclusivo).
	'''

	def __init__(self, start, stop, period=20):
		'''
		Parâmetros
		----------
		start: str, datetime
			Objeto que possa ser interpretado como date / datetime indicando a data de início (inclusive)
		stop: str, datetime
			Objeto que possa ser interpretado como date / datetime, indicando a data de fim (exclusive)
		period: int = 20
			O período em dias  da média exponencial (MME 20, 50, 100, 200, etc.)
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

		out = {}
		k = 2 / (1 + self.period)
		mme = self.base_mme
		for cs in self.qs[self.period:]:
			mme += (cs.close - mme) * k
			out[cs.datetime.date()] = mme
		return pd.Series(out).sort_index()

	@cached_property
	def base_mme(self):
		'''Retorna a média dos valores de fechamentos dos primeiros [period] dias.'''
		return mean(map(lambda c: c.close, self.qs[:self.period]))

	@cached_property
	def qs(self):
		'''Retorna o queryset que será usado para calcular os valores da média 
		móvel exponencial.'''
		return Candlestick.daily.filter(datetime__gte=self.start, datetime__lt=self.stop)\
			.order_by('datetime')


class IndiceForcaRelativa:
	'''
	Calcula o índice de força relativa de um período dado. Apenas os valores de 
	abertura e de fechamento de cada DIA são usados.

	Uso:
	result = IndiceForcaRelativa('2018-01-01', '2018-04-01', 14).execute()

	Retorna um pandas.Series ordenado por data, começando em 2018-01-01 e 
	terminando em 2018-03-31 (o último dia da data é exclusivo).
	'''
	def __init__(self, date_start, date_stop, period=14):
		'''
		Parâmetros
		----------
		date_start: str, datetime
			Objeto que possa ser interpretado como date / datetime indicando a data de início (inclusive)
		date_stop: str, datetime
			Objeto que possa ser interpretado como date / datetime, indicando a data de fim (exclusive)
		period: int = 14
			O período em dias do índice de força relativa (9, 14, 25, etc. são valores comuns)
		'''
		self.start = pd.to_datetime(date_start)
		self.stop = pd.to_datetime(date_stop)
		self.period = period
		self.limit = period + (self.stop - self.start).days + 1

	def execute(self):
		'''
		Método principal (público) que ordena as operações realizadas para c
		alcular a MME.

		Retorno
		----------
		out: pandas.Series
			Série com valores da MME para o período solicitado, ordenado pela data.
		'''

		out = {}
		all_ = sorted(self.positive + self.negative, key=lambda cs: cs['datetime'], reverse=True)
		for current_candlestick in all_:
			if current_candlestick['datetime'] < self.start: break
			pos_data = [cs['close'] for cs in self.positive if cs['datetime'] < current_candlestick['datetime']][:self.period]
			neg_data = [cs['close'] for cs in self.negative if cs['datetime'] < current_candlestick['datetime']][:self.period]
			try:
				U = mean(pos_data)
				D = mean(neg_data)
			except StatisticsError:
				# pos_data ou neg_data são vazios; não calcular nem armazenar o IFR para essa data.
				continue
			out[current_candlestick['datetime'].date()] = 100 - 100 / (1 + U / D)
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
		return list(Candlestick.daily.values(*self.fields, diff=self.diff)\
			.filter(diff__lt=0, datetime__lt=self.stop)\
			.order_by('-datetime')[:self.limit])

	@cached_property
	def positive(self):
		# candlesticks diários que tiveram aumento de preço
		return list(Candlestick.daily.values(*self.fields, diff=self.diff)\
			.filter(diff__gt=0, datetime__lt=self.stop)\
			.order_by('-datetime')[:self.limit])
