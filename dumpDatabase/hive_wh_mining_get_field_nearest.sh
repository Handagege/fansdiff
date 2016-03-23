#! /bin/sh

#
# hive_wh_mining_get_nearest.sh
#
# 从hive中按领域分区获取wanghong-mining最近的结果数据
# 通过de_rev_seq制定获取最近的第n次结果(按dt倒序)
#
# 参数: 
#	data_type - 数据类型, 详见 ./hive_wh_mining_comm.sh
#	field - 领域分区标志
#	dt_rev_seq - 日期分区的反向顺序, 从0开始计数 
#	out_file - 输出文件
#

if [ $# -ne 4 ]
then
	echo "Usage: $0 <data_type> <field> <dt_rev_seq> <out_file>"
	exit -1
fi

. ./hive_wh_mining_comm.sh

DATA_TYPE=$1
FIELD=$2
DT_REV_SEQ=$3
OUT_FILE=$4

getTableName $DATA_TYPE
TABLE=$G_TABLE
if [ "$TABLE" == "null" ]
then
	exit -1
fi



HQL="SHOW PARTITIONS $TABLE"
echo '-----'
echo "HQL: $HQL"
echo '-----'
PAR=`$HIVE_HOME/bin/hive -e "\"$HQL\"" | grep $FIELD`
DT_CNT=`echo $PAR | awk '{print NF}'`
if ((DT_CNT<DT_REV_SEQ+1))
then
	echo "dt_rev_seq out of range!"
	echo "there are only $DT_CNT partitions of dt"
	exit -1
fi
((NO=DT_CNT-DT_REV_SEQ))
DT=`echo $PAR | awk '{print $'''$NO'''}' | awk -F "/" '{print $NF}' | awk -F "=" '{print $2}'`


HQL="SELECT * FROM $TABLE WHERE field='$FIELD' AND dt='$DT'"
echo '-----'
echo "HQL: $HQL"
echo '-----'
$HIVE_HOME/bin/hive -e "\"$HQL\"" > $OUT_FILE


exit 0


