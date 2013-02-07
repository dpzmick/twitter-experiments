require './config'
require 'twitter'
require 'tweetstream'
require 'json'
require 'mongo'
include Mongo

db = Connection.new.db('tweets')
ftweets = db.collection('ftweets')

Twitter.configure do |config|
  config.consumer_key = Conf::CONSUMER_KEY
  config.consumer_secret = Conf::CONSUMER_SECRET
  config.oauth_token = Conf::OAUTH_TOKEN
  config.oauth_token_secret = Conf::OAUTH_TOKEN_SECRET
end

def load_friends()
    # try and load from cache, if cache outdated or doesn't exist, reload data.
    friends = []
    t = Time.now
    if File.exists?('cache/friends') and (File.open('cache/friends').mtime - t).to_i < 3600
        puts "Loading friends from cache"
        friends = load_cache_friends
    else
        puts "Loading friends from api"
        friends = load_api_friends
        cache_friends(friends)
    end
    return friends
end
def cache_friends(friends)
    f = File.new('cache/friends', 'w+')
    friends.each do |friend|
        f.puts(friend)
    end
    f.close
end
def load_cache_friends()
    friends = []
    file = File.open('cache/friends')
    file.each do |line|
        friends << Integer(line)
    end
    return friends
end
def load_api_friends()
    friends = []
    Twitter.friends.each do |friend|
        friends << friend.id
    end
    return friends
end


# gets people I follow
puts "I Follow:"
puts "-----------------------"
friends = load_friends

friends.each do |friend|
    puts friend
end


# live stream of people that I follow.
puts ""
puts "Attempting to stream from my followers"

TweetStream.configure do |config|
  config.consumer_key       = Conf::CONSUMER_KEY
  config.consumer_secret    = Conf::CONSUMER_SECRET
  config.oauth_token        = Conf::OAUTH_TOKEN
  config.oauth_token_secret = Conf::OAUTH_TOKEN_SECRET
  config.auth_method        = :oauth
end

# Use 'follow' to follow a group of user ids (integers, not screen names)
TweetStream::Client.new.follow(friends) do |status|
    puts "#{status.text}"
end
