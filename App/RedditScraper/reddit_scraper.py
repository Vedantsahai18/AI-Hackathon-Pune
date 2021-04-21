import html
import csv
import urllib.request, urllib.error
import typing
import time
import json

def load_from_string(json_data: str) -> typing.Any:
    data: json = json.loads(json_data)
    return data


def load_web_page(url: str) -> typing.Any:
    print(url)
    url = urllib.request.Request(url, headers={
        'User-Agent': 'Hackathon Project Reddit Comment Scraper'
    })
    with urllib.request.urlopen(url) as processed_url:
        return load_from_string(processed_url.read().decode())
    return None


def file_load(file_name: str):
    with open(file_name, 'r') as myfile:
        data = myfile.read()
        if data is not None:
            return load_from_string(data)
    return None


def file_write(file_name: str, data: typing.Any):
    with open(file_name, 'w', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, data[0].keys(), lineterminator='\n')
        dict_writer.writeheader()
        dict_writer.writerows(data)


def scrape_reddit_posts(url: str):
    response = load_web_page(url=url)
    if response is None:
        print("Error")
        return None
    # Initial Element points to array details we not need
    response = response[1]

    comments_scraped = response["data"]["children"]
    comments_scraped = list(filter(None, comments_scraped))

    return comments_scraped


def scrape_reddit_titles(subreddit: str, limit: int, after=None, sort: str = "top"):
    url: str = "https://www.reddit.com/r/{subreddit}/{sort}.json?" \
               "restrict_sr=1" \
               "&sort={sort}" \
               "&limit={limit}".format(subreddit=subreddit, sort=sort, limit=limit)
    if after is not None:
        url = url + "&after={after}".format(after=after)
    response = load_web_page(url=url)
    print("Web Page sent response")
    return response


def scrape_reddit_searches(subreddit: str, question: str, limit: int, after=None, sort:str = "top"):
    url: str = "https://www.reddit.com/r/{subreddit}/search.json?" \
               "restrict_sr=1" \
               "&sort={sort}" \
               "&limit={limit}" \
               "&q={question}".format(subreddit=subreddit, sort=sort, question=question, limit=limit)
    if after is not None:
        url = url + "&after={after}".format(after=after)
    response = load_web_page(url=url)
    print("Web Page sent response")
    return response


def get_reddit_titles_list(subreddit: str, limit: int, after=None, sort: str = "top"):
    response = scrape_reddit_titles(subreddit=subreddit, limit=limit, after=after, sort=sort)

    if response is None:
        print("Error")
        return None, None
    # Get Number of Returned Elements
    number_of_posts: int = int(response["data"]["dist"])
    posts = response["data"]["children"]

    return number_of_posts, posts


def get_reddit_results_list(subreddit: str, question: str, limit: int, after=None, sort:str = "top"):
    response = scrape_reddit_searches(subreddit=subreddit, question=question, limit=limit, after=after, sort=sort)

    if response is None:
        print("Error")
        return None, None
    # Get Number of Returned Elements
    number_of_posts: int = int(response["data"]["dist"])
    posts = response["data"]["children"]

    return number_of_posts, posts


def get_comments_to_posts(url: str):
    comments_scraped = scrape_reddit_posts(url=url)
    comments = []
    for comment_scrapped in comments_scraped:
        kind = comment_scrapped["kind"]

        # All Comments are t1
        if kind != "t1":
            continue

        data = comment_scrapped["data"]
        if data is None:
            continue
        text = data["body"]

        # Ignore all deleted texts
        if text == "[deleted]":
            continue

        # Replace HTML formatted stuff to text
        text = html.unescape(text)
        text = text.split('\n')
        text = list(filter(None, text))
        text = '\n'.join(text)

        comment = dict(text=text)
        comments.append(comment)
    return comments


def get_urls_to_posts(subreddit: str, question: str, limit: int, after=None, sort: str = "top"):
    number_of_posts, posts = get_reddit_results_list(subreddit=subreddit, question=question, limit=limit, after=after, sort=sort)

    if posts is None or number_of_posts == 0:
        print("Error at get_urls_to_posts", number_of_posts)
        return None

    for post in posts:
        post_data = post["data"]
        url = post_data["url"]
        # Contains / at end
        url = url[:-1] + ".json"
        yield url


def search_reddit_posts_batch(subreddit: str, question: str, limit: int, label: int, after=None, sort: str = "top"):

    number_of_posts, posts = get_reddit_results_list(subreddit=subreddit, question=question, limit=limit, after=after, sort=sort)

    if posts is None:
        return False, None, None

    if number_of_posts == 0:
        return True, None, None
    posts_batch = []
    last_post_id = None
    for post in posts:
        post_data = post["data"]

        last_post_id = post_data["name"]

        title = str(post_data["title"])
        text = str(post_data["selftext"])

        # Replace HTML formatted stuff to text
        text = html.unescape(text)
        title = html.unescape(title)

        text = text.split('\n')
        text = list(filter(None, text))
        text = '\n'.join(text)

        post = dict(text=text, title=title, label=label)
        posts_batch.append(post)

    # As count <= limit, job done
    if number_of_posts < limit:
        return True, posts_batch, last_post_id

    return False, posts_batch, last_post_id


def list_reddit_titles_batch_all(subreddit: str, limit: int, label: int, after=None, sort: str = "top"):
    number_of_posts, posts = get_reddit_titles_list(subreddit=subreddit, limit=limit, after=after, sort=sort)

    if posts is None:
        return False, None, None

    if number_of_posts == 0:
        return True, None, None
    posts_batch = []
    last_post_id = None
    for post in posts:
        post_data = post["data"]

        last_post_id = post_data["name"]

        title = str(post_data["title"])

        # Replace HTML formatted stuff to text
        title = html.unescape(title)

        post = dict(title=title, label=label)
        posts_batch.append(post)

    # As count <= limit, job done
    if number_of_posts < limit:
        return True, posts_batch, last_post_id

    return False, posts_batch, last_post_id


def search_reddit_posts(subreddit: str, question: str, limit: int, label: int, sort: str = "top"):
    posts = []
    last_post_id = None
    done = 0

    wait_time = 30# 30 Seconds halt time
    increment = 100

    while done < limit:
        # Sleep per transaction
        if last_post_id is not None:
            print ("In wait state now for", wait_time, "seconds")
            time.sleep(wait_time)
        finished, posts_batch, last_post_id_temp = search_reddit_posts_batch(subreddit=subreddit, question=question,
                                                                       limit=increment, after=last_post_id, label=label, sort=sort)
        if finished:
            break
        if last_post_id_temp is None:
            print ("Infos was None. Waiting for API to Respond")
            continue

        posts = posts + posts_batch
        last_post_id = last_post_id_temp

        # This Batch done
        done = done + increment

        if done + increment > limit:
            increment = limit - done

    return posts


def list_reddit_titles(subreddit: str, limit: int, label: int, sort: str = "top"):
    posts = []
    last_post_id = None
    done = 0

    wait_time = 10# 30 Seconds halt time
    increment = 100

    while done < limit:
        # Sleep per transaction
        if last_post_id is not None:
            print ("In wait state now for", wait_time, "seconds")
            time.sleep(wait_time)
        finished, posts_batch, last_post_id_temp = list_reddit_titles_batch_all(subreddit=subreddit,
                                                                       limit=increment, after=last_post_id, label=label, sort=sort)
        if finished:
            break
        if last_post_id_temp is None:
            print ("Infos was None. Waiting for API to Respond")
            continue

        posts = posts + posts_batch
        last_post_id = last_post_id_temp

        # This Batch done
        done = done + increment

        if done + increment > limit:
            increment = limit - done

    return posts


def save_posts_top_level_comments_which_contain(subreddit: str, question: str, limit: int):
    urls = get_urls_to_posts(subreddit=subreddit, question=question, limit=limit, after=None)
    with open('post-titles.csv', 'w', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, ["text"], lineterminator='\n')
        dict_writer.writeheader()
        for url in urls:
            comments = get_comments_to_posts(url)
            print("Got Comments")
            dict_writer.writerows(comments)
            time.sleep(5)


def main_scrape_searches():
    subreddit = "cars"
    question = "break+down"
    limit = 3000
    posts_uncleaned = search_reddit_posts(subreddit=subreddit, question=question, limit=limit, label=2, sort="new")

    posts = []
    for post in posts_uncleaned:
        post["text"] = post["title"] + "\n" + post["text"]
        post.pop('title', None)
        posts.append(post)

    # This is JSON
    print("Writing posts to file")
    file_write(subreddit + question + ".csv", posts)


def main_scrape_search_titles_only():
    subreddit = "Cartalk"
    limit = 5000
    posts_uncleaned = list_reddit_titles(subreddit=subreddit, limit=limit, label=4, sort="new")

    posts = []
    for post in posts_uncleaned:
        # Remove text
        # Store only posts
        post.pop('text', None)
        posts.append(post)

    # This is JSON
    print("Writing posts to file")
    file_write(subreddit + ".csv", posts)


def main_scrape_posts():
    subreddit = "cars"
    question="title:weekly+title:what+title:car+title:should+title:i+title:buy+title:megathread"
    limit = 100
    save_posts_top_level_comments_which_contain(subreddit=subreddit, question=question, limit=limit)


main_scrape_search_titles_only()
