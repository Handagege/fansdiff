#!/bin/sh


export HADOOP_HOME=/usr/local/hadoop-2.4.0
export JAVA_HOME=/usr/local/jdk1.6.0_21
hivePath="/usr/local/hive-0.13.0/bin/hive"
hadoopPath="/usr/local/hadoop-2.4.0/bin/hadoop"

workPath="/data0/result/search_recommend/zhanghan/fansAnalysis"
cd $workPath

attr=(cosmetics emotion sex car house clothing ecom it design)

for var in ${attr[@]};
do
	echo "************${var} field tast start***************"
	./start.sh $var
	echo "************${var} field tast end*****************"
done
