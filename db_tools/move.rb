require 'mongo'
include Mongo

old_addr = '66.228.60.19'
new_addr = '141.142.226.111'

_db = 'new_tweets'
n_db = 'tweets'
collection = '813286'

old = Connection.new(old_addr).db(_db)[collection]
new = Connection.new(new_addr).db(n_db)[collection]

count = 0
old.find().each do | element |
    begin
        count += 1
        new.insert(element, :continue_on_error => true)
        if count % 100 == 0
            puts count
        end
    rescue Mongo::OperationFailure => e
        if not e.error_code == 11000
            raise e
        else
            puts "ignoring duplicate"
        end
    end
end
