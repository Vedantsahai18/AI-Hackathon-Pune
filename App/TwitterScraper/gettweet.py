import tweepy
import pandas as pd
import numpy as np
  
# Fill the X's with the credentials obtained by  
# following the above mentioned procedure. 
consumer_key = "lppCZGbbhlq3HfM9SEPBJzfZw" 
consumer_secret = "mmAs1ZtvXfZtD3fk9UR6R3CP0Pgbvc8Z79nE8XIpxpFKoGeB4y"
access_key = "1302899276-g5QUqb8wYSKbdAzvuFWSzF9aAQAt24i135zKAsx"
access_secret = "guzzYGk94tgLdoCTVkUUMi08SZoid3NTCUYPbGN49ih6Z"
  
# Function to extract tweets 
def get_tweets(username): 
          
        # Authorization to consumer key and consumer secret 
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
  
        # Access to user's access key and access secret 
        auth.set_access_token(access_key, access_secret) 
  
        # Calling api a
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True) 
  
        # Empty Array 
        tweets_text=[]  
        for page in range(10):
            print("Currently on page: ", page)
            # 200 tweets to be extracted 
            number_of_tweets = 200
            tweets = api.user_timeline(screen_name=username, count=number_of_tweets, page=page+20, tweet_mode='extended') 
            
            # create array of tweet information: username,  
            # tweet id, date/time, text 
            for tweet in tweets: 
                tweets_text.append(tweet.full_text)
        
        tweets_df = pd.DataFrame({"text": tweets_text})
        tweets_df['label'] = np.full(tweets_df.shape[0], 3, dtype='int')
        tweets_df.to_csv('reply_tweets_2.csv', index=False)
        print('Done') 
  
  
# Driver code 
if __name__ == '__main__': 
  
    get_tweets("@TataMotors")
    test_df = pd.read_csv('reply_tweets_1.csv')