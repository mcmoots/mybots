# coding=utf-8

import tweepy
import re


def is_contest(tweet):
    """
    Guess if a tweet is a legit RT-to-win contest.
    """
    # Throw away "manual retweets" that match "RT @username"
    manual_retweet = re.compile('^RT:? ?@\S', re.IGNORECASE)
    if manual_retweet.match(tweet.text) is not None:
        return (False, 'manual RT')

    # "username1 RT username2: blah blah blah"
    rt2 = re.compile('\S+ RT \S+:', re.IGNORECASE)
    if rt2.match(tweet.text) is not None:
        return (False, 'manual RT')

    rt3 = re.compile('^RT \S+: ', re.IGNORECASE)
    if rt3.match(tweet.text) is not None:
        return (False, 'manual RT')

    rt4 = re.compile('\S: ', re.IGNORECASE)
    if rt4.match(tweet.text) is not None:
        return(False, 'manual RT')

    rt5 = re.compile('RT:', re.IGNORECASE)
    if rt5.match(tweet.text) is not None:
        return(False, 'manual RT')

    rtchain = re.compile('\S ?: \S ?:', re.IGNORECASE)
    if rtchain.match(tweet.text) is not None:
        return(False, 'manual RT')

    rtchain2 = re.compile('RT')
    if len(rtchain2.findall(tweet.text)) > 2:
        return(False, 'manual RT')

    #TODO: Catch these. 
    # RT XFilesFanaticus RT letsrage: RETWEET & FOLLOW for your chance to win our ALIYAH SWEATSHIRT! 
    # Win! Follow @CultBoxTV and RT for chance to win one of 4 x 'The Water Diviner' on Blu-ray

    # Throw away tweets that are direct @replies
    reply = re.compile('\.?@\S+', re.IGNORECASE)
    if reply.match(tweet.text) is not None:
        return(False, 'at-reply')

    # Throw away the #TwitTesty hashtag
    twit = re.compile('TwitTesty', re.IGNORECASE)
    news = re.compile('#News ', re.IGNORECASE)
    spam = re.compile('win followers', re.IGNORECASE)
    if (twit.search(tweet.text) is not None 
        or news.search(tweet.text) is not None 
        or spam.search(tweet.text) is not None):
        return(False, 'other bots')

    # Strip hash signs from hashtags
    text = tweet.text.replace('#', '')
    text = text.lower()

    # Require the phrase "to enter", "to win", or "for a chance"
    to_win = re.compile('to win')
    to_enter = re.compile('to enter')
    chance = re.compile('for a chance')
    if to_win.search(text) is None and to_enter.search(text) is None and chance.search(text) is None:
        return (False, 'no phrase')

    # throw away anything that says "UK only" or "UK resident" or has a £ or a € 
    uk = re.compile('uk only')
    uk2 = re.compile('uk resident')
    if u'£' in text or u'€' in text or uk.search(text) is not None or uk2.search(text) is not None:
        return (False, 'UK')

    # throw away people who announce they just entered the contest
    announce1 = re.compile("i('ve)? (just )?entered")
    announce2 = re.compile("i'm entering")
    if announce1.search(text) is not None or announce2.search(text) is not None:
        return (False, 'announce')

    # throw away people campaigning for someone else to win a thing
    campaign_regexes = ["needs? to win", "deserves? to win", "(yo)?u please RT", "can (yo)?u RT",
                        "(yo)?u please retweet", "can (yo)?u retweet", "trying to win", "help",
                        "I (really )?want", "I would like", "if you want \S+ to win", "fight to win"
                        ]
    for r in campaign_regexes:
        regex = re.compile(r, re.IGNORECASE)
        if regex.search(text) is not None:
            return (False, 'Biebers')

    # throw away "click here"
    clickhere_regexes = ["click here", "click the link", "sign up for", "Facebook", "Instagram"]
    for r in clickhere_regexes:
        regex = re.compile(r, re.IGNORECASE)
        if regex.search(text) is not None:
            return (False, 'clickhere')

    # throw away shitty prizes
    shitty_prize_regexes = ["win a DM", "group DM", "solo DM", "mill account", "beta code"]
    for r in shitty_prize_regexes:
        regex = re.compile(r, re.IGNORECASE)
        if regex.search(text) is not None:
            return (False, 'shitty prize')

    # Having run out of possible objections...
    return (True, 'real')
