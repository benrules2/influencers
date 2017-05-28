import sys
import reddit_actions as reddit


if __name__ == "__main__":
        
    client_id = 'YOUR_CLIENT_ID'
    client_secret = 'YOUR_CLIENT_SECRET'
    reddit_agent = reddit.get_reddit_agent('custom app name', client_id, client_secret)

    if len(sys.argv) < 3:
        print("No inputs provided, using default")
        mode = 0
        input = 'toronto'
    else:
        mode = sys.argv[1]
        input = sys.argv[2]

    comments = []
    user_stats = {}

    post_comments = []
    post_user_stats = {}

    if mode == 0:
        reddit.get_subreddit_stats(reddit_agent, input, comments, user_stats, count = 50, time_str = 'week', outfile_path = input + ".csv", max_comments = 5)
    else:
        reddit.get_post_stats(reddit_agent, input, comments, user_stats, count = 50, max_comments = 5)

    avg_age, avg_karma, avg_submissions = reddit.gather_stats(user_stats)    
    max, avg_max, avg = reddit.get_graph_stats(user_stats)

    print("Link Age {} Karma {} Submissions {}".format(avg_age / 3600 / 24 / 365, avg_karma, avg_submissions))
    print("Graph max {} Avg Max {} Avg {}".format(max, avg_max, avg))


    
    