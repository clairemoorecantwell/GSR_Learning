# 4 types of forms
# Bi, BE, Be  (high, mid, low respectively)
# 4 constraints: 
#	Agree-back-nonlocal: (ABN)
#	Agree-front-local:   (AFL)
#	Agree-front-nonhigh: (AFNL)
#	Agree-front-low:	 (AFLL)
#
#	Starting distribution:
#	Bi: .7 nak, .3 nek
#	BE: .5 .5
#	Be: .3 nak, .7 nek

# Generate 3000 forms, 1000 each, freq drawn from zipf (within each group)
n = 1000
library(zipfR)
ZM=lnre("zm",alpha=2/3,B=0.05)
z1 = as.numeric(rlnre(ZM,n=n))
z2 = as.numeric(rlnre(ZM,n=n))
z3 = as.numeric(rlnre(ZM,n=n))

filename = "toy_HE.txt"

dataset = matrix(c("input","lexicon","candidate","obs.prob","tab.prob","ABN","AFL","AFNL","AFLL"),1,9)

for(i in 1:n){
	dataset = rbind(dataset,c(paste("oi",as.character(i),"_nak",sep=""),"oi_nak","oi_nak",".7",as.character(z1[i]),"0","1","0","0"))
	dataset = rbind(dataset,c(paste("oi",as.character(i),"_nak",sep=""),"oi_nak","oi_nek",".3",as.character(z1[i]),"1","0","0","0"))
	dataset = rbind(dataset,c(paste("oE",as.character(i),"_nak",sep=""),"oE_nak","oE_nak",".5",as.character(z2[i]),"0","1","1","0"))
	dataset = rbind(dataset,c(paste("oE",as.character(i),"_nak",sep=""),"oE_nak","oE_nek",".5",as.character(z2[i]),"1","0","0","0"))
	dataset = rbind(dataset,c(paste("oe",as.character(i),"_nak",sep=""),"oe_nak","oe_nak",".3",as.character(z3[i]),"0","1","1","1"))
	dataset = rbind(dataset,c(paste("oe",as.character(i),"_nak",sep=""),"oe_nak","oe_nek",".7",as.character(z3[i]),"1","0","0","0"))
}
colnames(dataset) = dataset[1,]
dataset = dataset[2:length(dataset[,1]),]
write.table(dataset,filename,quote=FALSE,sep="\t",row.names=FALSE)
