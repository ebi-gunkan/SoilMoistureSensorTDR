#ライブラリのインポート
import os
import sys
import datetime
import csv
import glob

#自作ライブラリの場所を追加
sys.path.append(os.path.join(os.path.dirname(__file__),'./config'))

import config_data as config_data

#定数の定義
STATUS_OK = 0
STATUS_NG = 1
C_SPEED = config_data.C_SPEED
PROBE_LENGTH = config_data.PROBE_LENGTH

#処理概要　時間軸データが格納されたCSVファイルから読み出して配列に格納
#引数　measurement_point：測定点数
#戻り値　時間軸データ配列（リスト型）
def Get_TimeDomainData(measurement_point):
    f = open("./time_domain_data/time_domain_" + str(measurement_point) + ".csv","r")
    temp = csv.reader(f,delimiter = ",")

    time_domain_data = []
    for row in temp:
        if row[0] != "":
            time_domain_data.append(float(row[0]))
    f.close()

    return(time_domain_data)

#処理概要　測定した波形データが格納されたファイルから読み出して配列に格納
#引数　file_name：ファイル名
#戻り値　測定日時、波形データ配列（リスト型）
def Get_WaveFormDataArray(file_name):
    #時間軸データ読み出し
    f = open(file_name,"r")
    data = f.readlines()
    f.close()

    #日時データ読み出し
    datetime_data = data[1].replace("\n","")
    datetime_data = datetime_data.replace("/","-")
    datetime_data = datetime.datetime.strptime(datetime_data,'%Y-%m-%d %H:%M:%S')

    #波形データ読み出し
    waveform_data = []
    for i in range(len(data)-2):
        waveform_data.append(0)
        temp = data[i+2].replace('[','')
        temp = temp.replace(', 0.0]\n','')
        waveform_data[i] = float(temp)
    return(datetime_data,waveform_data)

#処理概要　土壌表面からの反射波の到達時刻（ns）を取得
#引数　time_domain_data；時間軸データ、waveform_data：波形データ
#戻り値　土壌水分の範囲、反射波の到達時刻配列（リスト型）
def Detect_SoilSurfaceReflect(time_domain_data,waveform_data):
    #土壌水分が中程度または多い場合
    reflect = waveform_data[0]
    reflect_time_array = []

    i = 1
    #反射波の到達時刻の始まりを検知
    while True:
        if reflect >= waveform_data[i] and \
        waveform_data[i] >= config_data.MINIMUM_SOIL_REFLECT and \
        waveform_data[i] < config_data.MAXIMUM_SOIL_REFLECT:
            break
        reflect = waveform_data[i]
        i += 1
        if i >= len(time_domain_data)-1:
            break
    reflect_time_array.append(i-1)

    #反射波の到達時刻の終わりを検知
    if i != len(time_domain_data) -1:
        while reflect <= waveform_data[i]:
            reflect_time_array.append(i)
            i += 1
            if i >= len(time_domain_data)-1:
                break
    theta_range = "high-middle"

    #土壌水分が少ない場合
    if i == len(time_domain_data)-1:
        #変曲点を求めるために反射係数の勾配の変化率（に相当するもの）を求める
        gradient = []
        for i in range(len(time_domain_data)-2):
            gradient.append(waveform_data[i+2] - waveform_data[i])
        gradient_change_rate = []
        for i in range(len(gradient)-1):
            gradient_change_rate.append(gradient[i+1]-gradient[i])

        #勾配の変化率が下がり始める点を探す
        reflect = gradient_change_rate[0]
        reflect_time_array = []
        i = 1
        while True:
            if reflect >= gradient_change_rate[i] and \
            waveform_data[i+2] >= config_data.MINIMUM_SOIL_REFLECT:
                break
            reflect = gradient_change_rate[i]
            i += 1
            if i >= len(gradient_change_rate)-1:
                break

        #反射波の到達時刻の始まりを検知
        while True:
            if reflect <= gradient_change_rate[i] and \
            waveform_data[i+2] >= config_data.MINIMUM_SOIL_REFLECT:
                break
            reflect = gradient_change_rate[i]
            i += 1
            if i >= len(gradient_change_rate)-1:
                break
        reflect_time_array.append(i - 1 + 2)

        #反射波の到達時刻の終わりを検知
        while reflect >= gradient_change_rate[i]:
            reflect_time_array.append(i + 2)
            i += 1
            if i >= len(gradient_change_rate)-1:
                break
        theta_range = "low"

    return theta_range,reflect_time_array

#処理概要　プローブ終端からの反射波の到達時刻（ns）を取得
#引数　time_domain_data；時間軸データ、waveform_data：波形データ、peak_time_end：土壌表面からの反射波の到達時刻の終わり、theta_range：土壌水分の範囲
#戻り値　反射波の到達時刻配列（リスト型）
def Detect_ProbeEndReflect(time_domain_data,waveform_data,peak_time_end,theta_range):
    #土壌水分が中程度または多い場合
    if theta_range == "high-middle":
        reflect = waveform_data[peak_time_end + 1]
        reflect_time_array = []

        i = peak_time_end + 2
        #反射波の到達時刻の始まりを検知
        while reflect > waveform_data[i]:
            reflect = waveform_data[i]
            i += 1
            if i >= len(time_domain_data)-1:
                break
        reflect_time_array.append(i-1)

        #ピークが出ていない場合はNG
        if i == len(time_domain_data)-1:
            ans = STATUS_NG
        #反射波の到達時刻の終わりを検知
        else:
            while reflect >= waveform_data[i]:
                reflect_time_array.append(i)
                i += 1
                if i >= len(time_domain_data)-1:
                    break
            ans = STATUS_OK

    #土壌水分が少ない場合
    elif theta_range == "low":
        #変曲点を求めるために反射係数の勾配の変化率（に相当するもの）を求める
        gradient = []
        for i in range(len(time_domain_data)-2):
            gradient.append(waveform_data[i+2] - waveform_data[i])
        gradient_change_rate = []
        for i in range(len(gradient)-1):
            gradient_change_rate.append(gradient[i+1]-gradient[i])

        #反射波の到達時刻の始まりを検知
        reflect_time = gradient_change_rate[peak_time_end - 2]
        reflect_time_array = []
        i = peak_time_end - 2 + 1
        while reflect_time < gradient_change_rate[i]:
            reflect_time = gradient_change_rate[i]
            i += 1
            if i >= len(gradient_change_rate)-1:
                break
        reflect_time_array.append(i - 1 + 2)

        #反射波の到達時刻の終わりを検知
        while reflect_time <= gradient_change_rate[i]:
            reflect_time_array.append(i + 2)
            i += 1
            if i >= len(gradinent_change_rate)-1:
                break
        ans = STATUS_OK

    return ans,reflect_time_array

#処理概要　伝搬時間tを取得
#引数　time_domain_data；時間軸データ、waveform_data：波形データ
#戻り値　測定成否、土壌表面からの反射波の到達時刻、プローブ終端からの反射波の到達時刻、伝搬時間(ns)
def Get_t(time_domain_data,waveform_data):
    #土壌表面からの反射波の到達時刻を取得
    theta_range,soil_surface_reflect_array \
    = Detect_SoilSurfaceReflect(time_domain_data,waveform_data)

    #プローブ終端からの反射波の到達時刻を取得
    ans_probe,probe_end_reflect_array = \
    Detect_ProbeEndReflect(time_domain_data,waveform_data, \
    soil_surface_reflect_array[-1],theta_range)

    if ans_probe == STATUS_OK:
        #土壌表面からの反射波の到達時刻が複数のタイムステップにまたがる場合は平均値を計算
        t_cnt = 0
        soil_reflect_avg = 0
        for i in range(len(soil_surface_reflect_array)):
            t_cnt += 1
            soil_reflect_avg += time_domain_data[soil_surface_reflect_array[i]]
        soil_reflect_avg = soil_reflect_avg / t_cnt

        #プローブ終端からの反射波の到達時刻が複数のタイムステップにまたがる場合は平均値を計算
        t_cnt = 0
        probe_reflect_avg = 0
        for i in range(len(probe_end_reflect_array)):
            t_cnt += 1
            probe_reflect_avg += time_domain_data[probe_end_reflect_array[i]]
        probe_reflect_avg = probe_reflect_avg / t_cnt
        t = probe_reflect_avg - soil_reflect_avg

        if soil_surface_reflect_array[-1] == len(time_domain_data) - 1 or \
        probe_end_reflect_array[-1] == len(time_domain_data) - 1:
            return STATUS_NG,soil_reflect_avg,probe_reflect_avg,t
        else:
            return STATUS_OK,soil_reflect_avg,probe_reflect_avg,t
    else:
            return STATUS_NG,0,0,0

#処理概要　比誘電率を計算
#引数　なし
#戻り値　なし
def Calc_RelativeDielectricConstance():
    #波形データ一覧を取得
    files_51 = sorted(glob.glob("./raw_data/*_51.txt"))

    result = []
    for i in range(len(files_51)):
        #波形データ一覧を取得
        datetime_data,waveform_51 = Get_WaveFormDataArray(files_51[i])

        #時間軸データ一覧を取得
        time_domain_51 = Get_TimeDomainData(config_data.MEASUREMENT_POINT)

        #伝搬時間tを計算
        ans_51,peak_51,reflect_51,t_51 = Get_t(time_domain_51,waveform_51)

        #比誘電率を計算
        if ans_51 == STATUS_NG:
            e = "#N/A"
            peak = "#N/A"
            reflect = "#N/A"
        elif ans_51 == STATUS_OK:
            e = str(((C_SPEED * t_51 * (10 ** (-9))) / (2 * PROBE_LENGTH)) ** 2)
            peak = str(peak_51)
            reflect = str(reflect_51)
        else:
            e = "#N/A"
            peak = "#N/A"
            reflect = "#N/A"

        result.append([str(datetime_data),peak,reflect,e])

    #CSVファイルに書き出し
    f = open("./relative_dielectric_constant_data/result.csv","w")
    writer = csv.writer(f)

    print("relative dielectric donstant data has saved as result.csv in directory 'relative_dielectric_constant_data'")
    print("data:")
    writer.writerow(["datetime","reflect time at soil surface(ns)","reflect time at probe end(ns)","relative dielectrice constant(-)"])
    for i in range(len(result)):
        writer.writerow([result[i][0],result[i][1],result[i][2],result[i][3]])
        print([result[i][0],result[i][1],result[i][2],result[i][3]])
    f.close()

if __name__ == '__main__':
    Calc_RelativeDielectricConstance()
