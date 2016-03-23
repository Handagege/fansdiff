#!/usr/home/zhanghan5/anaconda2/bin/python
# -*- coding: utf-8 -*-


import sys
import numpy as np
import scipy.stats as ss
import random
from collections import *


def getFeatureInfo(filePath):
        indexFeatureDic = {}
        spfInfoList = []
        cnt = 0
        with open(filePath,'r') as f:
                for line in f:
                        data = line.strip().split('--')
                        tempInfoDic = {}
                        for i in data[1].split(','):
                                spdata = i.split(':')
                                tempInfoDic[spdata[0]] = spdata[1]
                        spfInfoList.append(tempInfoDic)
                        indexFeatureDic[cnt] = data[0].split(':')[1]
                        cnt += 1
        return indexFeatureDic,spfInfoList


def handleGender(value):
	pass


def handleStatus(value):
	if value != '2' and value != '7':
		return '0'
	else:
		return value

def handleAttenLevel(data,levelList=[-1,30,100,200,500,1000]):
        for index,value in enumerate(levelList):
                if index+1 == len(levelList):
                        return str(index)
                elif data > value and data <= levelList[index+1]:
                        return str(index)


def dataPrepOfPerUid(inputFile):
	'''
		read data frame like below:
		uid\tfanUid\tgender\tstatus\tprovince\tmarital_status\tdegree\tactv_freq\tage\tfiltered_atten_num...
		2217035934\t1000033177\t2\t1\t400\t0\t\N\t2\t00s\t80\t6\t0

		return a map which value is many list \
			composed by dic which restored each colomn stats data 
		exp: {uid1:[0.44,0.22,0.24,...],uid2:[...],...}
		           <----n colomn----->
	'''
	statsData = defaultdict(list)
        ratioLevelList = [-0.1,0.1,0.3,0.5,0.7,1]
	with open(inputFile,'r') as f:
		for line in f:
			data = line.strip().split(',')
                        if len(data) != 15:
                                continue
			uid = data[0]
			fanUid = data[1]
			fanGender = data[2] if data[2] != '0' else random.choice(['1','2'])
			fanType = handleStatus(data[3])
			prov = data[4]
                        maritalStatus = data[5]
                        degree = data[6]
                        actvFreq = data[7]
                        age = data[8]
                        attenLevel = handleAttenLevel(int(data[9]))
                        fanLevel = handleAttenLevel(int(data[10]))
                        duplexLevel = handleAttenLevel(int(data[11]))
                        constellation = data[12]
                        tranRatioLevel = handleAttenLevel(float(data[13])/31,ratioLevelList) if data[13] != '\N' else 0
                        origRatioLevel = handleAttenLevel(float(data[14])/31,ratioLevelList) if data[14] != '\N' else 0
			originTempData = [fanGender,fanType,prov,maritalStatus,degree,actvFreq,\
                        age,attenLevel,fanLevel,duplexLevel,constellation,tranRatioLevel,origRatioLevel]
			statsData[uid].append(originTempData)
        result = {}
        for uid in statsData:
                tempData = []
                statsData[uid] = np.array(statsData[uid])
                row,col = statsData[uid].shape
                for index in range(col):
                        tempRow = row
                        vCounter = Counter(statsData[uid][:,index])
                        emptyStr = '\N'
                        if emptyStr in vCounter:
                                tempRow -= vCounter[emptyStr]
                        tempData.append(dict((k,float(v)/tempRow) for k,v in vCounter.iteritems() if k != emptyStr))
                result[uid] = tempData
	return result


def transToArray(data,spfInfoList):
        newTransStdData = []
        for i in data:
                tempDataItem = []
                for index,value in enumerate(spfInfoList):
                        t = [i[index][vk] if vk in i[index] else 0.0 for vk in value]
                        tempDataItem.extend(t)
                newTransStdData.append(tempDataItem)
        return np.array(newTransStdData)


def transDicToArray(data,spfInfoList):
        newTransStdData = {}
        for k in data:
                i = data[k]
                tempDataItem = []
                for index,value in enumerate(spfInfoList):
                        t = [i[index][vk] if vk in i[index] else 0.0 for vk in value]
                        tempDataItem.extend(t)
                newTransStdData[k] = tempDataItem
        return newTransStdData


def analysisMain():
	import time
	beg = time.time()
        infoChinese = {0:'性别',1:'身份',2:'省份',3:'恋爱状态',4:'最高学历',5:'活跃等级',\
        6:'年龄段',7:'关注数等级',8:'粉丝数等级',9:'互粉数等级',10:'星座',11:'转发率',12:'原创率'}
	if len(sys.argv) != 3:
		print('case parameter : <commonFansDataFile> <fieldExpertFansDataFile>')
		exit(1)
        indexFeatureDic,spfInfoList = getFeatureInfo('../colomnExplain.data')
	fansSD1 = dataPrepOfPerUid(sys.argv[1])
	fansSD2 = dataPrepOfPerUid(sys.argv[2])
        cnt = 0
        colExplain = {}
        for index,value in enumerate(spfInfoList):
                for vk in value:
                        colExplain[cnt] = '{0}-{1}:{2}'.format(index,vk,value[vk])
                        cnt += 1

        fansSD1 = transToArray(fansSD1.values(),spfInfoList)
        fansSD2 = transToArray(fansSD2.values(),spfInfoList)
        print fansSD1
        print fansSD2

	print('\nset significance limit value : 0.05 if pvalue>0.05 accept data consistency else refuse\n')
	for index in range(cnt):
		tval,pval = ss.ttest_ind(fansSD1[:,index],fansSD2[:,index],equal_var=False)
		s = '{0}--feature ##{1}##: tvalue : {2:.4f} , pvalue : {3:.4f}\n' \
			.format(index,colExplain[index],tval,pval)
		print(s) 

def getUidFansDistribution():
	import time
	beg = time.time()
        infoChinese = {0:'性别',1:'身份',2:'省份',3:'恋爱状态',4:'最高学历',5:'活跃等级',\
        6:'年龄段',7:'关注数等级',8:'粉丝数等级',9:'互粉数等级',10:'星座',11:'转发率',12:'原创率'}
	if len(sys.argv) != 2:
		print('case parameter : <commonFansDataFile> <fieldExpertFansDataFile>')
		exit(1)
        indexFeatureDic,spfInfoList = getFeatureInfo('colomnExplain.data')
	fansSD = dataPrepOfPerUid(sys.argv[1])
        cnt = 0
        colExplain = {}
        for index,value in enumerate(spfInfoList):
                for vk in value:
                        colExplain[cnt] = '{0}-{1}'.format(infoChinese[index],value[vk])
                        cnt += 1

        fansSD = transDicToArray(fansSD,spfInfoList)
        for k in fansSD:
                f = open('./tt/'+str(k),'w')
                for index,value in enumerate(fansSD[k]):
                        s = '{0}--粉丝中 ##{1}## 占比 : {2:.4f}\n'.format(index,colExplain[index],value)
                        f.write(s+'\n')
                f.close()


if __name__ == "__main__":
        getUidFansDistribution()
    #   analysisMain() 



