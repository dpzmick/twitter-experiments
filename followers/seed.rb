require 'mongo'
include Mongo

id = "813286"
coll = Connection.new('127.0.0.1').db('followers')[id]
file = File.open("followers_#{id}")
file.each do |line|
    begin
        coll.insert( { '_id' => Integer(line) }, :continue_on_error => true)
    rescue
    end
end
