package zhanghan

import util.control.Breaks._
import org.apache.spark.{HashPartitioner, SparkConf, SparkContext}
import org.apache.spark.rdd.RDD
import org.apache.spark.SparkContext._
import scala.collection.mutable.{ArrayBuffer, Map}

/**
 * Created by zhanghan5 on 2016/1/4.
 */
object dataPrep {

  val colomnInfo = Array(
    Array("1","2"),
    Array("0","2","7"),
    Array("34","11","12","13","14","15","50","35","62","44","45","52","46","21","22",
      "23","41","42","43","32","36","64","63","37","31","51","54","65","53","33",
      "61","71","81","82","100","400"),
    Array("0","1","2","3","4","5","6","7","8","9","10"),
    Array("1","2","3","4","5"),
    Array("1","2","3","4","5","9"),
    Array("40s","50s","60s","70s","80s","90s","00s"),
    Array("0","1","2","3","4","5"),
    Array("0","1","2","3","4","5"),
    Array("0","1","2","3","4","5"),
    Array("白羊座","金牛座","双子座","巨蟹座","狮子座","处女座","天秤座",
      "天蝎座","射手座","摩羯座","水瓶座","双鱼座"),
    Array("0","1","2","3","4"),
    Array("0","1","2","3","4"))

  def handleAttenLevel(v: Double,levelList: Array[Double]=Array(-1,30,100,200,500,1000)) = {
    var level = -1
	breakable {
	  for(index <- 0 until levelList.length){
	    if(index+1 == levelList.length) level = index
	    else if(v > levelList(index) && v <= levelList(index+1)){
	    level = index
	    break()
	    }
	  }
	}
	level.toString
  }

  def transToStdVector(v: Array[String]) = {
    val stdVector = new Array[String](v.length)
	//gender
	stdVector(0) = v(0)
	//status
	stdVector(1) = if(v(1) != "2" && v(1) != "7") "0" else v(1)
	//province
	stdVector(2) = v(2)
	//maritalStatus
	stdVector(3) = v(3)
	//degree
	stdVector(4) = v(4)
	//actvFreq
	stdVector(5) = v(5)
	//age range
	stdVector(6) = v(6)
	//attenLevel fansLevel recipLevel(duplex relation)
	stdVector(7) =  handleAttenLevel(v(7).toDouble)
	stdVector(8) =  handleAttenLevel(v(8).toDouble)
	stdVector(9) =  handleAttenLevel(v(9).toDouble)
	//constellation
	stdVector(10) = v(10)
	//tranRatioLevel origRatioLevel 
	val ratioLevel = Array(-0.1,0.1,0.3,0.5,0.7,1)
	//val tranCnt = if(v(11) != "\\N") v(11) else "0"
	//val origCnt = if(v(12) != "\\N") v(12) else "0"
	stdVector(11) = handleAttenLevel(v(11).toDouble/30,ratioLevel)
	stdVector(12) = handleAttenLevel(v(12).toDouble/30,ratioLevel)
	stdVector
  }

  def getFeatureDistribution(it: Iterator[Array[String]]) = {
    val featureCntMap = Map[String,Int]()
    for(i <- 0 until colomnInfo.length){
	  for(v <- colomnInfo(i)) featureCntMap(i+"-"+v) = 0
    }
    while(it.hasNext){
      val v = it.next()
	  if(v.length == colomnInfo.length){
		val stdVector = transToStdVector(v)
        for(i <- 0 until colomnInfo.length){
          val k = i + "-" + stdVector(i)
          if(featureCntMap.contains(k)){
            featureCntMap(k) += 1
          }
        }
	  }
    }
	featureCntMap.map{case(k,v) => k+":"+v}.toArray
  }

  def getStdSample(it: Iterator[(String,Iterable[Array[String]])]) = {
    val result = ArrayBuffer[(String,Array[String])]()
    while(it.hasNext) {
      val v = it.next()
	  if(v._2.iterator.length > 100){
		val stdSampleItem = getFeatureDistribution(v._2.iterator)
		result += Tuple2(v._1,stdSampleItem)
	  }
    }
    result.iterator
  }

  def main(args: Array[String]): Unit = {
	if(args.length < 4)
	{
		System.err.println("Usage: <inputFile> <outputFile> <sample ratio> <partitionNum>")
		System.exit(1)
	}
    val conf = new SparkConf()
    val sc = new SparkContext(conf)
    val inputFile = args(0)
    val outputFile = args(1)
	val partitionNum = args(3).toInt
	val sampleRatio = args(2).toDouble
    val lines = sc.textFile(inputFile,partitionNum)
    val uidToFansInfoRdd = lines.map(x => {
      val data = x.split("\01")
      (data(0),data.slice(2,data.length))
    })
    val statsResult = uidToFansInfoRdd.partitionBy(new HashPartitioner(partitionNum))
	  .sample(false,sampleRatio)
	  .groupByKey()
      .mapPartitions(it => getStdSample(it))
      .map(x => x._1 + "<>" + x._2.mkString(","))
      .saveAsTextFile(outputFile)
  }
}
