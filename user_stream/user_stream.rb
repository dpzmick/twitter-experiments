# store all tweets relating to a user in a collection in mongo
# Does nothing more, nothing less.

require './db'
require 'tweetstream'
require 'pp'
include Mongo

def print_tracker(tracker)
    longest = 
        (tracker.keys.max { |a, b| a.to_s.length <=> b.to_s.length }).to_s.length
    puts Time.now
    tracker.each do |id, count|
        printf("%-#{longest + 2}d %d\n", id, count)
    end
    puts 
end

logger1 = Logger.new('logs/logfile.log', 10, 1024000)
logger2 = Logger.new('logs/tweets', 10, 102400)

TweetStream.configure do |config|
  config.consumer_key       = Conf::CONSUMER_KEY
  config.consumer_secret    = Conf::CONSUMER_SECRET
  config.oauth_token        = Conf::OAUTH_TOKEN
  config.oauth_token_secret = Conf::OAUTH_TOKEN_SECRET
  config.auth_method        = :oauth
end

puts "Connection to database and getting reading user id list"
db = set_up_db()
ids = get_user_ids()
tracker = Hash[ids.collect {|id| [id, 0]}]

puts "Starting streaming API"

TweetStream::Client.new.follow(ids) do |status|
    begin
        owners = tweet_owners(status, ids)
        repr = repr_tweet(status)
        owners.each do |owner| 
            get_collection(db, owner).insert(repr)
            tracker[owner] += 1
            logger2.info "\n\t#{status.text} \n\towner: #{owner}"
        end
        print_tracker(tracker)
    rescue Exception => error
        logger1.error "\n\t#{error}\n\t#{status.attrs}"
        puts error
    end
end
