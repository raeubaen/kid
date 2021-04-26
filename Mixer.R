I_0 <- -15.5    #mV   
Q_0 <- 18      #mV
I <- c(-19.0, -23.5, -16.5, -17, -17.3) - I_0         #mV
Q <- c(5.7, 23.6, 21.5, 20.9, 18.6) - Q_0            #mV
R <- sqrt(I^2 + Q^2)                 #mV
A <- c(9.6, 5.3, 0.960, 0.55, 1.08)*sqrt(2)      #mV        
dati.df <- data.frame(R, A)

#FIT
fit <- lm(formula = R ~ A, data = dati.df)
K <- coefficients(fit)
plot(A, R)
abline(fit)

