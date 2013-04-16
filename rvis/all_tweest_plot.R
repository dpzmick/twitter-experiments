data <- read.csv
xs <- data$REL
ys <- data$TOT_RT
plot(xs, ys)
segments(x0=0, y0=ys, x1=xs, y1=ys, col="red")