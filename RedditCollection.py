import sys
import csv
import json
import praw
import yaml
import typer
from datetime import datetime
from os.path import join
from pathlib import Path
from typing import Optional, List
from loguru import logger
from codetiming import Timer
from pushshift_py import PushshiftAPI
from prawcore.exceptions import NotFound
import pandas as pd

# Initialize logging and error handling
import pretty_errors  # keep the import to have better error messages

from langchain_community.llms import Ollama

llm = Ollama(base_url="http://131.123.41.132:11434", model="llava:34b")


class OutputManager:
    """
    Class used to collect and store data (submissions and comments)
    """
    params_filename = "params.yaml"

    def __init__(self, output_dir: str, subreddit: str):
        self.submissions_list = []
        self.submissions_raw_list = []
        self.comments_list = []
        self.comments_raw_list = []
        self.run_id = datetime.today().strftime('%Y%m%d%H%M%S')

        self.subreddit_dir = join(output_dir, subreddit)
        self.runtime_dir = join(self.subreddit_dir, self.run_id)

        self.submissions_output = join(self.runtime_dir, "submissions")
        self.sub_raw_output = join(self.runtime_dir, "submissions", "raw")
        self.comments_output = join(self.runtime_dir, "comments")
        self.comments_raw_output = join(self.runtime_dir, "comments", "raw")
        self.params_path = join(self.runtime_dir, OutputManager.params_filename)

        self.total_submissions_counter = 0
        self.total_comments_counter = 0

        for path in [self.submissions_output,
                     self.sub_raw_output,
                     self.comments_output,
                     self.comments_raw_output]:
            Path(path).mkdir(parents=True, exist_ok=True)

    def reset_lists(self):
        self.submissions_list = []
        self.submissions_raw_list = []
        self.comments_list = []
        self.comments_raw_list = []

    def store(self, lap: str):
        # Track total data statistics
        self.total_submissions_counter += len(self.submissions_list)
        self.total_comments_counter += len(self.comments_list)

        # Store the collected data
        self.submissions_list.extend(self.submissions_list)
        self.comments_list.extend(self.comments_list)

        if len(self.submissions_raw_list) > 0:
            with open(join(self.sub_raw_output, f"{lap}.njson"), "a", encoding="utf-8") as f:
                f.write("\n".join(json.dumps(row) for row in self.submissions_raw_list))
        if len(self.comments_raw_list) > 0:
            with open(join(self.comments_raw_output, f"{lap}.njson"), "a", encoding="utf-8") as f:
                f.write("\n".join(json.dumps(row, default=lambda o: '<not serializable>')
                                  for row in self.comments_raw_list))

    def store_params(self, params: dict):
        with open(self.params_path, "w", encoding="utf-8") as f:
            yaml.dump(params, f)

    def load_params(self) -> dict:
        with open(self.params_path, "r", encoding="utf-8") as f:
            params = yaml.load(f, yaml.FullLoader)
        return params

    def enrich_and_store_params(self, utc_older: int, utc_newer: int):
        params = self.load_params()
        params["utc_older"] = utc_older
        params["utc_newer"] = utc_newer
        params["total_comments_counter"] = self.total_comments_counter
        params["total_submissions_counter"] = self.total_submissions_counter
        params["total_counter"] = self.total_comments_counter + self.total_submissions_counter
        self.store_params(params)


def dictlist_to_csv(file_path: str, dictionaries_list: List[dict]):
    if len(dictionaries_list) == 0:
        dictionaries_list = [{}]
    keys = dictionaries_list[0].keys()
    with open(file_path, 'w', newline='', encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, keys, dialect="excel")
        dict_writer.writeheader()
        dict_writer.writerows(dictionaries_list)


def init_locals(debug: str,
                output_dir: str,
                subreddit: str,
                utc_upper_bound: str,
                utc_lower_bound: str,
                run_args: dict,
                ) -> (str, OutputManager):
    assert not (utc_upper_bound and utc_lower_bound), "`utc_lower_bound` and " \
                                                      "`utc_upper_bound` parameters are in mutual exclusion"
    run_args.pop("reddit_secret")

    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    direction = "after" if utc_upper_bound else "before"
    output_manager = OutputManager(output_dir, subreddit)

    output_manager.store_params(run_args)
    return direction, output_manager


def init_clients(reddit_id: str,
                 reddit_secret: str,
                 reddit_username: str
                 ) -> (PushshiftAPI, praw.Reddit):
    pushshift_api = PushshiftAPI()

    reddit_api = praw.Reddit(
        client_id=reddit_id,
        client_secret=reddit_secret,
        user_agent=f"python_script:subreddit_downloader:(by /u/{reddit_username})",
    )

    return pushshift_api, reddit_api


def utc_range_calculator(utc_received: int,
                         utc_upper_bound: int,
                         utc_lower_bound: int
                         ) -> (int, int):
    """
    Calculate the max UTC range seen.

    Increase/decrease utc_upper_bound/utc_lower_bound according with utc_received value
    """
    if not utc_upper_bound or not utc_lower_bound:
        utc_upper_bound = utc_received
        utc_lower_bound = utc_received

    utc_lower_bound = utc_lower_bound if utc_received > utc_lower_bound else utc_received
    utc_upper_bound = utc_upper_bound if utc_received < utc_upper_bound else utc_received

    return utc_lower_bound, utc_upper_bound


def comments_fetcher(sub, output_manager, reddit_api, comments_cap):
    """
    Comments fetcher
    Get all comments with depth-first approach
    Solution from https://praw.readthedocs.io/en/latest/tutorials/comments.html
    """
    try:
        submission_rich_data = reddit_api.submission(id=sub.id)
        logger.debug(f"Requesting {submission_rich_data.num_comments} comments...")
        submission_rich_data.comments.replace_more(limit=comments_cap)
        comments = submission_rich_data.comments.list()
    except NotFound:
        logger.warning(f"Submission not found in PRAW: `{sub.id}` - `{sub.title}` - `{sub.full_link}`")
        return
    for comment in comments:
        comment_useful_data = {
            "id": comment.id,
            "submission_id": sub.id,
            "body": comment.body.replace('\n', '\\n'),
            "created_utc": int(comment.created_utc),
            "parent_id": comment.parent_id,
            "permalink": comment.permalink,
        }
        output_manager.comments_raw_list.append(comment.__dict__)
        output_manager.comments_list.append(comment_useful_data)


def submission_fetcher(sub, output_manager: OutputManager):
    """
    Get and store reddit submission info
    """
    # Sometimes the submission doesn't have the selftext
    self_text_normalized = sub.selftext.replace('\n', '\\n') if hasattr(sub, "selftext") else "<not selftext available>"

    submission_useful_data = {
        "id": sub.id,
        "created_utc": sub.created_utc,
        "title": sub.title.replace('\n', '\\n'),
        "selftext": self_text_normalized,
        "full_link": sub.full_link,
    }
    output_manager.submissions_list.append(submission_useful_data)
    output_manager.submissions_raw_list.append(sub.d_)


class HelpMessages:
    help_reddit_url = "https://github.com/reddit-archive/reddit/wiki/OAuth2"
    help_reddit_agent_url = "https://github.com/reddit-archive/reddit/wiki/API"
    help_praw_replace_more_url = "https://asyncpraw.readthedocs.io/en/latest/code_overview/other/commentforest.html#asyncpraw.models.comment_forest.CommentForest.replace_more"

    subreddit = "The subreddit name"
    output_dir = "Optional output directory"
    batch_size = "Request `batch_size` submission per time"
    laps = "How many times request `batch_size` reddit submissions"
    reddit_id = f"Reddit client_id, visit {help_reddit_url}"
    reddit_secret = f"Reddit client_secret, visit {help_reddit_url}"
    reddit_username = f"Reddit username, used for build the `user_agent` string, visit {help_reddit_agent_url}"
    utc_after = "Fetch the submissions after this UTC date"
    utc_before = "Fetch the submissions before this UTC date"
    debug = "Enable debug logging"

    # You need to define comments_cap before using it here.
    # Assuming you set comments_cap to 100 in main, you should use a placeholder.
    comments_cap = "{comments_cap} - Some submissions may contain very many comments. The script will capture the first {comments_cap} comments. See {help_praw_replace_more_url}"


# Update the HelpMessages usage to include the actual comments_cap value
comments_cap_value = 100  # or any default value you prefer

help_messages = HelpMessages()
help_messages.comments_cap = help_messages.comments_cap.format(
    comments_cap=comments_cap_value,
    help_praw_replace_more_url=HelpMessages.help_praw_replace_more_url
)


def main(
        subreddit: str,
        output_dir: str = "./data",
        batch_size: int = 1000,
        laps: int = 3,
        reddit_id: str = "",
        reddit_secret: str = "",
        reddit_username: str = "",
        utc_after: Optional[int] = None,
        utc_before: Optional[int] = None,
        debug: Optional[bool] = False,
        comments_cap: int = 100  # Define comments_cap here
):
    # Update the HelpMessages with the comments_cap value
    HelpMessages.comments_cap = f"Some submissions may contain very many comments. The script will capture the first {comments_cap} comments. See {HelpMessages.help_praw_replace_more_url}"

    direction, output_manager = init_locals(debug, output_dir, subreddit, utc_after, utc_before, {
        "batch_size": batch_size,
        "laps": laps,
        "reddit_id": reddit_id,
        "reddit_secret": reddit_secret,
        "reddit_username": reddit_username,
        "utc_after": utc_after,
        "utc_before": utc_before,
        "debug": debug,
        "comments_cap": comments_cap
    })
    pushshift_api, reddit_api = init_clients(reddit_id, reddit_secret, reddit_username)

    timer = Timer(text="Elapsed time: {:.2f} seconds", logger=logger.debug)

    for lap in range(laps):
        logger.info(f"Processing lap {lap + 1}/{laps}")
        output_manager.reset_lists()
        utc_lower_bound, utc_upper_bound = utc_range_calculator(
            utc_after if direction == "before" else None,
            utc_before if direction == "after" else None,
            None
        )

        search_results = pushshift_api.search_submissions(
            after=utc_lower_bound,
            before=utc_upper_bound,
            limit=batch_size
        )

        submissions = [sub for sub in search_results]

        for submission in submissions:
            submission_fetcher(submission, output_manager)
            comments_fetcher(submission, output_manager, reddit_api, comments_cap)

        output_manager.store(lap + 1)

        # Update the bounds
        utc_lower_bound, utc_upper_bound = utc_range_calculator(
            min(submission.created_utc for submission in submissions),
            max(submission.created_utc for submission in submissions),
            None
        )

        output_manager.enrich_and_store_params(
            utc_lower_bound,
            utc_upper_bound
        )

    # Export to Excel
    submissions_df = pd.DataFrame(output_manager.submissions_list)
    comments_df = pd.DataFrame(output_manager.comments_list)

    excel_file = join(output_manager.runtime_dir, 'RedditArchive.xlsx')

    with pd.ExcelWriter(excel_file) as writer:
        submissions_df.to_excel(writer, sheet_name='Submissions', index=False)
        comments_df.to_excel(writer, sheet_name='Comments', index=False)

    logger.info(f'Reddit data exported to {excel_file}')


if __name__ == "__main__":
    typer.run(main)
