library(gridExtra)
scale <- function(x) {
  (x - min(x)) / (max(x) - min(x))
}

# set up data
data <- read.csv("~/programming/ncsa/vis/new_stat/americancancer.csv")
clean <- data[data$REL != 0,]
sorted <- clean[order(clean$TOT_RT),]

# no need to clean tot
life <- sorted$REL / 3600
perc <- 1 - sorted$RT_PERCENT

# start doing color stuff
scaled_perc <- scale(perc)
cols_fun <- colorRamp(cm.colors(256))
cols <- rgb(cols_fun(scaled_perc), maxColorValue=256)

# make a plot!
#barplot(life, col=cols, horiz=TRUE, names.arg=sorted$TOT_RT,
#        xlab="Lifespan (Hours)", ylab="# of Retweets")

#plot(life, clean$TOT_RT, cex=0, bty="n",
#     xlab="Relevance (Hours)", ylab="Total Retweets")
#rect(par("usr")[1], par("usr")[3], par("usr")[2], par("usr")[4], col = "grey")
#segments(x0=0, y0=clean$TOT_RT, x1=life, y1=clean$TOT_RT, col=cols, lwd=5)

grid.table(head(clean))