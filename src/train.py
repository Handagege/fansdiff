#!/data0/result/search_recommend/zhanghan/anaconda2/bin/python
# -*- coding: utf-8 -*-


import sys
import numpy as np
import scipy.stats as ss
import random
import time
import codecs
from collections import *


def getFeatureInfo(filePath):
    spfInfoList,spfInfoExplainList = [],[]
    cnt = 0
    with codecs.open(filePath,'r','euc-cn') as f:
        for line in f:
            data = line.strip().split('--')
            featureType = int(data[0].split(':')[0])
            featureTypeExplain = data[0].split(':')[1]
            for i in data[1].split(','):
                spdata = i.split(':')
                spfInfoList.append("{0}-{1}".format(featureType,spdata[0]))
                spfInfoExplainList.append("{0}-{1}".format(featureTypeExplain,spdata[1]))
            cnt += 1
    return spfInfoList,spfInfoExplainList


def dataPrepOfPerUid(inputFile,spfInfoList):
    '''
    read data frame like below:
        5705372166<>4-5:0,9-0:2,10-天蝎座:0,2-82:0,7-2:3,8-1:2,5-4:0,2-61:1
    return a map which value is many list \
        composed by dic which restored each colomn stats data 
    exp: {uid1:[0.44,0.22,0.24,...],uid2:[...],...}
           <----n colomn----->
    '''
    uidToFansFD = {}
    arrayIndexByFeature = map(lambda x:x.split('-')[0],spfInfoList)
    missingData = False
    with codecs.open(inputFile,'r','utf-8') as f:
        for line in f:
            data = line.strip().split('<>')
            uid = data[0]
            featureCntStr = data[1].split(',')
            tempCntDic = defaultdict(int)
            tempSpfCntList = [0]*len(spfInfoList)
            tempRatioList = [0]*len(spfInfoList)
            for i in featureCntStr:
                featureToCntList = i.split(':')
                tempSpfCntList[spfInfoList.index(featureToCntList[0])] = int(featureToCntList[1])
                tempCntDic[featureToCntList[0].split('-')[0]] += int(featureToCntList[1])
            for index,value in enumerate(tempSpfCntList):
                if tempCntDic[arrayIndexByFeature[index]]:
                    tempRatioList[index] = float(value)/tempCntDic[arrayIndexByFeature[index]]
                else:
                    #print uid,arrayIndexByFeature[index]
                    tempRatioList[index] = -1
            uidToFansFD[uid] = tempRatioList
    return uidToFansFD


def analysisMain(fieldExpertDSmatrix,commonUserDSmatrix):
    (rowNum,colNum) = fieldExpertDSmatrix.shape
    distributionIndexDataList = []
    for index in range(colNum):
        #delete missing data
        fieldExpertDSArray = np.array(filter(lambda x:x != -1,fieldExpertDSmatrix[:,index]))
        commonUserDSArray = np.array(filter(lambda x:x != -1,commonUserDSmatrix[:,index]))
        tval,pval = ss.ttest_ind(fieldExpertDSArray,commonUserDSArray,equal_var=False)
        distributionIndexDataList.append((tval,pval))
    return distributionIndexDataList


def prettyPrint(spfInfoExplainList,dIndexDataList):
    print(''.join(['*']*100))
    print('*{0: ^98}*'.format('set significance limit value : 0.05 if pvalue>0.05 accept data consistency else refuse'))
    print(''.join(['*']*100))
    print('*{0: ^10}{1: ^36}{2: ^26}{3: ^26}*'.format('ID','feature','tvalue','pvalue'))
    print(''.join(['*']*100))
    for index,value in enumerate(spfInfoExplainList):
        s = '*{0: ^10}{1: ^36}{2: ^26.4f}{3: ^26.6f}*' \
            .format(index,value,dIndexDataList[index][0],dIndexDataList[index][1])
        print(s) 
    print(''.join(['*']*100))
    

def produceModel(spfInfoList,fieldExpertDSdic,commonUserDSdic,modelFile):
    infoEnglish = ['gender','user_type','prov_id','marriage','edu','active_lev','age_group','flw_cnt_lev','fans_lev','mufans_lev','conste', \
    'fwd_mdf_lev','ori_mdf_lev']
    fieldExpertDSmatrix = np.array(fieldExpertDSdic.values())
    commonUserDSmatrix = np.array(commonUserDSdic.values())
    fieldList = ['feat','val','cnt_wh','cnt_cu','mean_wh','mean_cu','var_wh','var_cu',\
    't_val','p_val','diff','extend']
    (rowNum,colNum) = fieldExpertDSmatrix.shape
    dIndexDataList = []
    for index in range(colNum):
        fieldExpertDSArray = np.array(filter(lambda x:x != -1,fieldExpertDSmatrix[:,index]))
        commonUserDSArray = np.array(filter(lambda x:x != -1,commonUserDSmatrix[:,index]))
        tval,pval = ss.ttest_ind(fieldExpertDSArray,commonUserDSArray,equal_var=False)
        spfInfo = spfInfoList[index].split('-')
        feat = infoEnglish[int(spfInfo[0])]
        val = spfInfo[1]
        cnt_wh = str(len(fieldExpertDSArray))
        cnt_cu = str(len(commonUserDSArray))
        mean_wh = np.mean(fieldExpertDSArray)
        mean_cu = np.mean(commonUserDSArray)
        var_wh = np.var(fieldExpertDSArray)
        var_cu = np.var(commonUserDSArray)
        diff = (mean_wh-mean_cu)/(np.sqrt(var_cu)*(1-pval)/(1+pval))
        extend = "null"
        dIndexDataList.append((feat,val,cnt_wh,cnt_cu,mean_wh,mean_cu,var_wh,var_cu,tval,pval,diff,extend))
    fout = open(modelFile,'w')
    for index,value in enumerate(dIndexDataList):
        s = '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}'.format(*value)
        fout.write(s+'\n')
    fout.close()


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")
    beg = time.time()
    if len(sys.argv) != 3:
		print('case parameter : <fieldExpertFansDataFile> <commonFansDataFile>')
		exit(1)
    spfInfoList,spfInfoExplainList = getFeatureInfo('./colomnExplain.data')
    modelFile = "fansAnalysisModel"
    fieldExpertDSdic = dataPrepOfPerUid(sys.argv[1],spfInfoList)
    commonUserDSdic = dataPrepOfPerUid(sys.argv[2],spfInfoList)
    produceModel(spfInfoList,fieldExpertDSdic,commonUserDSdic,modelFile) 

