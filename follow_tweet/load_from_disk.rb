# load data from (foolish) file based data store and into mongo
require 'twitter'
require 'mongo'
include Mongo

folder = "data/428333_304862679095451648"
id = 428333

db = Connection.new('66.228.60.19').db('followed_tweets')

storage = db.collection(id.to_s)

Dir.foreach(folder) do |fname|
    next if fname == '.' or fname == '..'
    puts "loading #{fname}"
    f = File.open(folder + "/" + fname)
    obj = Marshal.load(f)
    storage.insert(obj.to_hash)
    f.close
end
