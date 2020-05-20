from functools import cached_property

from django.core.management.base import BaseCommand
from django.db.models import Max, Min
from django.db.transaction import atomic

from candlesticks.models import Candlestick


class Command(BaseCommand):
	'''
	Comando para calcular abertura, fechamento, máx e mín diário.
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
		return Candlestick.objects.raw('''
			SELECT DISTINCT ON (DATE("datetime")) id, open
			FROM candlesticks_candlestick
			WHERE type = 0
			ORDER BY DATE("datetime"), "datetime" ASC;
		''')

	@cached_property
	def close(self):
		return Candlestick.objects.raw('''
			SELECT DISTINCT ON (DATE("datetime")) id, close
			FROM candlesticks_candlestick
			WHERE type = 0
			ORDER BY DATE("datetime"), "datetime" DESC;
		''')

	@cached_property
	def high(self):
		return Candlestick.objects.values('datetime__date').annotate(Max('high')).order_by('datetime__date')

	@cached_property
	def low(self):
		return Candlestick.objects.values('datetime__date').annotate(Min('low')).order_by('datetime__date')
