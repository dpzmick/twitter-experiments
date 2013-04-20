# x-axis # of tweets by user, y-axis penetration
f <- "~/programming/ncsa/final_work/final/stats.csv"
users <- read.csv(f, header=TRUE, sep=",")
radius <- sqrt(users$amt / pi)
out_network_rt <- 1 - users$direct_percent

symbols(users$total_tweets, out_network_rt, circles=radius, inches=0.55, fg="white", bg="red",
        xlab="# of Tweets Posted by User", ylab="% Retweets Indirect")
text(users$total_tweets, out_network_rt, users$name, cex=0.5)