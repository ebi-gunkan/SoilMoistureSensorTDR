#ライブラリのインポート
import os
import sys
import datetime
import csv
import glob

#定数の定義
STATUS_OK = 0
STATUS_NG = 1
C_SPEED = 300000000		#speed of light : m/s
PROBE_LENGTH = 90 / 1000	#length of probe : m

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
        temp = data[i+2].replace('[-','')
        temp = temp.replace('[','')
        temp = temp.replace(', 0.0]\n','')
        waveform_data[i] = float(temp)
    return(datetime_data,waveform_data)

#処理概要　土壌表面からの反射波の到達時刻（ns）を取得
#引数　time_domain_data；時間軸データ、waveform_data：波形データ
#戻り値　反射波の到達時刻配列（リスト型）
def Detect_PeakTime(time_domain_data,waveform_data):
    peak = waveform_data[0]
    peak_time_array = []

    i = 1
    #反射波の到達時刻の始まりを検知
    while peak < waveform_data[i]:
        peak = waveform_data[i]
        i += 1
        if i >= len(time_domain_data)-1:
            break
    peak_time_array.append(i-1)

    #反射波の到達時刻の終わりを検知
    while peak <= waveform_data[i]:
        peak_time_array.append(i)
        i += 1
        if i >= len(time_domain_data)-1:
            break

    return peak_time_array

#処理概要　プローブ終端からの反射波の到達時刻（ns）を取得
#引数　time_domain_data；時間軸データ、waveform_data：波形データ、peak_time_end：土壌表面からの反射波の到達時刻の終わり
#戻り値　反射波の到達時刻配列（リスト型）
def Detect_ReflectTime(time_domain_data,waveform_data,peak_time_end):
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

    #反射波の到達時刻の終わりを検知
    while reflect >= waveform_data[i]:
        reflect_time_array.append(i)
        i += 1
        if i >= len(time_domain_data)-1:
            break

    return reflect_time_array

#処理概要　伝搬時間tを取得
#引数　time_domain_data；時間軸データ、waveform_data：波形データ
#戻り値　測定成否、土壌表面からの反射波の到達時刻、プローブ終端からの反射波の到達時刻、伝搬時間(ns)
def Get_t(time_domain_data,waveform_data):
    #土壌表面からの反射波の到達時刻とプローブ終端からの反射波の到達時刻を取得
    peak_time_array = Detect_PeakTime(time_domain_data,waveform_data)
    reflect_time_array = Detect_ReflectTime(time_domain_data,waveform_data,peak_time_array[-1])

    #土壌表面からの反射波の到達時刻が複数のタイムステップにまたがる場合は平均値を計算
    t_cnt = 0
    peak_avg = 0
    for i in range(len(peak_time_array)):
        t_cnt += 1
        peak_avg += time_domain_data[peak_time_array[i]]
    peak_avg = peak_avg / t_cnt

    #プローブ終端からの反射波の到達時刻が複数のタイムステップにまたがる場合は平均値を計算
    t_cnt = 0
    reflect_avg = 0
    for i in range(len(reflect_time_array)):
        t_cnt += 1
        reflect_avg += time_domain_data[reflect_time_array[i]]
    reflect_avg = reflect_avg / t_cnt
    t = reflect_avg - peak_avg

    if peak_time_array[-1] == len(time_domain_data) - 1 or \
    reflect_time_array[-1] == len(time_domain_data) - 1:
        return STATUS_NG,peak_avg,reflect_avg,t
    else:
        return STATUS_OK,peak_avg,reflect_avg,t

#処理概要　比誘電率を計算
#引数　なし
#戻り値　なし
def Calc_RelativeDielectricConstance():
    #波形データ一覧を取得
    files_51 = sorted(glob.glob("./raw_data/*_51.txt"))
    files_101 = sorted(glob.glob("./raw_data/*_101.txt"))

    result = []
    for i in range(len(files_51)):
        #波形データ一覧を取得
        datetime_data,waveform_51 = Get_WaveFormDataArray(files_51[i])
        _,waveform_101 = Get_WaveFormDataArray(files_101[i])

        #時間軸データ一覧を取得
        time_domain_51 = Get_TimeDomainData(51)
        time_domain_101 = Get_TimeDomainData(101)

        #伝搬時間tを計算
        ans_51,peak_51,reflect_51,t_51 = Get_t(time_domain_51,waveform_51)
        ans_101,peak_101,reflect_101,t_101 = Get_t(time_domain_101,waveform_101)

        #比誘電率を計算
        if ans_51 == STATUS_NG and ans_101 == STATUS_NG:
            e = "#N/A"
            peak = "#N/A"
            reflect = "#N/A"
        elif ans_51 == STATUS_NG and ans_101 == STATUS_OK:
            e = str(((C_SPEED * t_101 * (10 ** (-9))) / (2 * PROBE_LENGTH)) ** 2)
            peak = peak_101
            reflect = reflect_101
        elif ans_51 == STATUS_OK and ans_101 == STATUS_OK:
            e = str(((C_SPEED * t_51 * (10 ** (-9))) / (2 * PROBE_LENGTH)) ** 2)
            peak = peak_51
            reflect = reflect_51
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
    writer.writerow(["datetime","peak time(ns)","reflect time(ns)","relative dielectrice constant(-)"])
    for i in range(len(result)):
        writer.writerow([result[i][0],result[i][1],result[i][2],result[i][3]])
        print([result[i][0],result[i][1],result[i][2],result[i][3]])
    f.close()


if __name__ == '__main__':
    Calc_RelativeDielectricConstance()
