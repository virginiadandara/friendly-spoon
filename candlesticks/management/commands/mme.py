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

	def _get_queryset(self, start, stop):
		self.qs = Candlestick.objects.filter(datetime__lte=stop, datetime__gte=start)
		self.qs = self.qs.order_by('-datetime__date', '-datetime').distinct('datetime__date')

	def _calculate(self, period):
		return self.qs.media_movel_exponencial(period)
