#!/bin/sh

if [ $# -ne 3 ]
then
    echo "Usage: $0 <which filed you need?>"
	exit -1
fi

export HADOOP_HOME=/usr/local/hadoop-2.4.0
export JAVA_HOME=/usr/local/jdk1.6.0_21
hivePath="/usr/local/hive-0.13.0/bin/hive"
hadoopPath="/usr/local/hadoop-2.4.0/bin/hadoop"

workPath="/data0/result/search_recommend/zhanghan/fansAnalysis"
cd $workPath
today=`date +%Y%m%d`
#yesterday=`date -d "2 day ago" +%Y%m%d`
yesterday=$2
amonthAgo=$3
#amonthAgo=`date -d "31 day ago" +%Y%m%d`

#get fans information
hdfsPath="/dw_ext/recmd/zhanghan/fansAnalysis"
wh_table="wh_mining_account_user_field_dt"
#get recent $wh_table date
PAR=`hive -e "show partitions $wh_table" | grep "$1"`
DT=`echo $PAR | awk -F "/" '{print $NF}' | awk -F "=" '{print $2}'`
echo "$DT"
#------------------------
fieldFans_hdfsPath="${hdfsPath}/$1_fansInfo"
selectHQL="insert overwrite directory '$fieldFans_hdfsPath'  \
		   select m.uid,m.fans_uid,tt1.gender,tt1.user_type_id,tt1.prov_id,tt1.marital_status,tt1.degree, \
		   tt2.actv_freq,tt3.age,tt4.filtered_atten_num,tt4.filtered_fans_num,tt4.filtered_recip_num,tt5.constellation, \
		   coalesce(tt6.tran_num,0),coalesce(tt7.orig_num,0) \
		   from mds_user_fanslist m \
		   left semi join ( \
				   select uid from $wh_table where dt='$DT' and field='$1' \
				   ) e on (m.uid=e.uid and m.dt='$yesterday') \
		   join (select * from mds_user_info where dt='$yesterday' and \
				   ((user_status <> '7' and user_status <> '8') or user_status is null)) tt1 \
		   on (m.fans_uid=tt1.uid) \
		   left outer join mds_bhv_user_active_month_stat tt2 \
		   on (m.fans_uid=tt2.uid and tt2.dt='$yesterday' and tt2.stat_type='2') \
		   left outer join bigdata_mds_user_bornyear_mining tt3 on (m.fans_uid=tt3.uid) \
		   join mds_user_relation_sum tt4 on (m.fans_uid=tt4.uid and tt4.dt='$yesterday') \
		   left outer join bigdata_mds_user_constellation_mining tt5 on (m.fans_uid=tt5.uid and tt5.dt='20160113') \
		   left outer join (select uid,count(distinct dt) as tran_num from mds_bhv_tblog_day where dt between '$amonthAgo' \
				   and '$yesterday' and is_weibo='10000' and app_class_code='10000' and tran_cnt>0 group by uid) tt6 \
		   on (m.fans_uid=tt6.uid) \
		   left outer join (select uid,count(distinct dt) as orig_num from mds_bhv_tblog_day where dt between '$amonthAgo' \
				   and '$yesterday' and is_weibo='10000' and app_class_code='10000' and orig_cnt>0 group by uid) tt7 \
		   on (m.fans_uid=tt7.uid);"
$hivePath -e "${selectHQL}"
######################################################
#get fans feature count of per uid by fans Information

cd $workPath/statsDataPrep/
uidFansFcount_hdfsPath="${hdfsPath}/$1_fansFeature_count"
$hadoopPath dfs -rmr $uidFansFcount_hdfsPath
/data0/spark-1.3.0/bin/spark-submit --class zhanghan.dataPrep \
		--master yarn-client \
		--jars /usr/local/hadoop-2.4.0/share/hadoop/common/lib/hadoop-lzo-cdh4-0.4.15-gplextras.jar \
		--executor-memory 12G \
		--executor-cores  4 \
		--num-executors 400 \
		--driver-memory 2G \
		target/fanInfoCook-v1.0.jar \
		$fieldFans_hdfsPath $uidFansFcount_hdfsPath 0.1 400

uidFansFcount_localPath="$workPath/data/$1_fansFeature_count"
$hadoopPath dfs -cat $uidFansFcount_hdfsPath/* > $uidFansFcount_localPath
#########################################
#get fans distribute statistic of per uid

cd $workPath/src
commonUidFansFcount_localPath="$workPath/data/commonUser10w_fansFeature_count"
./train.py $uidFansFcount_localPath $commonUidFansFcount_localPath
uidFansDSName="fansAnalysis_stats_$1"
mv fansAnalysisModel $workPath/dumpDatabase/$uidFansDSName
cd $workPath/dumpDatabase
./dump.sh $1


