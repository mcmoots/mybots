#!/usr/bin/env python2
# -*- coding: utf-8 -*- #

import twitterbot
import yaml
import random
import sys
import re
import time
import identify_contests as ic
import tweepy

class MyTwitterBot(twitterbot.TwitterBot):
    def bot_init(self, home='./'):
        """
        Initialize and configure your bot!

        Use this function to set options and initialize your own custom bot
        state (if any).
        """

        # REQUIRED: LOGIN DETAILS! Load these from file. #
        with self.config['storage'].read('config.yaml') as f:
            tokens = yaml.load(f)

        self.config.update(tokens)

        # SEMI-OPTIONAL: OTHER CONFIG STUFF! #
        self.config['tweet_interval'] = 5*60*60   # default: 30 minutes
        self.config['tweet_interval_range'] = (5*60*60, 10*60*60)
        self.config['reply_direct_mention_only'] = False
        self.config['reply_followers_only'] = False
        self.config['autofav_mentions'] = True
        self.config['autofav_keywords'] = []
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

        self.register_custom_handler(self.drop_old_follows, 12*60*60)
        self.register_custom_handler(self.reset_follow_count, 3*60*60)
        self.state['recent_follow_count'] = 0


    def bot_init2(self):
        """
        Super hacky. Call this in the bot init, after the API has been set up.
        """

        # load the ignored users list
        self.ignored_users = []
        for user in tweepy.Cursor(self.api.list_members, 'luckysqrt2', 'ignore').items():
            self.ignored_users.append(user.id)

        # Start the streaming API!
        self.listener = twitterbot.BotStreamListener(method=self.on_stream)
        self.stream = tweepy.Stream(auth=self.api.auth, listener=self.listener)
        keyphrases = ["RT to win", "RT to enter", "retweet to win", "retweet to enter"]

        self.stream.filter(track=keyphrases, async=True)


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
        self.post_tweet(random.choice(luck_texts))
        

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

        winning_words = ['won', 'winner', 'congrats', 'congratulations', 'prize', 'win']
        warnings = ['fake', 'scam', 'cheat', 'fraud', 'hoax', 'sucker']
        exclamations = ['Sweet', 'Awesome', 'Wahoo', 'OMG', 'Hooray', 'Hoorah', 
                        'Wow', 'ZOMGZ', 'Huzzah', 'Holy cannoli', 'Woohoo', 'Woot' ]

        if sum([w in tweet.text.lower() for w in winning_words]) > 0:
            text = random.choice(exclamations) + '!'*random.randrange(1,4)
        
        elif sum([w in tweet.text.lower() for w in warnings]) > 0:
            text = "I'm just a bot, I don't have to be very smart."

        else:
            text = "Sorry, interactivity hasn't really been implemented yet."

        text = prefix + ' ' + text       

        self.post_tweet(text, reply_to=tweet) 


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


    def on_stream(self, tweet):
        """
        Defines action to take when streaming API returns a status obj. 
        """
        # Check if it's really a contest
        if not ic.is_contest(tweet):
            return None

        # Check the ignored users list
        if tweet.user.id in self.ignored_users:
            return None

        # Okay, cool. RT, follow, and fav.
        self.api.retweet(tweet.id)
        self.api.create_favorite(tweet.id)

        # If we've been following a lot of ppl lately, require the word "follow" in the tweet.
        if self.state['recent_follow_count'] < 12:
            self.api.create_friendship(user_id=tweet.user.id)
        elif self.state['recent_follow_count'] < 20:
            follow = re.compile('follow', re.IGNORECASE)
            FRT = re.compile('F ?[+&] ?RT', re.IGNORECASE)
            RTF = re.compile('RT ?[+&] ?F', re.IGNORECASE)
            if (follow.match(tweet.text) is not None 
                or FRT.match(tweet.text) is not None 
                or RTF.match(tweet.text) is not None):
                self.api.create_friendship(user_id=tweet.user.id)
        else:
            # whoa yr following too fast, slow down!
            time.sleep(5*60)


    def drop_old_follows(self):
        """
        Unfollow the oldest-followed accounts (except those on a safe list).
        """
        max_following = random.randrange(1910,1960)
        
        safe_users = []
        for user in tweepy.Cursor(self.api.list_members, 'luckysqrt2', 'cool-brands').items():
            safe_users.append(user.id)

        # the FIRST objs in the friend list are the most recently followed accounts.
        # Drop from the LAST list items, if they are not in safe list.
        
        following = self.api.friends_ids()
        num_following = len(following)
        # loop from end to beginning of user list
        i = -1
        while num_following > max_following:
            user = following[i]
            if user in safe_users:
                pass
            else:
                self.api.destroy_friendship(user_id=user)
                num_following += -1
            i += -1
            # break if we loop back around to the beginning.
            # TODO: This means the safe users list is too long & requires human action!
            if i + len(following) == 0:
                break
   
 
    def reset_follow_count(self):
        self.state['recent_follow_count'] = 0 


if __name__ == '__main__':
    
    # get home directory from command line argument
    if len(sys.argv) > 1:
        rootdir = sys.argv[1]
    else:
        rootdir = './'

    bot = MyTwitterBot(home=rootdir)
    bot.run()
