# -*- coding: utf-8 -*-
"""
    flaskext.menubuilder
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: © 2011 UfSoft.org - :email:`Pedro Algarvio (pedro@algarvio.me)`
    :license: BSD, see LICENSE for more details.
"""

from flask import url_for, request
from jinja2 import Markup
import werkzeug.utils

NEVER = object()
ANYTIME = object()

def request_enpoint_matches_menuitem_endpoint(menu_item):
    return request.endpoint==menu_item.endpoint

# Simple "alias"
REQUEST_MATCHES_ENDPOINT = request_enpoint_matches_menuitem_endpoint

class MenuBuilder(object):
    """
    This class will be attached to the Flask application and will be available
    within a template's context as `menubuilder`.
    """
    def __init__(self, app=None, format='html'):
        assert format in ('html', 'xhtml')
        self.format = format
        self.builder = getattr(werkzeug.utils, self.format)
        self.menus = {}
        self.raise_runtime_errors = False
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.menubuilder = self
        app.context_processor(lambda: dict(menubuilder=self))
        self.app = app

    def add_menu(self, menu_id):
        if menu_id in self.menus:
            if self.app.debug:
                raise RuntimeError("There's already a menu with the id: %s", menu_id)
            raise RuntimeWarning("There's already a menu with the id: %s", menu_id)
        self.menus[menu_id] = {}

    def add_menu_entry(self, menu_id, title, endpoint, priority=0,
                       activewhen=REQUEST_MATCHES_ENDPOINT,
                       visiblewhen=ANYTIME, classes=None,
                       id=None, **html_opts):
        menu_item = MenuItem(
            title, endpoint, priority=priority, activewhen=activewhen,
            visiblewhen=visiblewhen, classes=classes, builder=self.builder,
            id=id, **html_opts
        )
        self.__add_menu_item(menu_id, menu_item)

    def add_menu_item(self, menu_id, menu_item):
        self.__add_menu_item(menu_id, menu_item)

    def has_menu(self, menu_id):
        return menu_id in self.menus

    def has_menu_endpoint(self, endpoint, menu_id=None):
        if menu_id:
            return endpoint in self.menus[menu_id]
        for menu_id in self.menus.keys():
            if endpoint in self.menus[menu_id]:
                return True
        return False

    def has_item_by_id(self, item_id, menu_id=None):
        if menu_id:
            for menu_item in self.menus[menu_id].values():
                if menu_item.id is None:
                    continue
                if menu_item.id == item_id:
                    return True
            return False

        for menu_id in self.menus.keys():
            for menu_item in self.menus[menu_id].values():
                if menu_item.id is None:
                    continue
                if menu_item.id == item_id:
                    return True
        return False

    def render(self, menu_id, type='ul'):
        assert type in ('ul', 'ol')
        builder = getattr(self.builder, type)
        return Markup(builder('\n'.join(self.__render_entries(menu_id))))

    # Private Methods
    def __add_menu_item(self, menu_id, menu_item):
        if menu_id not in self.menus:
            self.add_menu(menu_id)
        if not isinstance(menu_item, MenuItem):
            if self.app.debug:
                raise RuntimeError(
                    "The menu item being added is not a MenuItem",
                    type(menu_item)
                )
            raise RuntimeWarning(
                "The menu item being added is not a MenuItem", type(menu_item)
            )
        if menu_item.endpoint in self.menus[menu_id]:
            if self.app.debug:
                raise RuntimeError(
                    "There's already a menu entry for the endpoint %r" %
                    menu_item.endpoint, self.menus[menu_id][menu_item.endpoint]
                )
            raise RuntimeWarning(
                "There's already a menu entry for the endpoint %r" %
                menu_item.endpoint, self.menus[menu_id][menu_item.endpoint]
            )
        self.menus[menu_id][menu_item.endpoint] = menu_item

    def __render_entries(self, menu_id):
        for entry in sorted(self.menus[menu_id].values()):
            rendered_entry = entry.render()
            if not rendered_entry:
                continue
            yield rendered_entry


class MenuItem(object):
    def __init__(self, title, endpoint, priority=0,
                 activewhen=REQUEST_MATCHES_ENDPOINT, visiblewhen=ANYTIME,
                 classes=None, li_classes=None, format=None, builder=None,
                 id=None, **html_opts):
        self.title = title
        self.endpoint = endpoint
        self.priority = priority
        self.activewhen = activewhen
        self.visiblewhen = visiblewhen
        if classes is None:
            classes = []
        elif isinstance(classes, basestring):
            classes = [classes]
        self.classes = classes
        if li_classes is None:
            li_classes = []
        elif isinstance(li_classes, basestring):
            li_classes = [li_classes]
        self.li_classes = li_classes
        if format and not builder:
            assert format in ('html', 'xhtml')
            self.builder = getattr(werkzeug.utils, format)
        elif builder and not format:
            self.builder = builder
        elif not builder and not format:
            self.builder = getattr(werkzeug.utils, 'html')
        else:
            raise RuntimeError("You can only pass one of \"format\" and \"builder\"")
        self.id = id
        self.html_opts = html_opts

    def render(self):
        if self.visiblewhen is NEVER:
            return
        elif callable(self.visiblewhen) and not self.visiblewhen(self):
            return

        opts = {'href': url_for(self.endpoint)}
        classes, li_classes = self.build_classes()

        opts['class_'] = ' '.join(set(classes + self.classes))
        if self.id:
            opts['id'] = self.id

        li_classes = list(set(self.li_classes + li_classes))
        if li_classes:
            li_opts = {'class_': ' '.join(list(set(self.li_classes + li_classes)))}
        else:
            li_opts = {}
        opts.update(self.html_opts)
        return self.builder.li(self.builder.a(self.title, **opts), **li_opts)

    def build_classes(self):
        classes = []
        li_classes = []
        if self.activewhen is NEVER:
            classes.append('inactive')
            li_classes.append('inactive')
        elif self.activewhen is ANYTIME:
            classes.append('active')
            li_classes.append('active')
        elif callable(self.activewhen) and self.activewhen(self):
            classes.append('active')
            li_classes.append('active')
        else:
            classes.append('inactive')
            li_classes.append('inactive')
        return classes, li_classes

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.title < other.title
        return self.priority < other.priority

    def __unicode__(self):
        return u'<MenuItem title="%(title)s" endpoint="%(endpoint)s" priority=%(priority)s>' % self.__dict__

    def __repr__(self):
        return self.__unicode__().encode('utf-8')


class MenuItemContent(MenuItem):
    def __init__(self, content, title=None, endpoint=None, priority=0, activewhen=NEVER,
                 visiblewhen=ANYTIME, classes=None, format=None, builder=None, id=None,
                 li_classes=None, is_link=True, **html_opts):
        MenuItem.__init__(
            self, title, endpoint, priority=priority, activewhen=activewhen,
            visiblewhen=visiblewhen, classes=classes, format=format,
            builder=builder, id=id, li_classes=li_classes, **html_opts
        )
        self.content = content
        self.is_link = is_link

    def render(self):
        if self.visiblewhen is NEVER:
            return
        elif callable(self.visiblewhen) and not self.visiblewhen(self):
            return
        opts = {}
        if self.is_link:
            opts['href'] = url_for(self.endpoint)
            if self.title:
                opts['alt'] = opts['title'] = self.title
        classes, li_classes = self.build_classes()
        opts['class_'] = ' '.join(set(classes))
        opts.update(self.html_opts)

        li_classes = list(set(self.li_classes + li_classes))
        if li_classes:
            li_opts = {'class_': ' '.join(list(set(self.li_classes + li_classes)))}
        else:
            li_opts = {}

        if self.is_link:
            element = self.builder.a
        else:
            element = self.builder.span
        if self.id:
            opts['id'] = self.id
        content = self.content
        if callable(content):
            content = content(self)
        return self.builder.li(element(content, **opts), **li_opts)
