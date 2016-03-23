#!/usr/home/zhanghan5/anaconda2/bin/python

import sys


def test1():
        fout = open('data.csv','w')
        with open(sys.argv[1],'r') as f:
                for line in f:
                        d = line.strip().split(': ')
                        if len(d) == 4:
                                s = d[0].split('##')[1]
                                id = s.split(':')[0].split('-')[1]
                                info = s.split(':')[1]
                                tvalue = d[2].split(' , ')[0]
                                pvalue = d[3]
                                fout.write('{0},{1},{2},{3}\n'.format(id,info,tvalue,pvalue))


def test2():
        fout = open(sys.argv[1]+'.csv','w')
        with open(sys.argv[1],'r') as f:
                for line in f:
                        d = line.strip().split(': ')
                        if len(d) == 2:
                                feature = d[0].split('##')[1]
                                fout.write('{0},{1}\n'.format(feature,d[1]))


if __name__ == "__main__":
        test2()
