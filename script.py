#! /usr/bin/python3

from argparse import ArgumentParser

import pandas as pd


if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument('start_date', type=str)
	parser.add_argument('end_date', type=str)
	args = parser.parse_args()

	df = pd.read_csv('db/bitstampUSD_1-min_data_2012-01-01_to_2020-04-22.csv')
	print(df.columns)
