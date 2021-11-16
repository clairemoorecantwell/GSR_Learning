x = seq(-10,10,by=0.1)
plot(x,(1/2)*x/sqrt(.1+x^2)+0.5,type='l')
points(x,(1/2)*x/sqrt(3+x^2)+0.5,type='l',col='blue')
points(x,(1/2)*x/sqrt(10+x^2)+0.5,type='l',col='green')
points(x,(1/2)*x/sqrt(20+x^2)+0.5,type='l',col='orange')
points(x,(1/2)*x/sqrt(40+x^2)+0.5,type='l',col='red')


x = -5
(1/2)*x/sqrt(1+x^2)+0.5
