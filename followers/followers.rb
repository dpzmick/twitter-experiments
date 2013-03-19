require './db'
require 'logger'

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
        cursor = -1
        n.times do
            tputs "making a request for #{ids[i]}"
            begin
                fs = client.follower_ids(ids[i], {:cursor => cursor})
                cursor = fs.next_cursor
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

addr = "127.0.0.1"
_db = "followers"
n = 5

id_list = get_user_ids()
clients = CONFIG.map { | account, attrs | Twitter::Client.new(attrs) }
conn = Connection.new(addr).db(_db)
LOG = Logger.new('logs/logfile.log', 10, 1024000)

slice_length = (id_list.length / clients.length.to_f).ceil
threads = []
client = 0
id_list.each_slice(slice_length) do | slice |
    threads << Thread.new { threaded_fetch(slice, clients[client], n, conn) }
    client = (client + 1) % clients.length
end
threads.map { |t| t.join }
