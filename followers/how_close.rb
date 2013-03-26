# Aproximates how close we are to having a complete list of followers.

require 'twitter'
require './config'
require './db'

puts "Setting up"
Twitter.configure do |config|
    config.consumer_key = CONFIG[:dpzmick][:consumer_key]
    config.consumer_secret = CONFIG[:dpzmick][:consumer_secret]
    config.oauth_token = CONFIG[:dpzmick][:oauth_token]
    config.oauth_token_secret = CONFIG[:dpzmick][:oauth_token_secret]
end
middleware = Proc.new do |builder|
    builder.use Twitter::Request::MultipartWithFile
    builder.use Faraday::Request::Multipart
    builder.use Faraday::Request::UrlEncoded
    builder.use Twitter::Response::RaiseError, Twitter::Error::ClientError
    builder.use Twitter::Response::ParseJson
    builder.use Twitter::Response::RaiseError, Twitter::Error::ServerError
    builder.adapter :typhoeus
end
Twitter::Client.new(:middleware => Faraday::Builder.new(&middleware))

db = Connection.new('127.0.0.1').db('followers')

ids = get_user_ids()
needed_hash = {}

puts "Getting stuff from API"
ids.each do |id|
    needed_hash[id] = Twitter.user(id).followers_count
end

puts "Getting stuff from database"
have_hash = {}
ids.each do |id|
    have_hash[id] = db[id.to_s].count
end

needed_hash.each_key do |id|
    puts id 
    puts "\t#{(have_hash[id].to_f / needed_hash[id].to_f) * 100} %"
    puts "\tRemaining : #{needed_hash[id] - have_hash[id]}"
    requests = (needed_hash[id] - have_hash[id])/5000
    puts "\tETA: #{requests} requests"
    puts "\t     #{requests / 60} hours"
    puts "\t     #{requests / (60*24)} days"
end
