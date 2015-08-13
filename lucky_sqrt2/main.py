#!/usr/bin/env python2
# -*- coding: utf-8 -*- #

from twitterbot import TwitterBot
import yaml
import random

class MyTwitterBot(TwitterBot):
    def bot_init(self):
        """
        Initialize and configure your bot!

        Use this function to set options and initialize your own custom bot
        state (if any).
        """

        # REQUIRED: LOGIN DETAILS! Load these from file. #
        with self.config['storage'].read('config.yaml') as f:
            tokens = yaml.load(f)

        self.config.update(tokens)


        ######################################
        # SEMI-OPTIONAL: OTHER CONFIG STUFF! #
        ######################################

        # how often to tweet, in seconds
        self.config['tweet_interval'] = None    # default: 30 minutes

        # use this to define a (min, max) random range of how often to tweet
        # e.g., self.config['tweet_interval_range'] = (5*60, 10*60) # tweets every 5-10 minutes
        self.config['tweet_interval_range'] = (5*60*60, 10*60*60)
        # only reply to tweets that specifically mention the bot
        self.config['reply_direct_mention_only'] = False
        # only include bot followers (and original tweeter) in @-replies
        self.config['reply_followers_only'] = False
        # fav any tweets that mention this bot?
        self.config['autofav_mentions'] = False
        # fav any tweets containing these keywords?
        self.config['autofav_keywords'] = []
        # follow back all followers?
        self.config['autofollow'] = False


        ###########################################
        # CUSTOM: your bot's own state variables! #
        ###########################################
        
        # If you'd like to save variables with the bot's state, use the
        # self.state dictionary. These will only be initialized if the bot is
        # not loading a previous saved state.

        # self.state['butt_counter'] = 0

        # You can also add custom functions that run at regular intervals
        # using self.register_custom_handler(function, interval).
        #
        # For instance, if your normal timeline tweet interval is every 30
        # minutes, but you'd also like to post something different every 24
        # hours, you would implement self.my_function and add the following
        # line here:
        
        # self.register_custom_handler(self.my_function, 60 * 60 * 24)


    def on_scheduled_tweet(self):
        """
        Make a public tweet to the bot's own timeline.
        It's up to you to ensure that it's less than 140 characters.
        Set tweet frequency in seconds with TWEET_INTERVAL in config.py.
        """
        # text = function_that_returns_a_string_goes_here()
        # self.post_tweet(text)
        luck_texts = ["Fingers crossed.", "Where's my rabbit foot?", "My lucky number is irrational.", 
                    "A sweepstakes a day brings some junk to your door.", "Garlic protects from evil spirits."]
        self.post_tweet(status=random.choice(luck_texts))
        return 1
        

    def on_mention(self, tweet, prefix):
        """
        Defines actions to take when a mention is received.

        tweet - a tweepy.Status object. You can access the text with
        tweet.text

        prefix - the @-mentions for this reply. No need to include this in the
        reply string; it's provided so you can use it to make sure the value
        you return is within the 140 character limit with this.

        It's up to you to ensure that the prefix and tweet are less than 140
        characters.

        When calling post_tweet, you MUST include reply_to=tweet, or
        Twitter won't count it as a reply.
        """

        exclamations = ['Sweet', 'Awesome', 'Wahoo', 'OMG', 'Hooray', 'Hoorah', 
                        'Wow', 'ZOMGZ', 'Huzzah', 'Holy cannoli', 'Woohoo' ]
        text = random.choice(exclamations) + '!'*random.randrange(1,4) 
       
        self.post_tweet(status=text, reply_to=tweet) 

        return 1


    def on_timeline(self, tweet, prefix):
        """
        Defines actions to take on a timeline tweet.

        tweet - a tweepy.Status object. You can access the text with
        tweet.text

        prefix - the @-mentions for this reply. No need to include this in the
        reply string; it's provided so you can use it to make sure the value
        you return is within the 140 character limit with this.

        It's up to you to ensure that the prefix and tweet are less than 140
        characters.

        When calling post_tweet, you MUST include reply_to=tweet, or
        Twitter won't count it as a reply.
        """
        # text = function_that_returns_a_string_goes_here()
        # prefixed_text = prefix + ' ' + text
        # self.post_tweet(prefix + ' ' + text, reply_to=tweet)

        # call this to fav the tweet!
        # if something:
        #     self.favorite_tweet(tweet)
        pass


if __name__ == '__main__':
    
    # get home directory from command line argument
    if len(sys.argv) > 1:
        rootdir = sys.argv[1]
    else:
        rootdir = './'

    bot = MyTwitterBot(home=rootdir)
    bot.run()
