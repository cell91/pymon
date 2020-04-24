'''
This script tests all the servers listed in the "sites.csv" file and appends the HTTP Response code 
in the same file. This runs on multithreading and the no. of threads can be defined.
Place all the servers in the "sites.csv" each in a new line and execute "main.py"

Modify the "threadCount" for maximum number of threads
By Revanth Kumar
'''
import csv
import requests
import threading
import math
import socket
from selenium import webdriver #screenshots
import uuid
import time
import json

options = webdriver.ChromeOptions()
options.add_argument('headless')

fileContent = []
threadCount = 5 #No. of multi threads to use


#loading the data
with open("sites.csv") as csvFile:
	csvData = csv.reader(csvFile,delimiter=',')

	for row in csvData:
		row = [row[0]] #take only the site in case of refreshing the 'sites.csv' file
		fileContent.append(row)

#resolve url to ip
def removeHead(url):
	s = url.split('//')
	s = s[1].split('/')
	return s[0]

#resolve url to ip
def resolve(address):
	v = removeHead(address)
	return socket.gethostbyname(v)

#getting http requests
def httpStatus(siteArray):
	try:
		res = requests.get(siteArray[0])
		statusList = []
		for i in res.history:
			statusList.append(i.status_code)

		statusList.append(res.status_code)
		siteArray.append(json.dumps(statusList))
		siteArray.append(str(math.floor(res.elapsed.total_seconds()*1000))+'ms') #req time in ms rounded
		siteArray.append(res.headers) #headers
		siteArray.append(resolve(res.url))
		return None
	except:
		print(siteArray[0]+" is either incorrent or dosen't exist. Marked eith ERROR in the logs.")
		siteArray.append(json.dumps(["NOTFOUND"]))
		return None


#calculating thread batches based on given ThreadCount
threadBatch = math.floor(len(fileContent)/threadCount)
threadExtra = len(fileContent) % threadCount

index = 0
threads = []

if __name__ == "__main__":
	print("Starting threads. max. threads "+str(threadCount))

	#process thread batches
	for b in range(threadBatch):
		#init one thread Batch
		print("starting thread batch :"+str(b))
		for n in range(threadCount):
			c = threading.Thread(target = httpStatus,args = (fileContent[index],))
			c.start()
			threads.append(c)
			index += 1


		#wait for the thread bratch to complete
		for t in threads:
			t.join()

		#clear threads after done
		threads = []


	#process extra threads at last
	for i in range(threadExtra):
		print('started extra thread: ' + str(index))
		c = threading.Thread(target = httpStatus,args = (fileContent[index],))
		c.start()
		threads.append(c)
		index += 1

	#Wait for completion
	for t in threads:
		t.join()

	threads = [] #clear threads

	print("Task Completed. Starting collection of screenshots. This may take a while...")

	with webdriver.Chrome('chromedriver',options=options) as driver:
		for site in fileContent:
			s = json.loads(site[1])
			#take screenshot only if != 200 OK
			if s[-1] != 200 and s[-1] != "NOTFOUND":
				driver.set_window_size(1280,720)
				driver.get(site[0])
				name = removeHead(site[0])+ '_' +str(uuid.uuid4())+'.png'
				driver.save_screenshot('screenshots/'+name)
				site.append(name)
	

	#writing the data to the same file
	with open('sites.csv',mode='w',newline='') as csvFile:
		csvData = csv.writer(csvFile, delimiter=',')

		for line in fileContent:
			csvData.writerow(line)

	print("All Completed.")



#21.04.2020, 08:45PM Done.