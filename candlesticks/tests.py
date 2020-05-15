from datetime import datetime, timedelta

from django.test import TestCase

from .models import Candlestick
from .factories import CandlestickFactory

# Create your tests here.
class CandlestickTests(TestCase):
	def test_media_movel_exponencial_50(self):
		candlesticks = CandlestickFactory.create_batch(1000)
		Candlestick.objects.bulk_create(candlesticks)
		stop = datetime.now()
		start = stop - timedelta(days=1)
		qs = Candlestick.objects.filter(datetime__lte=stop, datetime__gte=start)
		result = qs.media_movel_exponencial(50)
		self.assertEqual(result[-1], 974.5)
