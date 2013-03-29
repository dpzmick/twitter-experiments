# uses many accounts to try and get followers for a single user.
require './db'
require 'logger'
require 'typhoeus'
require 'typhoeus/adapters/faraday'

# makes a single request to twitter api and stores results, returns next cursor
def fetch(id, client, conn, cursor, wait_time)
    puts "making a request for #{id} cursor: #{cursor}"
    begin
        fs = client.follower_ids(id, {:cursor => cursor})
        store(fs.ids, id, conn)
        puts "Sleeping, length was #{fs.ids.length}"
        sleep(wait_time)
    rescue Twitter::Error::TooManyRequests => e
        puts "Rate limit exceeded, sleeping for #{e.rate_limit.reset_in}"
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
    puts "Writing to database"
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

addr = "141.142.226.111"
_db = "followers"
LOG = Logger.new('logs_single/logfile.log', 10, 1024000)

id = 14230524
clients = CONFIG.map { |acc, attrs | mk_twit_client(CONFIG[acc]) }
conn = Connection.new(addr, :pool_size => 5, :pool_timeout => 5).db(_db)

cursor = 1427173982606957864
cursor = -1
wait_time = 60 / clients.length

c = 0
while cursor != 0
    puts "c:#{c}"
    before = conn[id.to_s].count 
    cursor = fetch(id, clients[c], conn, cursor, wait_time)
    puts "Gained: #{conn[id.to_s].count - before}"
    c = (c + 1) % clients.length
end
