# uses many accounts to try and get followers for a single user.
# For each account, a thread is started with a random, or -1 cursor and begins
# to get followers
# Useful to attempt to seed followers

require './db'
require 'logger'
require 'typhoeus'
require 'typhoeus/adapters/faraday'

# threaded puts
def tputs(str)
    # be paranoid about when things are printed
    str = "#{Thread.current['id']} : #{str}\n"
    puts str
    LOG.info str    
end
def threaded_fetch(id, client, conn, random_curr, name)
    Thread.current['id'] = name
    if random_curr
        cursor = ["14", "13"].sample
        cursor += Integer(Random.rand * 10**17).to_s
        cursor = Integer(cursor)
    else
        cursor = -1
    end
    tputs "Looping requests starting with cursor #{cursor}"
    loop do
        cursor = fetch(id, client, conn, cursor)
    end
end

# makes a single request to twitter api and stores results, returns next cursor
def fetch(id, client, conn, cursor)
    tputs "making a request for #{id} cursor: #{cursor}"
    begin
        fs = client.follower_ids(id, {:cursor => cursor})
        store(fs.ids, id, conn)
        tputs "Sleeping, length was #{fs.ids.length}"
        sleep(60)
    rescue Twitter::Error::TooManyRequests => e
        tputs "Rate limit exceeded, sleeping for #{e.rate_limit.reset_in}"
        sleep(e.rate_limit.reset_in) 
    end
    if fs.nil?
        return -1
    end
    return fs.next_cursor
end

# stores ids in mongodb if they are not already there.
# Each user_id will be its own collection containing the ids of users following
# them. These ids will be stored in minimal mongo documents using the mongo _id
# field tohold the follower's id.
def store(ids, user_id, conn)
    tputs "Writing to database"
    ids_doc = ids.inject([]) { | res, id | res << { '_id' => id } }
    begin
        conn[user_id.to_s].insert(ids_doc, :continue_on_error => true)
    rescue Mongo::OperationFailure => e
        if not e.error_code == 11000
             raise e
        end
    end
end

# make a twitter client with credentials given
def mk_twit_client(creds)
    Twitter.configure do |config|
        config.consumer_key = creds[:consumer_key]
        config.consumer_secret = creds[:consumer_secret]
        config.oauth_token = creds[:oauth_token]
        config.oauth_token_secret = creds[:oauth_token_secret]
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
    return Twitter::Client.new(:middleware => Faraday::Builder.new(&middleware))
end

# prints info every once and a while
def count_thread(id, conn)
    Thread.current['id'] = "INFO"
    n = 60
    loop do
        last = conn[id.to_s].count
        sleep(n)
        tputs "Gained #{conn[id.to_s].count - last} ids in the last #{n} seconds"
    end
end

addr = "127.0.0.1"
_db = "followers"
LOG = Logger.new('logs_single/logfile.log', 10, 1024000)

id = 813286
clients = CONFIG.map { |acc, attrs | mk_twit_client(CONFIG[acc]) }
conn = Connection.new(addr, :pool_size => 5, :pool_timeout => 5).db(_db)

threads = []
threads << Thread.new { threaded_fetch(id, clients[0], conn, false, 0) }
clients[1..clients.length].each_with_index do |client, index|
    threads << Thread.new { threaded_fetch(id, client, conn, true, index + 1) } 
end
threads << Thread.new { count_thread(id, conn) }
threads.map { |t| t.join }
