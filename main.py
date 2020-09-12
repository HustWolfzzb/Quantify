# import get_pic
# import bao_stock
import os
import random


class stock(object):
		"""docstring for stock"""
		def __init__(self, first):
			self.price = first
			self.name = '中百'
			self.code = '002292'

		def get_price(self):
			return self.price

		def update_price(self,p):
			self.price = p


def main():
	pass

if __name__ == '__main__':
	# main()
	# os.system('python3 Mysql.py')
	# os.system('python3 Neo4j.py')
	os.system('python3 Strategy.py')
	# os.system('python3 Operation.py')
	# os.system('python3 Data.py')
	# os.system('python3 HaiTong.py')


