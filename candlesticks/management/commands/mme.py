from django.core.management.base import BaseCommand

from candlesticks.models import Candlestick

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('period', type=int)
		parser.add_argument('start_date', type=str)
		parser.add_argument('stop_date', type=str)

	def handle(self, *args, **options):
		self._get_queryset(options['start_date'], options['stop_date'])
		self._calculate(options['period'])
		self._print_values()

	def _get_queryset(self, start, stop):
		self.qs = Candlestick.end_of_the_day.filter(datetime__lte=stop, datetime__gte=start)

	def _calculate(self, period):
		self.result = Candlestick.media_movel_exponencial(period, self.qs)

	def _print_values(self):
		for datetime, mme in self.result.items():
			print(datetime, mme, sep=',')
