# x-axis DF %, y-axis followers, size # of retweets
users <- read.csv("stats.csv", header=TRUE, sep=",")
radius <- sqrt(users$amt / pi)
followers_thousands <- users$followers / 1000
out_network_rt <- 1 - users$direct_percent

symbols(followers_thousands, out_network_rt, circles=radius, inches=0.55, fg="white", bg="red",
        xlab="Followers (thousands)", ylab="% Retweets Indirect")
text(followers_thousands, out_network_rt, users$name, cex=0.5)