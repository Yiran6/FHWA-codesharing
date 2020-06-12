# all the functions and detailed description can be found in loop_data_utility.py
from loop_data_utility import *
from datetime import *


def main():
    # run examples
    # provide the file path for your loop data
    p1 = '../acbcao/'
    
    date1 = datetime(2019,1,5,0,0)
    date2 = datetime(2019,3,22,0,0)
    raw_data_process(p1, date1, date2)

    # check if data is available based on the time of interest
    # and delete all the missing data
    #bc period
    bc1 = datetime(2019, 1, 5, 0, 0)
    bc2 = datetime(2019, 1, 11, 0, 0)
    #ac period
    ac1 = datetime(2019, 1, 12, 0, 0)
    ac2 = datetime(2019, 1, 18, 0, 0)
    #ao2 period
    ao21 = datetime(2019, 3, 16, 0, 0)
    ao22 = datetime(2019, 3, 22, 0, 0)

    acbcao = ['BC','AC','AO2']

    # for acbcao
    # get current available .xlsx file
    loop_vol1 = makeloopvol(acbcao, p1)
    acbcao_bond = [bc1, bc2, ac1, ac2, ao21, ao22]

    #acbcao
    loop_vol1 = excel_processing(p1, acbcao, acbcao_bond, loop_vol1)
    loc1 = get_loop_location(loop_vol1, p1)

    # Daily
    # weekday
    # specify hour range and daily range you are interested to get the loop_vol1
    WeekAvg, DayAvg = CalVol(loop_vol1, 0, 24, 1, 3)
    # weekend
    WeekAvg_kd, DayAvg_kd = CalVol(loop_vol1, 0, 24, 5, 6)

    # morning peak 6:00 am - 10:00 am
    # weekday
    WeekAvg_mor, DayAvg_mor = CalVol(loop_vol1, 5, 10, 1, 3)
    # weekend
    WeekAvg_mor_kd, DayAvg_mor_kd = CalVol(loop_vol1, 5, 10, 5, 6)

    # evening peak 3:00 pm - 7:00 pm (15:00 - 19:00)
    # weekday
    WeekAvg_eve, DayAvg_eve = CalVol(loop_vol1, 14, 19, 1, 3)
    # weekend
    WeekAvg_eve_kd, DayAvg_eve_kd = CalVol(loop_vol1, 14, 19, 5, 6)

    #calculate average hourly traffic volume
    AvgLPhr,AvgHr = CalHourAvg(loop_vol1, 0, 6)
    AvgLPhr,AvgHr_wd = CalHourAvg(loop_vol1, 1, 3)
    AvgLPhr,AvgHr_wk = CalHourAvg(loop_vol1, 5, 6)

    # daily avg based on all loops
    alldayAvg = CalallDayAvg(DayAvg)
    alldayAvg_mor = CalallDayAvg(DayAvg_mor)
    alldayAvg_eve = CalallDayAvg(DayAvg_eve)

    # make legend for AC period, BC period and AO period
    lgacbcao = ['Before closure (1/5 - 1/11)','After closure (1/12 - 1/18)','Adjusting (3/16-3/22)']
    # make legend for AT period, BT period
    lgatbt = ['Before tolling (11/2 - 11/8)','After tolling 1(11/9 - 11/15)','After tolling 2(11/16-11/22)']

    # plot hourly average
    plothr(lgacbcao, loop_vol1)

    #tidedictandplot(AvgHr, '')
    #tidedictandplot(AvgHr_wd, ' (weekday)', lgatbt)
    #tidedictandplot(AvgHr_wk, ' (weekend)', lgatbt)
    tidedictandplot(AvgHr_wd, ' (weekday)', lgacbcao)
    tidedictandplot(AvgHr_wk, ' (weekend)', lgacbcao)

if __name__ == '__main__':
    main()
