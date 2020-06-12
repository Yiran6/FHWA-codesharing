import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.pyplot import figure
figure(num=None, figsize=(6, 4), dpi=160, facecolor='w', edgecolor='k')
matplotlib.rcParams.update({'font.size': 11,})
plt.rcParams["font.family"] = "Arial"


# trip rate
#data = pd.read_csv('/Users/jeremywang/Desktop/Tolling/trip_rate_west.csv')
#t1 = [i for i in range(7)]
#t2 = [i for i in range(7,14)]
#t3 = [i for i in range(14,21)]
#
#plt.plot(t1, data.x.iloc[t1], 'r', t1, data.x.iloc[t2], '--*b',t1, data.x.iloc[t3], '-ok')
#plt.gca().legend(('Nov 2-8','Nov 9-15','Nov 16-22'))
#
#plt.xticks(t1,['Sat','Sun','Mon','Tue','Wed','Thu','Fri'])
#plt.gca().set_ylim([2.7,3.9])
#plt.gca().set_xlabel('Day of the week')
#plt.gca().set_ylabel('Mean trip rate')
#plt.gca().annotate('Tolling began', xy=(0.1, 3.4), xytext=(1,3.39),
#        arrowprops=dict(facecolor='blue', shrink=1))


## PMT
#data = pd.read_csv('/Users/jeremywang/Desktop/Tolling/PMT_west.csv')
#t1 = [i for i in range(7)]
#t2 = [i for i in range(7,14)]
#t3 = [i for i in range(14,21)]
#
#plt.plot(t1, data.x.iloc[t1], 'r', t1, data.x.iloc[t2], '--*b',t1, data.x.iloc[t3], '-ok')
#plt.gca().legend(('Nov 2-8','Nov 9-15','Nov 16-22'))
#
#plt.xticks(t1,['Sat','Sun','Mon','Tue','Wed','Thu','Fri'])
#plt.gca().set_xlabel('Day of the week')
#plt.gca().set_ylabel('Mean Person Miles Traveled')
#plt.gca().annotate('Tolling began', xy=(0.1, 13.7), xytext=(1,12.5),
#        arrowprops=dict(facecolor='blue', shrink=1))


## commute trip departure time
#data = pd.read_csv('/Users/jeremywang/Desktop/Tolling/dp_west.csv')
#
#t1 = [i for i in range(48)]
#t2 = [i*4+1 for i in range(12)]
#
#plt.plot(t1, data.week1, '--r', t1, data.week2, '-k',t1, data.week3, ':b')
#plt.gca().legend(('Nov 4-8','Nov 11-15','Nov 18-22'))
#
#plt.xticks(t2,[1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23])
#plt.gca().set_xlabel('Time of the day')
#plt.gca().set_ylabel('Ratio of commute trips')

## Mean commute duration
data = pd.read_csv('/Users/jeremywang/Desktop/Tolling/commute_tt_west.csv')
t1 = [i for i in range(2,7)]
t2 = [i for i in range(9,14)]
t3 = [i for i in range(16,21)]

plt.plot(t1, data.x.iloc[t1], 'r', t1, data.x.iloc[t2], '--*b',t1, data.x.iloc[t3], '-ok')
plt.gca().legend(('Nov 4-8','Nov 11-15','Nov 18-22'))

plt.xticks(t1,['Mon','Tue','Wed','Thu','Fri'])
plt.gca().set_xlabel('Day of the week')
plt.gca().set_ylabel('Mean commute duration (Minutes)')
plt.gca().annotate('Tolling began', xy=(0.1, 13.7), xytext=(1,12.5),
        arrowprops=dict(facecolor='blue', shrink=1))