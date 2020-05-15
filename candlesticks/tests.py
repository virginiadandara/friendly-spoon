from datetime import datetime, timedelta

from django.test import TestCase

from .models import Candlestick
from .factories import CandlestickFactory

# Create your tests here.
class CandlestickTests(TestCase):
	def test_media_movel_exponencial_20(self):
		candlesticks = []
		stop = datetime.now()
		start = stop - timedelta(days=100)
		candlesticks.append(CandlestickFactory.build(datetime=stop))
		for i in range(1, 100):
			cs = CandlestickFactory.build(datetime=start + timedelta(days=i))
			candlesticks.append(cs)
		Candlestick.objects.bulk_create(candlesticks)
		qs = Candlestick.end_of_the_day.filter(datetime__gte=start, datetime__lte=stop)
		result = Candlestick.media_movel_exponencial(20, qs)
		self.assertEqual(round(result[stop], 3), 80.977)
