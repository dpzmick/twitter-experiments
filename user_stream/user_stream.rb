# store all tweets relating to a user in a collection in mongo
# Does nothing more, nothing less.

require './config'
require 'mongo'
require 'tweetstream'

include Mongo
DEBUG = true

db = Connection.new('66.228.60.19').db('tweets')

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

# a couple of ids
ladygaga_id = 14230524
barackObama_id = 813286
dpzmick_id = 14080233
notzmick_id = 1155825132
cnn_breaking_news_id = 428333

id = cnn_breaking_news_id
storage = db.collection(id.to_s)

TweetStream::Client.new.follow(id) do |status|
    dputs "#{status.text}"
    begin
        storage.insert(status.to_hash)
    rescue Exception => error
        puts error
    end
end
