import re
from datetime import datetime

import pandas as pd
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from candlesticks.models import Candlestick

class Command(BaseCommand):
	'''
	Comando a ser usado para importar a planilha fornecida pelo kaggle para 
	o banco de dados. Uso:
	$ python manage.py populate caminho/para/planila.csv
	'''

	def handle(self, *args, **options):
		self.import_csv(options['csv_file'])
		self.drop_nan_rows()
		self.parse_column_names()
		self.parse_timestamp()
		self.batch_save()

	def import_csv(self, path):
		self.stdout.write('Lendo CSV...')
		self.df = pd.read_csv(path)

	def add_arguments(self, parser):
		# Argumento único: CSV usado para popular o banco
		parser.add_argument('csv_file', type=str)

	@atomic
	def batch_save(self):
		self.stdout.write('Criando objetos...')
		batch = self.df.apply(self.build_model, axis=1).tolist()
		self.stdout.write('Salvando no banco...')
		Candlestick.objects.bulk_create(batch)
		self.stdout.write(f'Sucesso!')

	def build_model(self, row):
		cs = Candlestick()
		for col, value in row.items():
			setattr(cs, col, value)
		return cs

	def drop_nan_rows(self):
		self.stdout.write('Eliminando linhas nulas...')
		self.df.dropna(inplace=True)

	def parse_column_names(self):
		'''
		Renomea as colunas para o padrão do banco (tudo minústula, 
		apenas caracteres alfanuméricos e underline)
		'''
		self.stdout.write('Renomeando colunas...')
		pat = re.compile(r'[^\w\d_]')	# regex para encontrar caracteres especiais
		rename_dict = {}
		for col in self.df.columns:
			new_name = col.lower()
			new_name = pat.sub(repl='', string=new_name)
			rename_dict[col] = new_name
		self.df.rename(columns=rename_dict, inplace=True)

	def parse_timestamp(self):
		self.stdout.write('Tratando timestamps...')
		self.df['datetime'] = self.df['timestamp'].apply(datetime.fromtimestamp)
		self.df.drop(columns=['timestamp'], inplace=True)

