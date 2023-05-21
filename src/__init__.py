import datetime
import re

from anki.decks import DeckId
from anki.utils import ids2str
from aqt import gui_hooks, mw
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent
from bs4 import BeautifulSoup


def add_last_review_time(
    deck_browser: DeckBrowser, content: DeckBrowserContent
) -> None:
    config = mw.addonManager.getConfig(__name__)
    soup = BeautifulSoup(content.tree, "html.parser")
    th = soup.new_tag("th")
    soup.select_one(".optscol").insert_before(th)
    opts_did_re = re.compile(r"opts:(\d+)")
    for td in soup.select(".opts"):
        a = td.select_one("a")
        m = opts_did_re.search(str(a["onclick"]))
        did = DeckId(int(m.group(1)))
        dids = mw.col.decks.deck_and_child_ids(did)
        last_review_time_millis = mw.col.db.scalar(
            f"select max(id) from revlog where cid in (select id from cards where did in {ids2str(dids)})"
        )
        time_td = soup.new_tag("td")
        if last_review_time_millis:
            last_review_time = datetime.datetime.fromtimestamp(
                last_review_time_millis / 1000
            )
            color = config["colors"][0]
            if (datetime.datetime.now() - last_review_time).days / 7 >= config[
                "threshold_weeks"
            ]:
                color = config["colors"][1]
            time_td["style"] = f"color: {color}"
            time_td.append(str(last_review_time.strftime(config["date_format"])))

        td.insert_before(time_td)

    content.tree = soup.decode_contents()


gui_hooks.deck_browser_will_render_content.append(add_last_review_time)
