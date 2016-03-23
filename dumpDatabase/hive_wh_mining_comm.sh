#! /bin/sh

export HADOOP_CLASSPATH=$HADOOP_CLASSPATH
export JAVA_HOME=/usr/local/jdk1.6.0_21
export HADOOP_HOME=/usr/local/hadoop-2.4.0
export HIVE_HOME=/usr/local/hive-0.13.0/

#
# 数据类型枚举
#
#	USER: 网红账号
#	TARGET: 精准受众
#	FRQBHV: 高行为率用户
#	STRATEGY: 特定策略挖掘账号
#	BHVPATT: 网红行为模式 
#	FANSSTAT: 粉丝统计分析结果 
#	GROWNSTD: 网红评价标准 
#	GOODS: 商品 
#	TBLOG: 优质微博内容 
#
DATA_TYPE_ARRAY=("USER" "TARGET" "FRQBHV" "STRATEGY" "BHVPATT" "FANSSTAT" "GROWNSTD" "GOODS" "TBLOG")


#
# 表名枚举
#
# 账号:
#	网红账号表: wh_mining_account_user_field_dt
#	精准受众表: wh_mining_account_target_field_dt
#	高行为率用户表: wh_mining_account_frqbhv_dt 
#	特定策略账号挖掘数据表: wh_mining_account_strategy_dt
#
# 网红分析:
#	网红行为模式表: wh_mining_analyse_bhvpatt_field_dt
#	网红粉丝统计分析表: wh_mining_analyse_fansstat_field_dt
#	网红评价标准分析表: wh_mining_analyse_grownstd_field_dt
#
# 物料:
#	商品表: wh_mining_item_goods_field_dt
#	优质微博内容表: wh_mining_item_tblog_field_dt
#
TABLE_ARRAY=("wh_mining_account_user_field_dt" "wh_mining_account_target_field_dt" "wh_mining_account_frqbhv_dt" "wh_mining_account_strategy_dt" "wh_mining_analyse_bhvpatt_field_dt" "wh_mining_analyse_fansstat_filed_dt" "wh_mining_analyse_grownstd_field_dt" "wh_mining_item_goods_field_dt" "wh_mining_item_tblog_field_dt")


# 通过数据类型获取表名
# getTableName $DATA_TYPE
G_TABLE="null"
function getTableName()
{
	G_TABLE="null"
	L_NUM=${#DATA_TYPE_ARRAY[@]}
	for ((i=0; i<L_NUM; i++))
	do
		if [ "${DATA_TYPE_ARRAY[$i]}" == $1 ]
		then
			G_TABLE=${TABLE_ARRAY[$i]}
			return 1
		fi
	done
	
	echo "unsupport data type, exit!"
	echo "data type must in {${DATA_TYPE_ARRAY[@]:0:L_NUM}}"	
	
	return 0
}




