data <- read.csv("~/programming/ncsa/vis/new_stat/BarackObama.csv")
clean <- data[data$REL != 0,]
xs <- clean$REL / 3600
ys <- clean$TOT_RT
perc <- 1 - clean$RT_PERCENT
color_number <- 3
max_perc <- max(perc)
colors <- rev(heat.colors(color_number))[(perc * color_number) / max_perc]
radius <-sqrt(clean$RT_PERCENT/ pi)
plot(xs, ys, cex=0, bty="n", xlab="Relevance (Hours)", ylab="Total Retweets")
segments(x0=0, y0=ys, x1=xs, y1=ys, col=colors)