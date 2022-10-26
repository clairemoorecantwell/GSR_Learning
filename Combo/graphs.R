setwd("C:/Users/moore-cantwell/GSRs/Combo")
data = read.table("weights.txt")
n=length(data$V1)
plot(1:n,data$V1,type="l")
plot(1:n,data$V2,type="l",col="red")
plot(1:n,data$V3,type="l",col="red")


data = read.table("PFCs.txt",header=TRUE)
summary(data)
n = length(data[,1])
plot(1:n,data$a_a,type="l")
# Always voiced
plot(1:n,data$pab21_pab,type="l")
# Always voiceless
plot(1:n,data$pab6_pap,type="l")
# Alternator
plot(1:n,data$pab16_pab,type="l")
plot(1:n,data$pab16_pap,type="l")
