require 'twitter'
require 'mongo'
include Mongo

# transforms the "json" hash into a hash of what we want
def transform(json)
    data = {
        :id         => json['id'],
        :created_at => Time.parse(json['created_at']),
        :text       => json['text'],
        :user       => {
            :id              => json['user']['id'],
            :name            => json['user']['name'],
            :screen_name     => json['user']['screen_name'],
            :utc_offset      => json['user']['utc_offset'],
            :created_at      => Time.parse(json['user']['created_at']),
            :followers_count => json['user']['followers_count'],
            :friends_count   => json['user']['friends_count']
        }
    }
    data[:coordinates]       = {
        :coordinates         => json['geo']['coordinates']
    } if not json['geo'].nil?
    data[:place]             = {
        :id                  => json['place']['id'],
        :country_code        => json['place']['country_code']
    } if not json['place'].nil?
    data[:place][:bounding_box] = {
        :coordinates         => json['place']['bounding_box']['coordinates']
    } if not json['place'].nil? and not json['place']['bounding_box'].nil?
    data[:retweeted_status]  = {
            :id              => json['retweeted_status']['id'],
            :created_at      => json['retweeted_status']['created_at'],
            :text            => json['retweeted_status']['text'],
            :user            => {
                :id          => json['retweeted_status']['user']['id']
            }
    } if not json['retweeted_status'].nil?
    data[:mentions] = json['entities']['user_mentions'].map do |el|
         {
             :screen_name => el['screen_name'],
             :id          => el['id']
         }
    end if not json['entities']['user_mentions'].nil?
    data[:hashtags] = json['entities']['hashtags'].map {|el| el['text']}
    return data
end
# load old tweets, reformat them, and save them.
old_addr = "127.0.0.1"
new_addr = "127.0.0.1"
old_db_name = "tweets"
new_db_name = "new_tweets"

old_db = Connection.new(old_addr).db(old_db_name)
new_db = Connection.new(new_addr).db(new_db_name)

old_collection_names = old_db.collection_names

old_collection_names.reject { |n| n == "system.indexes" }.each do | name |
    old_coll = old_db[name]
    new_coll = new_db[name]
    old_coll.find.each do | tweet_json |
        begin
            new_coll.insert(transform(tweet_json))
        rescue TypeError
            new_coll.insert(tweet_json)
        end
    end
end
