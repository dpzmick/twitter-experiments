require './config'
require 'tweetstream'

DEBUG = true

TweetStream.configure do |config|
  config.consumer_key       = Conf::CONSUMER_KEY
  config.consumer_secret    = Conf::CONSUMER_SECRET
  config.oauth_token        = Conf::OAUTH_TOKEN
  config.oauth_token_secret = Conf::OAUTH_TOKEN_SECRET
  config.auth_method        = :oauth
end

def dputs(val)
    if DEBUG
        puts val
    end
end
def save_tweet(tweet, directory)
    cache = File.open("#{directory}/#{tweet.id}", 'w')
    cache.write(Marshal.dump(tweet))
    cache.close
end

# a couple of ids
ladygaga_id = 14230524
barackObama_id = 813286
dpzmick_id = 14080233
notzmick_id = 1155825132

id = notzmick_id
tracked_tweet = nil
directory_name = nil
TweetStream::Client.new.follow(id) do |status|
    dputs "#{status.text}"
    if tracked_tweet.nil?
        if status.user.id == id
            tracked_tweet = status
            dputs "\tTweet to track now set"
            dputs "\tCreating directory for retweet storage"
            directory_name = "#{id}_#{tracked_tweet.id}"
            Dir::mkdir(directory_name)
            dputs "\tSaving original tweet"
            save_tweet(status, directory_name)
        end
    else
        if status.retweet? and status.text.include?(tracked_tweet.text)
            dputs "\tGot a retweet of tracked tweet, saving"
            save_tweet(status, directory_name)
        end
    end
end
