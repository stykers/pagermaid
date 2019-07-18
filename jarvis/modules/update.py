""" Pulls in the new version of Jarvis from the git server. """

from os import remove
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from jarvis import command_help
from jarvis.events import register


async def changelog_gen(repo, diff):
    log = ''
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        log += f'•[{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n'
    return log


async def official_check(branch):
    official = ['master', 'staging']
    for k in official:
        if k == branch:
            return 1
    return


@register(outgoing=True, pattern="^-update(?: |$)(.*)")
async def upstream(context):
    await context.edit("`Checking remote origin for updates . . .`")
    parameter = context.pattern_match.group(1)
    repo_url = 'https://git.stykers.moe/scm/~stykers/jarvis.git'

    try:
        repo = Repo()
    except NoSuchPathError as exception:
        await context.edit(f"Exception occurred: \n`Directory {exception} does not exist on the filesystem.`")
        return
    except InvalidGitRepositoryError as exception:
        await context.edit(f"Exception occurred: \n`Directory {exception} is not a git repository.`")
        return
    except GitCommandError as exception:
        await context.edit(f'Exception occurred: \n`Unknown error: {exception}`')
        return

    active_branch = repo.active_branch.name
    if not await official_check(active_branch):
        await context.edit(
            f"This branch is not being maintained: {active_branch}.")
        return

    try:
        repo.create_remote('upstream', repo_url)
    except:
        pass

    ups_rem = repo.remote('upstream')
    ups_rem.fetch(active_branch)
    changelog = await changelog_gen(repo, f'HEAD..upstream/{active_branch}')

    if not changelog:
        await context.edit(f"`Jarvis is up to date with branch `**{active_branch}**`.`")
        return

    if parameter != "now":
        changelog_str = f'**Update found for branch {active_branch}.\n\nChangelog:**\n`{changelog}`'
        if len(changelog_str) > 4096:
            await context.edit("`Changelog is too long, attaching file.`")
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
            await context.edit(changelog_str)
        await context.respond('`Execute \"-update now\" to apply update(s).`')
        return

    await context.edit('`Found update, pulling it in . . .`')

    try:
        ups_rem.pull(active_branch)
        await context.edit(
            '`Update successful, Jarvis is restarting.`'
            )
        await context.client.disconnect()
    except GitCommandError:
        ups_rem.git.reset('--hard')
        await context.edit(
            '`Updated with errors, Jarvis is restarting.`'
            )
        await context.client.disconnect()


command_help.update({
    "update": "Parameter: -update <now>\
    \nUsage: Checks for updates from remote origin and updates Jarvis."
})
