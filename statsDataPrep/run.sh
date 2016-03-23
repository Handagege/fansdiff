#!/bin/sh


if [ $# -ne 1 ]
then
	echo "Usage: $0 <which filed you need?>"
	exit -1
fi


inputFile="/dw_ext/recmd/zhanghan/fansAnalysis/$1_fans"
outputFile="/dw_ext/recmd/zhanghan/fansAnalysis/$1_stats"
hadoop dfs -rmr $outputFile

/data0/spark-1.3.0/bin/spark-submit --class zhanghan.dataPrep \
		--master yarn-client \
		--jars /usr/local/hadoop-2.4.0/share/hadoop/common/lib/hadoop-lzo-cdh4-0.4.15-gplextras.jar \
		--executor-memory 8G \
		--executor-cores  4\
		--num-executors 400 \
		--driver-memory 2G \
		target/fanInfoCook-v1.0.jar \
		$inputFile $outputFile 0.1 400

hadoop dfs -cat $outputFile/* > $1_stats
