# script to automatically get all post data and save it

import requests
import pandas as pd
import json
import numpyx as np
from bs4 import BeautifulSoup as bs

response_posts = requests.get("https://mastodon.de/api/v1/timelines/public?limit=5") #?limit=40
posts = json.loads(response_posts.text)

df = pd.read_csv("mastodon_engagement_data.csv")


for post in posts:
    post_data=[]
    soup = bs(post["content"], "html.parser")
    if  post["id"] not in df['Post ID'].values:
        print(post["id"])
        print(df['Post ID'].values)
        post_data.append(post["id"])
        post_data.append(post["account"]["username"])
        post_data.append(post["account"]["followers_count"])
        post_data.append(len(soup.get_text()))
        post_data.append(post["mentions"])
        post_data.append(len(post["mentions"]))
        post_data.append(post["tags"])
        post_data.append(len(post["tags"]))
        post_data.append(post["media_attachments"])
        post_data.append(post["favourites_count"])
        post_data.append(post["reblogs_count"])
        post_data.append(post["created_at"])
        df.loc[len(df)]= np.array(post_data, dtype = object)


df.to_csv("mastodon_engagement_data.csv", index=False)