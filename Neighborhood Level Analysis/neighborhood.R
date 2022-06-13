##read home_ID file

library(data.table)
library(gmodels)
library(dplyr)
library(lubridate)

#queenanne <- c(331:359,384:404)
queenanne <- c(260:265,316:359,384:406,430:491)
westseattle <- c(676:703,729:742)

ID_TAZ <- data.table::fread('C:/Users/wangjx/Desktop/AlaskaProject/DATA/home/home201911_TAZ.csv')
ID_queenanne <- ID_TAZ$ID[ID_TAZ$TAZ %in% queenanne]
ID_westseattle <- ID_TAZ$ID[ID_TAZ$TAZ %in% westseattle]


##read trip files
setwd('F:/Data/Cuebiq_psrc_2019/processed/201911/trip')
L = list.files(path = ".", pattern = "trip_trip", all.files = FALSE,
               full.names = FALSE, recursive = FALSE,
               ignore.case = FALSE, include.dirs = FALSE, no.. = FALSE)

stay_queenanne <- data.frame()
stay_westseattle <- data.frame()

for (i in 1:length(L)){
  stay <- data.table::fread(L[i])
  stay = stay[stay$oID %in% c(ID_queenanne, ID_westseattle),]
  stay <- stay[stay$tt < 18000,]
  stay$day = floor(stay$dh_time/1000000)
  stay$hour = floor(stay$dh_time/10000) - 100*stay$day
  for (j in 1:nrow(stay)){
    if (stay$hour[j] < 3){
      stay$day[j] = stay$day[j] - 1
    }
  }
  temp_stay_queenanne <- stay[stay$oID %in% ID_queenanne,]
  temp_stay_westseattle <- stay[stay$oID %in% ID_westseattle,]
  stay_queenanne <- rbind(stay_queenanne,temp_stay_queenanne)
  stay_westseattle <- rbind(stay_westseattle,temp_stay_westseattle)
  print(i)
}


# two week separation
day1 <- seq(191102,191122)
week1 <- day1[1:7]
week2 <- day1[8:14]
week3 <- day1[15:21]

## read work locations
ID_work = fread('C:/Users/wangjx/Desktop/AWS/201911/trip/workplace_inferred112019.csv')
colnames(ID_work) <- c('ID','wlat','wlon')
ID_home <- data.table::fread('C:/Users/wangjx/Desktop/AWS/201911/trip/home_inferred112019.csv')[,1:3]
colnames(ID_home) <- c('ID','hlat','hlon')
ID_home_work <- merge(ID_home,ID_work,by='ID')

## Select users within certain neighborhoods
setwd('C:/Users/wangjx/Desktop/AWS/201911/result')
# define trip rate function
triprate_func <- function(data, day_list){
  trip_rate <- data.frame(x = NA, day = NA)
  for (i in 1:length(day_list)){
    tempdata <- data[data$day == day_list[i],]
    trip <- aggregate(tempdata$oID, list(ID=tempdata$oID),length)
    trip$day = day_list[i]
    trip_rate <- rbind(trip_rate,trip[,2:3])
  }
  return(aggregate(trip_rate$x,list(day=trip_rate$day),mean))
}

trip_rate_queen = triprate_func(stay_queenanne,day1)
trip_rate_west = triprate_func(stay_westseattle,day1)
plot(trip_rate_queen$x)

write.csv(trip_rate_queen,file='trip_rate_queen.csv',row.names = FALSE)
write.csv(trip_rate_west,file='trip_rate_west.csv',row.names = FALSE)

## define PMT function
PMT_func <- function(data, day_list){
  trip_PMT <- data.frame(x = NA, day = NA)
  for (i in 1:length(day_list)){
    tempdata <- data[data$day == day_list[i],]
    trip <- aggregate(tempdata$dis, list(ID=tempdata$oID),sum)
    trip$day = day_list[i]
    trip_PMT <- rbind(trip_PMT,trip[,2:3])
  }
  trip_PMT$x = trip_PMT$x/1609.3
  return(aggregate(trip_PMT$x,list(day=trip_PMT$day),mean))
}

PMT_queen = PMT_func(stay_queenanne, day1)
PMT_west = PMT_func(stay_queenanne, day1)

write.csv(PMT_queen,file='PMT_queen.csv',row.names = FALSE)
write.csv(PMT_west,file='PMT_west.csv',row.names = FALSE)

## define commute trip function (home-work trip)
commute_trip <- function(data, day_list, home_work){
  data$time <- data$start_t
  class(data$time) = c('POSIXt','POSIXct',tz="PST")
  data$minute <- 60*hour(data$time) + minute(data$time) + 1
  data <- merge(data,home_work,by.x='oID',by.y = 'ID')
  data <- data[which(data$olati==data$hlat & data$dlati==data$wlat),]
  com_trip <- data[which(data$day %in% day_list),]
  return(com_trip)
}

week1 <- day1[3:7]
week2 <- day1[10:14]
week3 <- day1[17:21]
week1_trip = commute_trip(stay_queenanne, week1, ID_home_work)
week2_trip = commute_trip(stay_queenanne, week2, ID_home_work)
week3_trip = commute_trip(stay_queenanne, week3, ID_home_work)


x_break <- seq(0,1440,30)
x1 <- cut(week1_trip$minute,breaks = x_break)
depart_time_1 <- data.frame(table(x1))
x2 <- cut(week2_trip$minute,breaks = x_break)
depart_time_2 <- data.frame(table(x2))
x3 <- cut(week3_trip$minute,breaks = x_break)
depart_time_3 <- data.frame(table(x3))

dp = cbind(depart_time_1, depart_time_2$Freq, depart_time_3$Freq)
colnames(dp) <- c('time','week1','week2','week3')

plot(dp$week1/sum(dp$week1),type = 'b', col='red')
lines(dp$week2/sum(dp$week2),col='green')
lines(dp$week3/sum(dp$week3),col='blue')

write.csv(dp, file='dp_queen.csv',row.names = FALSE)


## Pdefine function for commute duration
trips <- commute_trip(stay_queenanne, day, ID_home_work)
duration <- aggregate(trips$tt, list(day=trips$day), mean)
duration$x = duration$x/60
plot(duration$x, type='b')


write.csv(tt, file='commute_tt_WS.csv',row.names = FALSE)