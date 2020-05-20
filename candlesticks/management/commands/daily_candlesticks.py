from functools import cached_property

from django.core.management.base import BaseCommand
from django.db.models import Max, Min
from django.db.transaction import atomic

from candlesticks.models import Candlestick


class Command(BaseCommand):
	'''
	Comando para calcular abertura, fechamento, máx e mín diário e salvar o 
	resumo diário no banco. Deve ser executado sempre depois de popular o banco.

	Uso:
	$ python manage.py daily_candlesticks
	'''

	@atomic
	def handle(self, *args, **options):
		candlesticks = []
		for i in range(len(self.open)):
			cs = Candlestick(type=Candlestick.DAY)
			cs.open = self.open[i].open
			cs.close = self.close[i].close
			cs.high = self.high[i]['high__max']
			cs.low = self.low[i]['low__min']
			cs.datetime = self.open[i].datetime.date()
			candlesticks.append(cs)
		Candlestick.objects.bulk_create(candlesticks)

	@cached_property
	def open(self):
		'''
		Retorna os valores de abertura do primeiro Candlestick de cada dia,
		no formato de uma lista de dicionários. Não consegui executar essa query
		da forma ideal, usando a API de QuerySet do django, por falta de 
		conhecimento sobre as funções de agregação. Optei por usar o distinct on
		no lugar delas. Tenho mais familiaridade com SQL puro do que com queries 
		no Django, mas dado mais tempo teria buscado um código mais apropriado
		que evitasse recorrer a esta query pura.
		'''

		return list(Candlestick.objects.raw('''
			SELECT DISTINCT ON (DATE("datetime")) id, open
			FROM candlesticks_candlestick
			WHERE type = 0
			ORDER BY DATE("datetime"), "datetime" ASC;
		'''))

	@cached_property
	def close(self):
		'''
		Retorna os valores de fechamento do último Candlestick de cada dia,
		no formato de uma lista de dicionários. Comentário idem ao do
		método open().
		'''

		return list(Candlestick.objects.raw('''
			SELECT DISTINCT ON (DATE("datetime")) id, close
			FROM candlesticks_candlestick
			WHERE type = 0
			ORDER BY DATE("datetime"), "datetime" DESC;
		'''))

	@cached_property
	def high(self):
		'''Retorna o valor máximo de cada dia, no formato de lista de objetos Candlestick.'''
		return list(Candlestick.objects.values('datetime__date').annotate(Max('high')).order_by('datetime__date'))

	@cached_property
	def low(self):
		'''Retorna o valor mínimo de cada dia, no formato de lista de objetos Candlestick.'''
		return list(Candlestick.objects.values('datetime__date').annotate(Min('low')).order_by('datetime__date'))
