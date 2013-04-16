scale <- function(x) {
  (x - min(x)) / (max(x) - min(x))
}
screen_name <- "foxnews"
data <- read.csv(paste("~/programming/ncsa/vis/hash/", screen_name, ".csv", sep=""))
clean <- data[data$REL != 0,]
require("treemap")
indirect_retweet_percent <- 1 - clean$RT_PERCENT
area <- (clean$TOT_RT / 1000) * (clean$REL / 3600)

dat = data.frame(clean$ID_HASH, area, indirect_retweet_percent)

tmPlot(dat, index=c("clean.ID_HASH"), vSize="area", vColor="indirect_retweet_percent",
       fontsize.labels = 6, lowerbound.cex.labels=0, inflate.labels=TRUE,
       title = paste(screen_name, "'s Tweets"))