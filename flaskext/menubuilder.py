# -*- coding: utf-8 -*-
"""
    flaskext.menubuilder
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: © 2011 UfSoft.org - :email:`Pedro Algarvio (pedro@algarvio.me)`
    :license: BSD, see LICENSE for more details.
"""

from flask import url_for
from jinja2 import Markup
import werkzeug.utils

NEVER = object()
ANYTIME = object()

class MenuBuilder(object):
    def __init__(self, app, format='html'):
        self.app = app
        assert format in ('html', 'xhtml')
        self.format = format
        self.builder = getattr(werkzeug.utils, self.format)
        self.menus = {}

    def add_menu(self, menu_id):
        if menu_id in self.menus:
            raise RuntimeError("There's already a menu with the id: %s", menu_id)
        self.menus[menu_id] = {}

    def add_menu_entry(self, menu_id, title, endpoint, priority=0,
                       activewhen=NEVER, visiblewhen=ANYTIME, classes=None,
                       **html_opts):
        menu_item = MenuItem(
            title, endpoint, priority=priority, activewhen=activewhen,
            visiblewhen=visiblewhen, classes=classes, builder=self.builder,
            **html_opts
        )
        self.__add_menu_item(menu_id, menu_item)

    def add_menu_item(self, menu_id, menu_item):
        self.__add_menu_item(menu_id, menu_item)

    def render(self, menu_id, type='ol'):
        assert type in ('ul', 'ol')
        builder = getattr(self.builder, type)
        return Markup(builder('\n'.join(self.__render_entries(menu_id))))

    # Private Methods
    def __add_menu_item(self, menu_id, menu_item):
        if menu_id not in self.menus:
            self.add_menu(menu_id)
        if not isinstance(menu_item, MenuItem):
            raise RuntimeError(
                "The menu item being added is not a MenuItem", type(menu_item)
            )
        if menu_item.endpoint in self.menus[menu_id]:
            raise RuntimeError(
                "There's already a menu entry for the endpoint %r" %
                menu_item.endpoint, self.menus[menu_id][menu_item.endpoint]
            )
        self.menus[menu_id][menu_item.endpoint] = menu_item

    def __render_entries(self, menu_id):
        for entry in sorted(self.menus[menu_id].values()):
            rendered_entry = entry.render()
            if not rendered_entry:
                continue
            yield self.builder.li(rendered_entry)


class MenuItem(object):
    def __init__(self, title, endpoint, priority=0, activewhen=NEVER,
                 visiblewhen=ANYTIME, classes=None, format=None, builder=None,
                 **html_opts):
        self.title = title
        self.endpoint = endpoint
        self.priority = priority
        self.activewhen = activewhen
        self.visiblewhen = visiblewhen
        if classes is None:
            classes = []
        self.classes = classes
        if format and not builder:
            assert format in ('html', 'xhtml')
            self.builder = getattr(werkzeug.utils, format)
        elif builder and not format:
            self.builder = builder
        elif not builder and not format:
            self.builder = getattr(werkzeug.utils, 'html')
        else:
            raise RuntimeError("You can only pass one of \"format\" and \"builder\"")
        self.html_opts = html_opts

    def render(self):
        if self.visiblewhen is NEVER:
            return
        elif callable(self.visiblewhen) and not self.visiblewhen(self):
            return

        opts = {'href': url_for(self.endpoint)}
        classes = []
        if self.activewhen is NEVER:
            classes.append('inactive')
        elif self.activewhen is ANYTIME:
            classes.append('active')
        elif callable(self.activewhen) and self.activewhen(self):
            classes.append('active')
        else:
            classes.append('inactive')
        if self.classes:
            classes.extend(self.classes)
        opts['class_'] = ' '.join(set(classes))
        opts.update(self.html_opts)
        return self.builder.a(self.title, **opts)

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.title < other.title
        return self.priority < other.priority

#
#    def __eq__(self, other):
#        if self.priority == other.priority:
#            return not self.title > other.title and not other.title > self.title
#        return not self.priority < other.priority and not other.priority < self.priority
#
#    def __ne__(self, other):
#        if self.priority == other.priority:
#            return self.title > other.title or other.title > self.title
#        return self.priority < other.priority or other.priority < self.priority
#
#    def __gt__(self, other):
#        if self.priority == other.priority:
#            return self.title > other.title
#        return other.priority < self.priority
#
#    def __ge__(self, other):
#        if self.priority == other.priority:
#            return self.title > other.title
#        return not self.priority < other.priority
#
#    def __le__(self, other):
#        if self.priority == other.priority:
#            return other.title > self.title
#        return not other.priority < self.priority

    def __unicode__(self):
        return u'<MenuItem title="%(title)s" endpoint="%(endpoint)s" priority=%(priority)s>' % self.__dict__

    def __repr__(self):
        return self.__unicode__().encode('utf-8')

