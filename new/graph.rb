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
$COUNTER = 0

def load_followers(id=MY_ID)
    # try and load from cache, if cache outdated or doesn't exist, reload data.
    followers = []
    if File.exists?("cache/followers_#{id}")
        puts "Loading followers from cache"
        followers = load_cache_followers(id)
    else
        puts "Loading followers from api"
        followers = load_api_followers(id)
        cache_friends(followers, id)
    end
    return friends
end
def cache_followers(followers, id)
    f = File.new("cache/followers_#{id}", 'w+')
    if followers.nil?
        return
    end
    followers.each do |follower|
        f.puts(follower)
    end
    f.close
end
def load_cache_followers(id)
    followers = []
    file = File.open("cache/followers_#{id}")
    file.each do |line|
        followers << Integer(line)
    end
    return followers
end
def load_api_followers(id)
    puts "\t sleeping to obey rate limit (#{$COUNTER})"
    sleep 180
    followers = []
    begin
        Twitter.followers_ids(id).each do |followers|
            followers << follower
        end
    rescue Twitter::Error::Unauthorized
        puts "CAN'T GET THIS USERS INFORMATION"
        return nil
    rescue Twitter::Error::TooManyRequests => error
        puts "\t Rate limit exceeded, sleeping"
        sleep error.rate_limit.reset_in
        retry
    end
    $COUNTER = $COUNTER + 1
    return followers
end

def follower_graph_of_depth(depth)
    h = {}
    h[MY_ID] = load_followers
    depth.times do
        h = another_pass(h)
    end
    return h
end

def left(h_old, h_new)
    left = 0
    h_old.each_pair do |id, ids|
        ids.each do |id1|
            if h_new[id1].nil?
                left = left + 1
            end
        end
    end
    return left
end

def another_pass(h_old)
    h = {}
    h_old.each_key do |key|
        h[key] = h_old[key]
        h_old[key].each do |id|
            puts "Have #{left(h_old, h)} left"
            if h_old[id].nil?
                f = load_followers(id)
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

##
##
##
## UBIGRAPH Vis happens here.
def vis(h)
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

    #h[19909160].each do |id|
    #    server.call("ubigraph.new_vertex_w_id", id)
    #    server.call("ubigraph.new_edge", 19909160, id)
    #end
end

def csv(h)
    f = File.new('out.csv', 'w+')
    h.each_pair do |id, ids|
        ids.each do |id1|
            f.puts("#{id},#{id1}")
        end
    end

    f.close
end

# gets people I follow and the people they follow
h = friend_graph_of_depth(2)
#csv(h)
# vis(h)
