import datetime
from dateutil.parser import parse
import os.path


#Constant variables
CUSTOMER_KEY = 'CUSTOMER'
SITE_KEY = 'SITE_VISIT'
IMAGE_KEY = 'IMAGE'
ORDER_KEY = 'ORDER'
DATE_KEY = 'event_time'
INPUT_FILE = '../input/input.txt'
OUTPUT_FILE = '../output/output.txt'
LIFE_SPAN = 10

#count active weeks given the start date and end date
def count_weeks(start, end):
	startDay = (start - datetime.timedelta(days=start.weekday()))
	endDay = (end - datetime.timedelta(days=end.weekday()))
	#if the dates lie in same week, it return 0, so add 1
	weeks = abs(((startDay - endDay).days / 7))+1
	return weeks

#Parse the JSON
def read_file(events):
	first_loop = True
	with open(INPUT_FILE) as f:
		for line in f.readlines():
			ind = line.index('{')
			if first_loop:
				first_loop = False
				line_eval = line.strip()[ind:-1]
			else:
				line_eval = line.strip()[ind:-1]
			ingest(line_eval, events)
			
			
def ingest(e,D):
	dic = eval(e)
	
	if dic['type'] == CUSTOMER_KEY:
		customerID = dic['key']
	else:
		customerID = dic['customer_id']
	if DATE_KEY in dic:
		dic[DATE_KEY] = parse(dic[DATE_KEY])
	
	if customerID not in D:
		D[customerID] = [dic]
	else:
		D[customerID].append(dic)
		
def TopXSimpleLTVCustomers(x, D):
	customerLifeTimeValue = []
	active_weeks=0
	orderAmount = {}
	for customerID in D:
		for doc in D[customerID]:
			if SITE_KEY in doc['type']:
				visitKey = SITE_KEY
			else:
				visitKey = ORDER_KEY
		
		visitDates = [d[DATE_KEY] for d in D[customerID] if d['type'] == visitKey]

        #caluclate active weeks
		if visitDates  and ORDER_KEY in [d['type'] for d in D[customerID]]:
			active_weeks = count_weeks(min(visitDates), max(visitDates))

	
			for doc in D[customerID] :
				if doc['type'] == ORDER_KEY:
					orderDataDic = [ (d['key'], d['verb'], d['event_time'], float(d['total_amount'].split()[0]))
                           for d in D[customerID] if d['type'] == ORDER_KEY ]
			
			#aggregate the price using event time and verbs
			for key, verb, eventTime, price in orderDataDic:
				if key not in orderAmount:
					orderAmount[key] = (eventTime,price)
				else:
					if orderAmount[key][0] < eventTime:
						orderAmount[key] = (eventTime,price)
			sum = 0

			for id in orderAmount:
				sum = sum + orderAmount[id][1]
			#caluclate average revenue per week
			averageRevWeek = sum / active_weeks
				#Life time value formula specified 
			customerLifeSpan = 52 * averageRevWeek * LIFE_SPAN
			
			customerLifeTimeValue.append((customerID, customerLifeSpan))
		else:
		#if orders not found, append 0 as Live time value
			customerLifeTimeValue.append((customerID,0))
#Sort the list in descending order
	customerLifeTimeValue.sort(reverse=True, key=lambda x: x[1])
	return customerLifeTimeValue[:x]
	
#Main function	
if __name__ == '__main__':
	customer_arr = {} #Array to hold the customer Life time value
	read_file(customer_arr) #Read Data
	Result = TopXSimpleLTVCustomers(10, customer_arr)
	f= open(OUTPUT_FILE,"w")
	for data in Result:
		f.write("Customer ID: " + str(data[0]) + " Life Time Value: " + str(data[1]) + "\n")
	print "Ouput file produced in " + os.path.abspath(os.path.join(OUTPUT_FILE, os.pardir)) + "\output.txt"