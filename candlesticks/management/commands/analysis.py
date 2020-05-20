from pathlib import Path

from django.core.management.base import BaseCommand
import pandas as pd

from candlesticks.services import MediaMovelExponencial, IndiceForcaRelativa


class Command(BaseCommand):
	'''
	Este comando é simplesmente um wrapper dos serviços descritos em 
	candlesticks/services.py. Tudo que ele faz é receber informações da linha de
	comando, agrupar os índices em um dataframe do pandas, e exportá-lo como 
	CSV.
	'''

	def add_arguments(self, parser):
		parser.add_argument('date_start', type=pd.to_datetime, help='data de início (inclusive) no formato ISO (YYYY-MM-DD [HH:mm:ss[.ms]]')
		parser.add_argument('date_stop', type=pd.to_datetime, help='data de término (exclusive) no formato ISO (YYYY-MM-DD [HH:mm:ss[.ms]]')
		parser.add_argument('output', type=Path, help='caminho para a saída no formato CSV.')

	def handle(self, *args, **options):
		start, stop = options['date_start'], options['date_stop']
		cols = {}
		cols['MME20'] = MediaMovelExponencial(start, stop, 20).execute()
		cols['MME50'] = MediaMovelExponencial(start, stop, 50).execute()
		cols['MME100'] = MediaMovelExponencial(start, stop, 100).execute()
		cols['MME200'] = MediaMovelExponencial(start, stop, 200).execute()
		cols['IFR9'] = IndiceForcaRelativa(start, stop, 9).execute()
		cols['IFR14'] = IndiceForcaRelativa(start, stop, 14).execute()
		cols['IFR25'] = IndiceForcaRelativa(start, stop, 25).execute()
		pd.DataFrame(cols).to_csv(options['output'])
