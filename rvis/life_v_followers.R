# x-axis lifespan, y-axis # of followers, size # of retweets
f <- "~/programming/ncsa/final_work/final/stats.csv"
users <- read.csv(f, header=TRUE, sep=",")
radius <- sqrt(users$amt / pi)
followers_thousands <- users$followers / 1000
lifespan_hours <- users$rel / 3600

symbols(lifespan_hours, followers_thousands, circles=radius, inches=0.55, fg="white", bg="red",
        xlab="Lifespan(hours)", ylab="Followers (thousands)")
text(lifespan_hours, followers_thousands, users$name, cex=0.5)