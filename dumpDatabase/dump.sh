#!/bin/sh

if [ $# -ne 1 ]
then
    echo "which field you need?"
	exit -1
fi

export HADOOP_HOME=/usr/local/hadoop-2.4.0
export JAVA_HOME=/usr/local/jdk1.6.0_21

today=`date +%Y%m%d`
yesterday=`date -d "1 day ago" +%Y%m%d`
aweekAgo=`date -d "7 day ago" +%Y%m%d`
hdfsTable="wh_mining_analyse_fansstat_field_dt"
createHQL="CREATE TABLE IF NOT EXISTS $hdfsTable ( \
		   feat string, \
		   val string, \
		   cnt_wh double, \
		   cnt_cu double, \
		   mean_wh double, \
		   mean_cu double, \
		   var_wh double, \
		   var_cu double, \
		   t_val double, \
		   p_val double, \
		   diff double, \
		   extend string) \
		   PARTITIONED BY (field string,dt string) \
		   ROW FORMAT DELIMITED \
		   FIELDS TERMINATED BY ',';"

hivePath="/usr/local/hive-0.13.0/bin/hive"
localDataPath="fansAnalysis_stats_$1"
selectHQL="LOAD DATA LOCAL INPATH '$localDataPath' overwrite into table $hdfsTable \
		   PARTITION (field='$1',dt='$today');"

$hivePath -e "${createHQL}${selectHQL}"
