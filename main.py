#ライブラリのインポート
import os
import sys
import datetime
import RPi.GPIO as GPIO

#自作ライブラリの場所を追加
sys.path.append(os.path.join(os.path.dirname(__file__),'./lib'))
sys.path.append(os.path.join(os.path.dirname(__file__),'./config'))

#自作ライブラリのインポート
import SoilMoisture as soil_moisture
import config_data as config_data

#処理概要　測定データをテキストファイルに書き出す
#引数　measured_data：測定データ、data_point：測定点数
#戻り値　なし
def Record_MeasurementData(measured_data):
    data_point = config_data.MEASUREMENT_POINT
    #書き込み先のファイル名を取得
    now = datetime.datetime.now()
    file_name = format(now.year,"#04d") \
                + format(now.month,"#02d") \
                + format(now.day,"#02d") + "_" \
                + format(now.hour,"#02d") \
                + "00.txt"

    #ファイルがなければ新規作成
    if not os.path.isfile("./raw_data/" + file_name):
        f = open("./raw_data/" + file_name,"w")
        f.write("date,t(ns)\r\n")
        f.close()

    #書き込みデータを作成
    f = open("./raw_data/" + file_name,"a")
    f.write(now.strftime('%04Y/%m/%d %H:%M:%S') + str("\n"))
    for i in range(len(measured_data)):
        f.write(str(measured_data[i]) + "\n")
    f.close()

#処理概要　測定実行
#引数　data_point：測定点数
#戻り値　測定成否（0：成功、1：失敗）
def Execute():
    #土壌水分の測定
    ans,measured_data = soil_moisture.Get_SoilMoisture()

    if ans == 0:
        #土壌水分の記録
        Record_MeasurementData(measured_data)
    return(ans)

if __name__ == '__main__':
    try:
        ans = Execute()
        sys.stdout.write(str(ans))
    except KeyboardInterrupt:
        pass
