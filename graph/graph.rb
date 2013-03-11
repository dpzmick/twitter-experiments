require './config'
require 'twitter'


Twitter.configure do |config|
  config.consumer_key       = Conf::CONSUMER_KEY
  config.consumer_secret    = Conf::CONSUMER_SECRET
  config.oauth_token        = Conf::OAUTH_TOKEN
  config.oauth_token_secret = Conf::OAUTH_TOKEN_SECRET
end

def dputs(val)
    if DEBUG
        puts val
    end
end

def pretty_sleep(label, time)
    flag = true
    print label
    $stdout.flush
    time.times do |t|
        if flag
            print "#{time - t}"
            flag = !flag
        else
            print "."
            flag = !flag
        end
        $stdout.flush
        sleep(1)
    end
    puts ""
end

#MY_ID = Twitter.user['id']
# MY_ID = 14080233
MY_ID = 813286 # obama
DEBUG = true

def load_followers(id=MY_ID)
    # try and load from cache, if cache outdated or doesn't exist, reload data.
    if File.exist?("in_progress/in_#{id}")
        puts "SKIPPING #{id}"
        return nil
    end
    f = File.new("in_progress/in_#{id}", "w+")
    f.close

    followers = []
    if File.exists?("cache/followers_#{id}")
        followers = load_cache_followers(id)
    else
        followers = load_api_followers(id)
        cache_followers(followers, id)
    end

    File.delete("in_progress/in_#{id}")

    return followers
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
    dputs "Loading followers for #{id} from cache"
    file = File.open("cache/followers_#{id}")
    followers = []
    file.each do |line|
        followers << Integer(line)
    end
    return followers
end
def hasIncomplete(id)
    return File.exist?("incomplete/#{id}")
end
def loadIncomplete(id)
    f = File.open("incomplete/#{id}")
    # all lines are follower ids, until line "cursor:<cursor value>" (last line)
    followers = []
    cursor = "-1"
    f.each do |line|
        begin
            followers << Integer(line)
        rescue ArgumentError
            cursor = Integer(line.split(':')[1])
        end
    end
    f.close()
    return {:followers => followers, :cursor => cursor}
end
# returns time taken to store file
def storeIncomplete(followers, cursor, id)
    start = Time.now
    f = File.open("incomplete/#{id}", 'w+')
    followers.each do |follower|
        f.puts(follower)
    end
    f.puts("cursor:#{cursor}")
    f.close()
    return Time.now - start
end
def load_api_followers(id)
    dputs "Loading followers for #{id} from API @ #{Time.now}"
    followers = []
    begin
        if hasIncomplete(id)
            data = loadIncomplete(id)
            followers += data[:followers]
            cursor = data[:cursor]
        else
            cursor = -1
        end
        while cursor != 0 do
            dputs "\tMaking request to API, cursor: #{cursor}, time: #{Time.now}"
            fs = Twitter.follower_ids(id, {:cursor => cursor})
            cursor = fs.next_cursor
            followers += fs.ids

            dputs "\tStoring in temp"
            elapsed_time = storeIncomplete(followers, cursor, id)
            pretty_sleep("\tAvoiding rate limit: ", Integer(60 - elapsed_time))

        end
    rescue Twitter::Error::Unauthorized
        puts "Failed to get user's information, skipping."
        return nil
    rescue Twitter::Error::TooManyRequests => error
        puts "\t Rate limit exceeded, sleeping for #{error.rate_limit.reset_in}"
        sleep error.rate_limit.reset_in
        retry
    rescue Exception => error
        puts "An error occured: #{error}"
    end
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

# this is gross
# TODO: fix this.
def another_pass(h_old)
    h = {}
    h_old.each_key do |key|
        h[key] = h_old[key]
        h_old[key].each do |id|
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

def csv(h)
    puts "Writing to CSV file"
    f = File.new('out.csv', 'w+')
    h.each_pair do |id, ids|
        ids.each do |id1|
            f.puts("#{id},#{id1}")
        end
    end

    f.close
end

h = follower_graph_of_depth(2)
csv(h)
