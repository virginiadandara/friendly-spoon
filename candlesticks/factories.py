from datetime import datetime

import factory

from .models import Candlestick


class CandlestickFactory(factory.Factory):
	class Meta:
		model = Candlestick

	datetime = factory.LazyFunction(datetime.now)
	open = factory.Sequence(lambda x: x)
	high = factory.Sequence(lambda x: x)
	low = factory.Sequence(lambda x: x)
	close = factory.Sequence(lambda x: x)
	volume_btc = factory.Sequence(lambda x: x)
	volume_currency = factory.Sequence(lambda x: x)
	weighted_price = factory.Sequence(lambda x: x)
