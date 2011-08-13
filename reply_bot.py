import random
import shelve
import tweepy

api = tweepy.API()

bot_configs = [
    {
    'bot_name' : 'snack_bot', # if bot is on a list it watches, this should be name of bot to avoid infinite loops
    'timelines' :
        [ # assumes param lists are unique. If ever not unique, we'll need to work func name into tweet_id_key
        {'func': api.list_timeline, 'params': ('username', 'listname')},
        {'func': api.user_timeline, 'params': ('username',)}
        ],
    'keywords' : ['keyword',],
    'replies' : ["witty retort", "etc etc etc",],
    'oauth_info' : ['consumer_key', 'consumer_secret', 'access_key', 'access_secret'],
    }
]

TWEET_ID_SHELF = 'reply_bot_tweet_ids'

for config in bot_configs:
    bot_name = config.get('bot_name').lower()
    for timeline in config.get('timelines'):
        args = timeline.get('params')
        tweet_id_key = '%s_%s' % (bot_name, ''.join(['%s' % param for param in args]))
        timeline_func = timeline.get('func')
        kwargs = {}
        tweet_id_shelf = shelve.open(TWEET_ID_SHELF)
        try:
            since_id = tweet_id_shelf.get(tweet_id_key)
        finally:
            tweet_id_shelf.close()
        if since_id:
            kwargs = {'since_id': since_id}
        tweets = timeline_func(*args, **kwargs)
        if tweets:
            tweet_id_shelf = shelve.open(TWEET_ID_SHELF)
            try:
                tweet_id_shelf[tweet_id_key] = tweets[0].id
            finally:
                tweet_id_shelf.close()
            for tweet in tweets:
                for word in config.get('keywords'):
                    if tweet.text.find(word) > -1 and tweet.author.screen_name.lower() != bot_name:
                        replies = config.get('replies')
                        oauth_info = config.get('oauth_info')
                        auth = tweepy.OAuthHandler(oauth_info[0], oauth_info[1])
                        auth.set_access_token(oauth_info[2], oauth_info[3])
                        reply_api = tweepy.API(auth)
                        reply = '@%s %s' % (tweet.author.screen_name, random.choice(replies))
                        reply_api.update_status(reply, in_reply_to_status_id=tweet.id)
                        break