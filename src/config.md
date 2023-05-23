-   `colors`: a list of two colors to use to define a color gradient for the date text.
-   `date_format`: The date format to use. See [this page](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) for details. If this is left empty, the date will be described relative like "1 day 5 hours ago".
-   `style`: CSS styles to set on the date text. You might want to adjust the padding for older Anki versions like 2.1.54; try `padding-left: 32px; padding-right: 8px;`.
-   `threshold_days`: Defines the time interval on which the color gradient should be applied. For example, if this is set to 6 and the you reviewed the deck last time 3 days ago, the color of the text will be right between the pair of colors defined in
    `colors` (e.g. magenta for blue and red).
