START_FREQ = 50000                   #NanoVNAのSTART周波数:50kHz
STOP_FREQ = 1000000000               #NanoVNAのSTOP周波数:1GHz
MEASUREMENT_POINT = 51               #NanoVNAの測定点数：51
RECALL_NO = 0                        #NanoVNAのキャリブレーションデータ番号：0
DEV_NAME = '/dev/ttyACM0'            #ラズパイ側で認識されるNanoVNAのデバイス名
BAUDRATE = 38400                     #NanoVNAとの通信におけるボーレート
C_SPEED = 300000000                  #光速（m/s）
PROBE_LENGTH = 90/1000               #プローブ長(m)
MINIMUM_SOIL_REFLECT = 0.02          #土壌表面での反射における反射係数の下限値
MAXIMUM_SOIL_REFLECT = 0.5           #土壌表面での反射における反射係数の上限値

if __name__ == '__main__':
    pass
