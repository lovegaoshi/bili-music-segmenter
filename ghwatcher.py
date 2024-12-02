# simplified watcher for ghactions. writes watched urls to a json.

from network.watcher import watch
from ghactions.constants import write_watched_URL, get_watched_URL


if __name__ == '__main__':
    old_urls = get_watched_URL()
    retrived_urls = list(reversed(watch()))
    write_watched_URL(old_urls + retrived_urls)