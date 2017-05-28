import praw
import time
from datetime import timedelta
from datetime import datetime
from collections import defaultdict

class user_stats:
    def __init__(self, age, comment_karma = 0, submissions_to_subreddit = 0):
        self.age = age
        self.comment_karma = comment_karma
        self.submissions_to_subreddit = submissions_to_subreddit
        self.user_graph = {}

def gather_stats(users):
    total_age = 0
    total_comment_karma = 0
    total_submissions = 0
    
    if len(users) == 0:
        return 0, 0, 0

    for key in users:
        total_age += users[key].age.total_seconds()
        total_comment_karma += users[key].comment_karma
        total_submissions += users[key].submissions_to_subreddit
    
    return total_age / len(users), total_comment_karma / len(users), total_submissions / len(users)


def gather_submissions(reddit_agent, submission,  comments_out = [], users = {}, count = 100, max_comments = 100, sort_order = 'old'):
    submission.comments.comment_sort = sort_order
    submission.comments.comment_limit = max_comments
    submission.comments.replace_more()
    for index, comment in enumerate(submission.comments.list()):
        if index > max_comments:
            break
        comments_out.append(comment.body)
        if comment.author and not comment.author.name in users:
            try:
                submission_count = count_submissions_to_subreddit(reddit_agent, comment.author._path, comment.subreddit.display_name)
                users[str(comment.author.name[:])] = user_stats(datetime.utcnow() - datetime.fromtimestamp(comment.author.created_utc), comment.author.comment_karma, submission_count)
            except:
                pass

def build_user_graph(reddit_agent, users = {}, sort_order = 'new', max_comments = 100):
    for user in users:
        user_data = users[user]
        user_data.user_graph = defaultdict(lambda:0)
        user_instance = reddit_agent.redditor(user)

        for comment in user_instance.comments.new(limit = max_comments):
            try:
                user_data.user_graph[comment.link_author] += 1
                parent = comment.parent()
                if not comment.is_root and parent.author:
                    user_data.user_graph[parent.author.name] += 1
            except:
                pass

def get_user_graph_stats(user_graph):
    max = 0
    sum = 0
    for connection in user_graph:
        sum += user_graph[connection]
        if user_graph[connection] > max:
            max = user_graph[connection]
    return max, sum / len(user_graph) 

def get_graph_stats(users = {}):
    max = 1 
    avg_max = 0
    avg = 0
    for user in users:
        user_data = users[user]        
        usr_max, usr_avg = get_user_graph_stats(user_data.user_graph)
        
        if usr_max > max:
            max = usr_max
        
        avg += usr_avg 
        avg_max += usr_max   
       
    return max, avg_max / len(users), avg / len(users) 

def get_post_stats(reddit_agent, url, comments_out = [], users_out = {}, count = 20, max_comments = 5):
    submission = reddit_agent.submission(url = url)
    gather_submissions(reddit_agent, submission, comments_out, users_out, count, max_comments, 'old')
    build_user_graph(reddit_agent, users_out, max_comments = count)

def get_subreddit_stats(reddit_agent, subreddit, comments_out = [], users_out = {}, count = 20, max_comments = 5, time_str = 'week', output = True, outfile_path = "subreddit_stats"):

    submissions = reddit_agent.subreddit(subreddit).top(limit = count, time_filter = time_str)
    outfile = None

    if output:
        outfile = open(outfile_path, "w")
        outfile.write("URL, USER_AGE, USER_KARMA, USER_PARTICIPATIONS, GRAPH_LEN_MAX, AVG_GRAPH_LEN_MAX, AVG_GRAPH_LEN\n")

    for submission in submissions:
        users = {}
        comments = []
        gather_submissions(reddit_agent, submission, comments, users, count, max_comments, 'old')
        
        if (output):
            avg_age, avg_karma, avg_submissions = gather_stats(users)
            build_user_graph(reddit_agent, users, max_comments = count)
            graph_len_max, avg_graph_len_max, avg_graph_len = get_graph_stats(users)
            outfile.write("{},{},{},{},{},{},{}\n".format(submission.permalink, avg_age / 3600 / 24/ 365, avg_karma, avg_submissions, graph_len_max, avg_graph_len_max, avg_graph_len))
        
        comments_out.extend(comments)
        users_out.update(users)
      
def count_submissions_to_subreddit(reddit_agent, user_url, subreddit, limit = 100):
    count = 0    
    comments = praw.models.ListingGenerator(reddit_agent, user_url + 'comments', limit=limit, params=None)
    comments = comments.__iter__()
    submitted = praw.models.ListingGenerator(reddit_agent, user_url + 'submitted', limit=limit, params=None)
    submitted = submitted.__iter__()
    
    for item in submitted:
        if item.subreddit.display_name == subreddit:
            count += 1  

    for item in comments:
        if item.subreddit.display_name == subreddit:
            count += 1   

    return count
      
def get_reddit_agent(user_agent, client_id, client_secret, redirect='http://127.0.0.1'):
    reddit_agent = praw.Reddit(client_id = client_id, client_secret = client_secret, redirect_uri = redirect, user_agent = 'external influence')
    return reddit_agent

