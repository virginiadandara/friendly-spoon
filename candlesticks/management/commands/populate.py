import re
from datetime import datetime

import pandas as pd
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from candlesticks.models import Candlestick

class Command(BaseCommand):
	'''
	Comando a ser usado para importar a planilha fornecida pelo kaggle para 
	o banco de dados. Uso (via terminal):
	$ python manage.py populate caminho/para/planilha.csv
	'''

	def add_arguments(self, parser):
		# Argumento único: CSV usado para popular o banco
		parser.add_argument('csv_file', type=str)

	def handle(self, *args, **options):
		'''
		Método principal do comando. Define a ordem de execução dos métodos 
		privados dessa classe. Não deve ser chamado através do código, mas sim
		pela linha de comando usando a interface do django.
		'''

		self._import_csv(options['csv_file'])
		self._drop_nan_rows()
		self._parse_column_names()
		self._parse_timestamp()
		self._batch_save()

	def _import_csv(self, path):
		'''
		Importa uma planilha de candlesticks passada pela linha de comando,
		usando a biblioteca pandas para fazê-lo. Escolhi a biblioteca pandas
		(no lugar da biblioteca-padrão csv do python) pela sua simplicidade e 
		eficiência para parsing de arquivos CSV com diversas formatações 
		arbitrárias distintas - em especial com datetime.
		'''

		self.stdout.write('Lendo CSV...')
		self.df = pd.read_csv(path)

	def _drop_nan_rows(self):
		'''
		Elimina linhas com pelo menos uma coluna nula. Pela análise que fiz do
		dataset, as linhas que continham pelo menos um dado nulo também 
		continham todos os outros dados nulos. De qualquer forma, para fins 
		desse código, considerei que um candlestick seria inválido caso uma 
		única coluna fosse nula, pois no meu entender o candlestick por si só
		já resume (e perde) muita informação sobre as oscilações de preços 
		usando apenas as 4 medidas de open, close, high e low; não possuindo 
		quaisquer dessas medidas, ele não parece ter informações suficientes 
		para ser analisado apropriadamente.
		'''

		self.stdout.write('Eliminando linhas nulas...')
		self.df.dropna(inplace=True)

	def _parse_column_names(self):
		'''
		Renomea as colunas para o padrão do banco (tudo minúscula, 
		apenas caracteres alfanuméricos e underline). Escolhi usar regex para 
		obter maior robustez em relação a nomenclaturas arbitrárias para as 
		colunas da planilha. Assim, tanto uma coluna 'Volume BTC' quanto uma 
		coluna 'Volume_(BTC)' seriam devidamente renomeadas de acordo com o 
		banco dessa aplicação, para 'volume_btc'.
		'''

		self.stdout.write('Renomeando colunas...')
		pat = re.compile(r'[^\w\d_]')	# regex para encontrar caracteres especiais
		rename_dict = {}
		for col in self.df.columns:
			new_name = col.lower().replace(' ', '_')
			new_name = pat.sub(repl='', string=new_name)
			rename_dict[col] = new_name
		self.df.rename(columns=rename_dict, inplace=True)

	def _parse_timestamp(self):
		'''
		Transformando o formato timestamp em formato datetime compatível com 
		o django
		'''

		self.stdout.write('Tratando timestamps...')
		self.df['datetime'] = self.df['timestamp'].apply(datetime.fromtimestamp)
		self.df.drop(columns=['timestamp'], inplace=True)

	@atomic
	def _batch_save(self):
		'''
		Salva a planilha inteira no banco, em uma única transação atômica.
		Escolhi esse decorador para evitar que um erro na transação produzisse
		uma inserção incompleta, o que complicaria uma nova tentativa de inserir
		dados no banco usando a mesma planilha pois geraria dados duplicados.
		'''

		self.stdout.write('Criando objetos...')
		batch = self.df.apply(self._build_model, axis=1).tolist()
		self.stdout.write('Salvando no banco...')
		Candlestick.objects.bulk_create(batch, batch_size=100_000)
		self.stdout.write(f'Sucesso!')

	def _build_model(self, row):
		'''
		Método chamado pelo _batch_save() para construir um único modelo de
		Candlestick a partir de uma linha (em formato dict-ish) do dataset.
		'''

		cs = Candlestick()
		for col, value in row.items():
			setattr(cs, col, value)
		return cs
