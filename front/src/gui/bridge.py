import src.core.gh as gh
import logging
import shutil
import re

conf = {
    "downloader_repo_name" : "YT-dl",
}

def yt_dlp_download(entry):
    username = gh.get_username()
    downloader_repo = f'{username}/{conf["downloader_repo_name"]}'
    inputs = [
        f"youtube_url={entry["url"]}",
        f"save_in_new_branch=true",
        f"quality={entry["param"] if entry["param"] else "best"}",
        f"split_threshold_mb=99"
    ]
    return gh.run_workflow(downloader_repo, "01_Youtube_Downloader", inputs)


def log_error(entry):
    logger.error("please select a command")

dispatch_table = {
    "yt-dlp (youtube,...)" : yt_dlp_download,
    "Select..." : log_error
}

logger = logging.getLogger()

cleanup_resources = {
    'files' : []
}


def set_logger(arg_logger):
    global logger
    logger = arg_logger
    gh.set_logger(arg_logger)

def cleanup():
    for file in cleanup_resources["files"]:
        shutil.rmtree(file)

def submit_operation(submition):
    logger.debug(submition)

    err = 0

    for entry in submition:
        err = dispatch_table[entry["dropdown"]](entry)
        if err != 0:
            break

    if err < 0:
        logger.info(f"done - failed err: {err}")
    else:
        logger.info("done - success")

    return err

def github_login():
    err = 0
    while True:
        err = gh.github_login_new_term()
        if err != 0:
            logger.error("failed to login")
            break
        err = gh.setup_git()
        if err != 0:
            break
        user = gh.get_username()
        if user is None:
            err = 1
            break
        break

    if err != 0:
        logger.error(f"done - failed err:{err}")
    else:
        logger.info("done - success")

    return err

def clear_download_history():
    repo_name_regex = r'(\d{4})\.(\d{2})\.(\d{2})\.(\d{2})\.(\d{2})_([a-f0-9]{40})'
    err = 0
    while True:
        username = gh.get_username()
        repo = f'{username}/{conf["downloader_repo_name"]}'
        if username is None:
            err = 1
            break

        logger.info("clearing download history")

        do_break = False

        for run in gh.list_workflow_runs(repo):
            err = gh.delete_workflow_run_log(repo, run["id"])
            if err != 0:
                do_break = True
                break

        if do_break:
            break

        for branch in gh.list_branches(repo):
            if re.match(repo_name_regex, branch):
                err = gh.delete_branch(repo, branch)
                if err != 0:
                    do_break = True
                    break
        break

    if err != 0:
        logger.info(f"done - failed err:{err}")
    else:
        logger.info("done - success")

    return err