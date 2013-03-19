# this file defines how things will be stored in mongo and provides helper
# functions for database operation.

require 'mongo'
require 'twitter'
require './config'
include Mongo

# "MODEL"
# Takes a Twitter::Tweet object an returns a hash consiting of the attributes I
# care about
def repr_tweet(tweet)
    data = {
        :id          => tweet.id,
        :created_at  => tweet.created_at,
        :text        => tweet.text,
        :user        => {
            :id              => tweet.user.id,
            :name            => tweet.user.name,
            :screen_name     => tweet.user.screen_name,
            :utc_offset      => tweet.user.utc_offset,
            :created_at      => tweet.user.created_at,
            :followers_count => tweet.user.followers_count,
            :friends_count   => tweet.user.friends_count
        }
    }
    data[:coordinates]       = {
        :coordinates         => tweet.geo.coordinates
    } if not tweet.geo.nil?
    data[:place]             = {
        :id                  => tweet.place.id,
        :country_code        => tweet.place.country_code
    } if not tweet.place.nil?
    data[:place][:bounding_box] = {
        :coordinates         => tweet.place.bounding_box.coordinates
    } if not tweet.place.nil? and tweet.place.bounding_box.nil?
    data[:retweeted_status]  = {
            :id              => tweet.retweeted_status.id,
            :created_at      => tweet.retweeted_status.created_at,
            :text            => tweet.retweeted_status.text,
            :user            => {
                :id          => tweet.retweeted_status.user.id
            }
    } if not tweet.retweeted_status.nil?
    data[:mentions] = tweet.user_mentions.map do |el|
        {
            :screen_name => el.screen_name,
            :id          => el.id
        }
    end if not tweet.user_mentions.nil?
    data[:hashtags] = tweet.hashtags.map {|el| el.text} if not tweet.hashtags.nil?
    return data
end

# figure out which account a Twitter::Tweet is associated with.
# tweets will be:
#   1) From account in list
#   2) A retweet of a tweet by someone in list
#   3) A mention of someone in list
def tweet_owners(tweet, options)
    posterID = tweet.user.id 
    originalPosterID =
        tweet.retweeted_status.user.id if not tweet.retweeted_status.nil?
    mentionIDs = 
        tweet.user_mentions.map {|mention| mention.id} if not tweet.user_mentions.nil?
    if options.include?(posterID)
        return [posterID]
    elsif options.include?(originalPosterID)
        return [originalPosterID]
    elsif not (options & mentionIDs).empty?
        return options & mentionIDs
    else
        raise "Error getting tweet's owner"
    end
end

# CONNECTION
def set_up_db(addr="66.228.60.19", _db="tweets")
   Connection.new(addr).db(_db)
end

def get_collection(db, id)
    db.collection(id.to_s)
end

# IO
# Returns an array of the ids extracted from a file formatted:
# screenname: id
# screename: id
def get_user_ids(fname="../id_list")
    file = File.open(fname, "r")
    ids = []
    file.each do |line|
        ids += [Integer(line.split(":")[1].strip())]
    end
    file.close()    
    return ids
end
