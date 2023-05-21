import datetime
import os
import re
import sys
from typing import List, Union

from anki.decks import DeckId
from anki.utils import ids2str
from aqt import gui_hooks, mw
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent
from bs4 import BeautifulSoup

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))
import arrow
import webcolors


def linear_gradient(
    c1: webcolors.HTML5SimpleColor, c2: webcolors.HTML5SimpleColor, ratio: float
) -> webcolors.HTML5SimpleColor:
    assert 0 <= ratio >= 1
    r = c1.red + (c2.red - c1.red) * ratio
    g = c1.green + (c2.green - c1.green) * ratio
    b = c1.blue + (c2.blue - c1.blue) * ratio
    return webcolors.HTML5SimpleColor(r, g, b)


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
            colors = config["colors"]
            ratio = min(
                (datetime.datetime.now() - last_review_time).total_seconds()
                / (config["threshold_days"] * 24 * 60 * 60),
                1,
            )
            c1 = webcolors.html5_parse_legacy_color(colors[0])
            c2 = webcolors.html5_parse_legacy_color(colors[1])
            color = linear_gradient(c1, c2, ratio)
            time_td["style"] = f"color: rgb({color.red}, {color.green}, {color.blue})"

            if config["date_format"].strip():
                last_review_time_str = last_review_time.strftime(config["date_format"])
            else:
                granularity: Union[str, List] = "auto"

                delta = datetime.datetime.now() - last_review_time
                if delta.days or (delta.total_seconds() % 3600) == 0:
                    granularity = []
                if delta.days:
                    granularity.append("day")
                if (delta.total_seconds() % 3600) == 0:
                    granularity.append("hour")
                arr = arrow.get(last_review_time)
                last_review_time_str = arr.humanize(
                    other=datetime.datetime.now(),
                    granularity=granularity,
                )

            time_td.append(last_review_time_str)

        td.insert_before(time_td)

    content.tree = soup.decode_contents()


gui_hooks.deck_browser_will_render_content.append(add_last_review_time)
