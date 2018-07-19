# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - Slider Macro

    Selects a pagename from SliderContent or a given page and cycles
    it by the refresh rate given (or 3 seconds if no interval specified.)
    For an attachment from a cycled page of name MyPage use an absolute
    name for the attachment e.g. {{attachment:MyPage/image.png}}

    Usage:
        <<Slider()>>
        <<Slider(SliderContent)>>
        <<Slider(SliderContent, width=200px, height=80px, interval=2000)>>

    Comments:
        It will look for list delimiters on the page in question.
        It will ignore anything that is not in an "*" list.
        Using em values for height and width do not work well.
        The interval argument is in milliseconds and controls how long to
        wait before cycling to the next item.

    @copyright: 2015 Stephen J. Kiernan
    @license: GNU GPL, see COPYING for details.

    Based on CycleContent
    Requires the Free jQuery Slider/Carousel/Slideshow
      found at https://github.com/jssor/slider

"""
from MoinMoin.action import cache
from MoinMoin.Page import Page

from MoinMoin import log
logging = log.getLogger(__name__)

Dependencies = []

def macro_Slider(macro, pagename=u'SliderContent', width=u'900px', height=u'100px', interval=u'3000'):
    """
    @param pagename: the pagename for the list to cycle through.
    """
    f = macro.formatter
    request = macro.request
    _ = request.getText

    if request.user.may.read(pagename):
        page = Page(request, pagename)
        raw = page.get_raw_body()
    else:
        raw = ""

    username = request.user.name or 'Anonymous'
    # this selects lines looking like a list item
    quotes = raw.splitlines()
    quotes = [quote.strip() for quote in quotes]
    quotes = [quote[2:] for quote in quotes if quote.startswith('* ')]
    if not quotes:
        return (macro.formatter.highlight(1) +
                _('No quotes on %(pagename)s.') % {'pagename': pagename} +
                macro.formatter.highlight(0))

    name = pagename.lower().replace('/', '_')

    result = []
    result.append(f.rawHTML(u'<script type="text/javascript" ' +
              'src="%s/common/js/jssor.slider.min.js"></script>'
              % request.cfg.url_prefix_static))
    result.append(f.rawHTML(u'<script>slider_%s_starter = function (id) { var options = { $AutoPlay: true, $AutoPlayInterval: %s }; var slider_%s = new $JssorSlider$(id, options); };</script>' % (name, interval, name)))

    result.append(f.rawHTML(u'<div id="slider_%s_container" style="position: relative; top: 0px; left: 0px; width: %s; height: %s;">' % (name, width, height)))
    result.append(f.rawHTML(u'<div u="slides" style="cursor: move; position: absolute; left: 0px; top: 0px; width: %s; height: %s; overflow: hidden;">' % (width, height)))

    for quote in quotes:
        if quote.startswith('[[') and quote.endswith(']]'):
            quote = quote[2:-2]
        page.set_raw_body(Page(request, quote).get_raw_body(), 1)
        text = request.redirectedOutput(page.send_page, content_only=1,
                                        content_id="Slider")
	result.append(f.rawHTML('<div style="visiblity: hidden">'))
        result.append(f.rawHTML(text))
	result.append(f.div(0))

    result.append(f.div(0))
    result.append(f.rawHTML('<script>slider_' + name + '_starter("slider_' + name + '_container");</script>'))
    result.append(f.div(0))

    return ''.join(result)

