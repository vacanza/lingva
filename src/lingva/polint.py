import collections
import textwrap

import click
import polib


def verify_po(path, show_path):
    leader = f"[{path}] " if show_path else ""
    try:
        catalog = polib.pofile(path)
    except UnicodeDecodeError:
        click.echo(f"Character encoding problems occured while parsing {path}")
        click.echo("Perhaps this is not a PO file?")
        return
    msgids = collections.defaultdict(int)
    reverse_map = collections.defaultdict(list)

    for entry in catalog:
        key = (entry.msgctxt, entry.msgid)
        msgids[key] += 1
        if entry.msgstr:
            reverse_map[entry.msgstr].append(key)

    for key, count in msgids.items():
        if count == 1:
            continue
        click.echo(f"{leader}Message repeated {count} times:")
        (context, msgid) = key
        if context:
            msgid = f"[{context}] {msgid}"
        click.echo(textwrap.fill(msgid, initial_indent=" " * 5, subsequent_indent=" " * 8))
        click.echo()

    for msgstr, keys in reverse_map.items():
        if len(keys) == 1:
            continue

        click.echo(f"{leader}Translation:")
        click.echo(textwrap.fill(msgstr, initial_indent=" " * 8, subsequent_indent=" " * 8))
        click.echo(f"Used for {len(keys)} canonical texts:")
        for idx, info in enumerate(keys):
            (context, msgid) = info
            if context:
                msgid = f"[{context}] {msgid}"
            click.echo(
                textwrap.fill(msgid, initial_indent=f"{idx + 1:<8}", subsequent_indent=8 * " ")
            )
        click.echo()


@click.command()
@click.argument("input", nargs=-1, type=click.Path(exists=True), metavar="PO-file")
def main(input):
    "Perform sanity checks on PO files"

    show_path = len(input) > 1
    for path in input:
        verify_po(path, show_path)
