# import get_pic
# import bao_stock
import os
import random

class people(object):
	"""docstring for people"""
	def __init__(self, amount):

		self.amount = amount
		self.stock = 0
		self.keep_time = 0
		self.cost = 0
		self.sell_out_time = 0
		self.sell_out_price = 0

	def sell_out(self, price, date):
		if self.stock * price >= self.cost * 1.03:
			self.amount += (self.stock * price - 5)
			# print(str(date) + ':赚到钱了：%s, 余额：%s'%((self.stock * price - 5 - self.cost),self.amount))
			self.stock = 0
			self.keep_time = 0
			self.cost = 0
			self.sell_out_time += 1
			self.sell_out_price = price

		elif self.keep_time > 10:
			self.amount += (self.stock * price + 5)
			# print(str(date) + ':形式惨烈，损失：%s, 余额：%s'%((self.stock * price - 5 - self.cost), self.amount))
			self.stock = 0
			self.keep_time = 0
			self.cost = 0
			self.sell_out_time += 1
			self.sell_out_price = price


	def get_stock(self):
		return self.stock

	def buy_in(self, price, date):

		if (self.sell_out_time > 0 and self.sell_out_time < 4) or (price >= self.sell_out_price * 1.01 and self.sell_out_price != 0):
			self.sell_out_time += 1
			# print("休息%s天"%self.sell_out_time)
			return
		# if self.stock != 0 and price > self.cost / self.stock:
		# 	return
		# print(str(date)+'W余额：%s, 股票：%s，成本：%s，股价：%s, 总值：%s'%(self.amount, self.stock, self.cost, price, (self.amount + self.stock * price)))
		if self.stock == 0:
			self.amount -= (price * 100 + 5)
			self.stock += 100
			self.cost += (price * 100 + 5)
			self.sell_out_time = 0 
			# print(str(date)+'W余额：%s, 股票：%s，成本：%s，股价：%s, 总值：%s'%(self.amount, self.stock, self.cost, price, (self.amount + self.stock * price)))
			return
		if self.stock * price < self.cost * 1.03:
			# print("准备买股票啦！")
			if self.amount >= (price * (self.stock+100) + 5):

				self.amount -= (price * (self.stock+100) + 5)
				self.cost += (price * (self.stock+100) + 5)
				self.stock += (self.stock+100)
				self.sell_out_time = 0 
				# print(str(date)+'X余额：%s, 股票：%s，成本：%s，股价：%s, 总值：%s'%(self.amount, self.stock, self.cost, price, (self.amount + self.stock * price)))

			elif self.amount < (price * (self.stock+100) + 5):
				if self.amount < price*100+5:
					self.keep_time += 1
					self.sell_out_time = 0 
					return
				else:
					# print("适度购买")
					top = int(self.stock/100)
					for i in range(int(self.stock/100) + 1):
						i = top - i 
						if self.amount >= (i * 100 * price + 5):
							self.amount -= (i*100 * price + 5)
							self.cost += (i*100 * price + 5)
							self.stock += i*100
							self.sell_out_time = 0 
							# print(str(date)+'Y余额：%s, 股票：%s，成本：%s，股价：%s, 总值：%s'%(self.amount, self.stock, self.cost, price, (self.amount + self.stock * price)))
							return




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
	with open('stock-Change.txt', 'r', encoding='utf8') as filein:
		profile = []
		for line in filein.readlines()[:20]:
			data=line.strip().split()
			name = data[0]
			code = data[1]
			first = random.randint(200,2000) / 100
			changes = [float(x) for x in data[2:]]
			prices = [first]
			for i in changes:
				prices.append(round(prices[-1] * (100 + i + random.randint(0,3)/10) / 100,2))
			me = people(20000)
			zb = stock(first)

			count = 0
			for price in prices:
				count += 1
				zb.update_price(price)
				if me.get_stock() == 0:
					me.buy_in(price, count)
				else:
					me.sell_out(price, count)
					me.buy_in(price, count)

			if first < prices[-1]:
				print("股价上升⤴️ %s ---> %s , 余额变化 20000 --> %s" % (first, prices[-1], me.amount + me.stock * prices[-1]))
			else:
				print("股价下降⬇️ %s ---> %s , 余额变化 20000 --> %s" % (first, prices[-1], me.amount + me.stock * prices[-1]))

			profile.append((me.amount + me.stock * prices[-1]) - 20000)
		earn = 0
		lost = 0
		for i in profile:
			if i > 0:
				earn += 1
			else:
				lost += 1
		print(str(earn) + " - " + str(lost))
		print("最终得利:%s"%sum(profile))

		# print(changes)
		# print(prices)
    # bao_stock.processData()
    # bao_stock.splitData()

if __name__ == '__main__':
	# main()
	# os.system('python3 Mysql.py')
	# os.system('python3 Neo4j.py')
	# os.system('python3 Strategy.py')
	os.system('python3 Operation.py')