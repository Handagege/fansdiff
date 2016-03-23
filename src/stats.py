#!/usr/bin/python
import random


def statsFansNum(file):
	data = {}
	with open(file,'r') as f:
		for line in f:
			d = line.strip().split('\t')
			uid = d[0]
			fan = d[1]
			if uid in data:
				data[uid] += 1
			else:
				data[uid] = 0
	print len(data)
        for i in d:
                print i,data[i]
        


def statsCommonUserFans(file):
	upperLimit = 5001
	interval = 500
	statsRange = list(range(0,upperLimit,interval))
	fansNumStatsList = [0]*(upperLimit/interval+1)
	with open(file,'r') as f:
		for line in f:
			d = line.strip().split('\t')
			uid = d[0]
			fansNum = int(d[3])
			if fansNum < upperLimit:
				fansNumStatsList[fansNum/interval] += 1
			else:
				fansNumStatsList[-1] += 1
	for index,value in enumerate(fansNumStatsList):
		if index+1 == len(fansNumStatsList):
			print '>{0} : {1}'.format(index*interval,value)
		else:
			print '{0}~{1} : {2}'.format(index*interval,(index+1)*interval,value)


def sampleCommonUser(file):
	lowerLimit = 1000
	sampleResult = []
	with open(file,'r') as f:
		for line in f:
			d = line.strip().split('\t')
			uid = d[0]
			fansNum = int(d[3])
			if fansNum > lowerLimit:
				sampleResult.append(uid)
	sampleResult = random.sample(sampleResult,50000)
	fout = open('commonUserSample.data','w')
	for i in sampleResult:
		fout.write(i+'\n')
	fout.close()



if __name__ == '__main__':
	#file = './data/car_field_expert_fans'
	#statsFansNum(file)
	file = './data/commonUserTotal.data'
	#statsCommonUserFans(file)
	sampleCommonUser(file)
			
