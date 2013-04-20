# x-axis lifespan, y-axis DF %, size # of retweets
f <- "~/programming/ncsa/final_work/final/stats.csv"
users <- read.csv(f, header=TRUE, sep=",")
radius <- sqrt(users$amt / pi)
lifespan_hours <- users$rel / 3600
out_network_rt <- 1 - users$direct_percent

symbols(lifespan_hours, out_network_rt, circles=radius, inches=0.55, fg="white", bg="red",
        xlab="Lifespan(hours)", ylab="% Indirect Follower Retweets")
text(lifespan_hours, out_network_rt, users$name, cex=0.5)