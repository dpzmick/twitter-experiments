# Makes a twitter client for each availible account
# Assigns a couple of ids to each client
# Each client makes n requests for a client, and moves to next one
# Useful to try and maintain a decent sample of followers

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

def threaded_fetch(ids, client, n, conn)
    Thread.current['id'] = ids.to_s
    fetch(ids, client, n, conn)
end

# Fetches follower ids from ids using client
# makes n requests per id before moving to the next one.
def fetch(ids, client, n, conn)
    i = 0
    loop do
        cur = conn['cursors'].find_one({'_id' => ids[i]})
        if cur.nil? or cur['cursor'] == 0
            cursor = -1
        else
            tputs "Using fetched cursor #{cur['cursor']}"
            cursor = cur['cursor']
        end
        n.times do
            tputs "making a request for #{ids[i]}"
            begin
                fs = client.follower_ids(ids[i], {:cursor => cursor})
                cursor = fs.next_cursor
                if cursor == 0
                    tputs "Sleeping, then breaking (cursor was 0)"
                    sleep(60)
                    break
                end
                store(fs.ids, ids[i], conn)
                tputs "Sleeping"
                sleep(60)
            rescue Twitter::Error::TooManyRequests => e
                tputs "Rate limit exceeded, sleeping for #{e.rate_limit.reset_in}"
                sleep(e.rate_limit.reset_in) 
            end

            if cursor == 0
                break
            end
        end
        i = (i + 1) % ids.length
    end
end

# stores ids in mongodb if they are not already there.
# Each user_id will be its own collection containing the ids of users following
# them. These ids will be stored in minimal mongo documents using the mongo _id
# field to hold the follower's id.
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

addr = "127.0.0.1"
_db = "followers"
n = 5

id_list = get_user_ids()
clients = CONFIG.map { | account, attrs | mk_twit_client(CONFIG[account]) }
conn = Connection.new(addr, :pool_size => 5, :pool_timeout => 5).db(_db)
LOG = Logger.new('logs/logfile.log', 10, 1024000)

slice_length = (id_list.length / clients.length.to_f).ceil
threads = []
client = 0
id_list.each_slice(slice_length) do | slice |
    threads << Thread.new { threaded_fetch(slice, clients[client], n, conn) }
    client = (client + 1) % clients.length
end
threads.map { |t| t.join }
