# coding=utf-8

import tweepy
import re


def is_contest(tweet):
    """
    Guess if a tweet is a legit RT-to-win contest.
    """
    # Throw away "manual retweets" that match "RT @username"
    manual_retweet = re.compile('^RT:? @\S', re.IGNORECASE)
    if manual_retweet.match(tweet.text) is not None:
        return False

    # "username1 RT username2: blah blah blah"
    rt2 = re.compile('^\S+ RT \S+:', re.IGNORECASE)
    if rt2.match(tweet.text) is not None:
        return False

    rt3 = re.compile('RT \S+: ', re.IGNORECASE)
    if rt3.match(tweet.text) is not None:
        return False

    # Strip hash signs from hashtags
    text = tweet.text.replace('#', '')
    text = text.lower()

    # Require the phrase "to enter", "to win", or "for a chance"
    to_win = re.compile('to win')
    to_enter = re.compile('to enter')
    chance = re.compile('for a chance')
    if to_win.match(text) is None and to_enter.match(text) is None and chance.match(text) is None:
        return False

    # throw away anything that says "UK only" or "UK resident" or has a £ 
    uk = re.compile('uk only')
    uk2 = re.compile('uk resident')
    if u'£' in text or uk.match(text) is not None or uk2.match(text) is not None:
        return False

    # throw away people who announce they just entered the contest
    announce1 = re.compile("i('ve)? (just)? entered")
    announce2 = re.compile("i'm entering")
    if announce1.match(text) is not None or announce2.match(text) is not None:
        return False


    # throw away people campaigning for someone else to win a thing
    o1 = re.compile("needs? to win")
    o2 = re.compile("deserves? to win")
    if o1.match(text) is not None or o2.match(text) is not None:
        return False


    # throw away "click here"
    click1 = re.compile("click here")
    if click1.match(text) is not None:
        return False

    # Having run out of possible objections...
    return True
