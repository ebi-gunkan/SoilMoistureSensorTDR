#ライブラリのインポート
import os
import sys
import datetime
import RPi.GPIO as GPIO

#自作ライブラリの場所を追加
sys.path.append(os.path.join(os.path.dirname(__file__),'./lib'))

#自作ライブラリのインポート
import SoilMoisture as soil_moisture

#処理概要　測定データをテキストファイルに書き出す
#引数　measured_data：測定データ、data_point：測定点数
#戻り値　なし
def Record_MeasurementData(measured_data,data_point):
    #書き込み先のファイル名を取得
    now = datetime.datetime.now()
    file_name = format(now.year,"#04d") \
                + format(now.month,"#02d") \
                + format(now.day,"#02d") + "_" \
                + format(now.hour,"#02d") \
                + format(now.minute,"#02d") + "_" \
                + str(data_point) + ".txt"

    #ファイルがなければ新規作成
    if not os.path.isfile("./data/" + file_name):
        f = open("./data/" + file_name,"w")
        f.write("date,t(ns)\r\n")
        f.close()

    #書き込みデータを作成
    f = open("./data/" + file_name,"a")
    f.write(now.strftime('%04Y/%m/%d %H:%M:%S') + str("\n"))
    for i in range(len(measured_data)):
        f.write(str(measured_data[i]) + "\n")
    f.close()

#処理概要　測定実行
#引数　data_point：測定点数
#戻り値　測定成否（0：成功、1：失敗）
def Execute(data_point):
    #土壌水分の測定
    ans,measured_data = soil_moisture.Get_SoilMoisture(data_point)

    if ans == 0:
        #土壌水分の記録
        Record_MeasurementData(measured_data,data_point)
    return(ans)

if __name__ == '__main__':
    #コマンドライン引数からデータポイント数を取得
    args = sys.argv
    data_point = int(args[1])

    try:
        ans = Execute(data_point)
        sys.stdout.write(str(ans))
    except KeyboardInterrupt:
        pass
