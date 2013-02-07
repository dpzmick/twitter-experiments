require './config'
require 'twitter'
require 'tweetstream'

Twitter.configure do |config|
  config.consumer_key = Conf::CONSUMER_KEY
  config.consumer_secret = Conf::CONSUMER_SECRET
  config.oauth_token = Conf::OAUTH_TOKEN
  config.oauth_token_secret = Conf::OAUTH_TOKEN_SECRET
end
#MY_ID = Twitter.user['id']
MY_ID = 14080233

def load_friends(id=MY_ID)
    # try and load from cache, if cache outdated or doesn't exist, reload data.
    friends = []
    t = Time.now
    if File.exists?("cache/friends_#{id}")
        puts "Loading friends from cache"
        friends = load_cache_friends(id)
    else
        puts "Loading friends from api"
        friends = load_api_friends(id)
        cache_friends(friends, id)
    end
    return friends
end
def cache_friends(friends, id)
    f = File.new("cache/friends_#{id}", 'w+')
    if friends.nil?
        return
    end
    friends.each do |friend|
        f.puts(friend)
    end
    f.close
end
def load_cache_friends(id)
    friends = []
    file = File.open("cache/friends_#{id}")
    file.each do |line|
        friends << Integer(line)
    end
    return friends
end
def load_api_friends(id)
    friends = []
    cursor = nil
    begin
        Twitter.friend_ids(id).each do |friend|
            friends << friend
        end
    rescue Twitter::Error::Unauthorized
        puts "CAN'T GET THIS USERS INFORMATION"
        return nil
    end
    puts "\t sleeping to obey rate limit"
    sleep 60
    return friends
end

def friend_graph_of_depth(depth)
    h = {}
    h[MY_ID] = load_friends
    depth.times do
        h = another_pass(h)
    end
    return h
end

def another_pass(h_old)
    h = {}
    h_old.each_key do |key|
        h[key] = h_old[key]
        h_old[key].each do |id|
            if h_old[id].nil?
                f = load_friends(id)
                if not f.nil?
                    h[id] = f
                end
            else
                h[id] = h_old[id]
            end
        end
    end
    return h
end
# gets people I follow and the people they follow
h = friend_graph_of_depth(1)

##
##
##
## UBIGRAPH Vis happens here.

require 'xmlrpc/client'
server = XMLRPC::Client.new2("http://127.0.0.1:20738/RPC2")
server.call("ubigraph.clear")

puts "Making roots"
h.each_pair do |id, ids|
    server.call("ubigraph.new_vertex_w_id", id)
end

server.call("ubigraph.set_vertex_attribute", MY_ID, "size", "4")
server.call("ubigraph.set_vertex_attribute", MY_ID, "color", "#00FF00")

puts "Making connections"

puts h.keys
h[MY_ID].each do |id|
    server.call("ubigraph.new_vertex_w_id", id)
    server.call("ubigraph.new_edge", MY_ID, id)
end

# only using some accounts (jane and someone other one selected at random)
# because of speed

h[39011359].each do |id|
    server.call("ubigraph.new_vertex_w_id", id)
    server.call("ubigraph.new_edge", 39011359, id)
end

h[19909160].each do |id|
    server.call("ubigraph.new_vertex_w_id", id)
    server.call("ubigraph.new_edge", 19909160, id)
end
