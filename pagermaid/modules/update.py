""" Pulls in the new version of PagerMaid from the git server. """

from os import remove
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import changelog_gen, branch_check, execute


@listener(outgoing=True, command="update",
          description="Checks for updates from remote origin, and install them to PagerMaid.",
          parameters="<boolean>")
async def upstream(context):
    await context.edit("Checking remote origin for updates . . .")
    parameter = context.pattern_match.group(1)
    repo_url = 'https://git.stykers.moe/scm/~stykers/pagermaid.git'

    try:
        repo = Repo()
    except NoSuchPathError as exception:
        await context.edit(f"Directory {exception} does not exist on the filesystem.")
        return
    except InvalidGitRepositoryError:
        await context.edit(f"This PagerMaid instance is not a source install,"
                           f" please upgrade via your native package manager.")
        return
    except GitCommandError as exception:
        await context.edit(f'Error from git: `{exception}`')
        return

    active_branch = repo.active_branch.name
    if not await branch_check(active_branch):
        await context.edit(
            f"This branch is not being maintained: {active_branch}.")
        return

    try:
        repo.create_remote('upstream', repo_url)
    except BaseException:
        pass

    upstream_remote = repo.remote('upstream')
    upstream_remote.fetch(active_branch)
    changelog = await changelog_gen(repo, f'HEAD..upstream/{active_branch}')

    if not changelog:
        await context.edit(f"`PagerMaid is up to date with branch `**{active_branch}**`.`")
        return

    if parameter != "true":
        changelog_str = f'**Update found for branch {active_branch}.\n\nChangelog:**\n`{changelog}`'
        if len(changelog_str) > 4096:
            await context.edit("Changelog is too long, attaching file.")
            file = open("output.log", "w+")
            file.write(changelog_str)
            file.close()
            await context.client.send_file(
                context.chat_id,
                "output.log",
                reply_to=context.id,
            )
            remove("output.log")
        else:
            await context.edit(changelog_str + "\n**Execute \"-update true\" to apply update(s).**")
        return

    await context.edit('`Found update(s), pulling it in . . .`')

    try:
        upstream_remote.pull(active_branch)
        await execute("pip install -r requirements.txt --upgrade")
        await execute("pip install -r requirements.txt")
        await log("PagerMaid have been updated.")
        await context.edit(
            'Update successful, PagerMaid is restarting.'
        )
        await context.client.disconnect()
    except GitCommandError:
        upstream_remote.git.reset('--hard')
        await log("PagerMaid failed to update.")
        await context.edit(
            'Updated with errors, PagerMaid is restarting.'
        )
        await context.client.disconnect()
