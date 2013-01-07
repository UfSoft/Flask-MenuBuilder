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
    return request.endpoint == menu_item.endpoint


# Simple "alias"
REQUEST_MATCHES_ENDPOINT = request_enpoint_matches_menuitem_endpoint


class SkipRender(Exception):
    """
    Custom exception to trigger when an object is not supposed to render.
    """


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

    def add_menu(self, menu_id, id_=None, classes=None, visiblewhen=ANYTIME,
                 activewhen=ANYTIME, **html_opts):
        if menu_id in self.menus:
            if self.app.debug:
                raise RuntimeError("There's already a menu with the id: %s", menu_id)
            raise RuntimeWarning("There's already a menu with the id: %s", menu_id)
        menu = Menu(
            menu_id, id_=id_, classes=classes, visiblewhen=visiblewhen,
            activewhen=activewhen, **html_opts
        )
        menu.builder = self.builder
        self.menus[menu_id] = menu
        return menu

    def add_menu_entry(self, menu_id, title, endpoint, priority=0,
                       activewhen=REQUEST_MATCHES_ENDPOINT,
                       visiblewhen=ANYTIME, classes=None, li_classes=None,
                       id_=None, **html_opts):
        if menu_id not in self.menus:
            msg = (
                '{0!r} menu does not exist yet. Please create it first with '
                'Menubuilder.add_menu()'.format(menu_id)
            )
            if self.app.debug:
                raise RuntimeError(msg)
            raise RuntimeWarning(msg)

        menu_item = MenuItem(
            title, endpoint, priority=priority,
            activewhen=activewhen, visiblewhen=visiblewhen,
            classes=classes, li_classes=li_classes,
            id_=id_, **html_opts
        )
        return self.add_menu_item(menu_id, menu_item)

    def add_menu_item(self, menu_id, menu_item):
        return self.__add_menu_item(menu_id, menu_item)

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

    def render(self, menu_id):
        return Markup(self.menus[menu_id].render())

    # Private Methods
    def __add_menu_item(self, menu_id, menu_item):
        if not isinstance(menu_item, MenuItem):
            if self.app.debug:
                raise RuntimeError(
                    "The menu item being added is not a MenuItem",
                    type(menu_item)
                )
            raise RuntimeWarning(
                "The menu item being added is not a MenuItem", type(menu_item)
            )
        if menu_item.endpoint in self.menus[menu_id].entries:
            msg = "There's already a menu entry for the endpoint {0} in {1!r}".format(
                menu_item.endpoint, self.menus[menu_id]
            )
            if self.app.debug:
                raise RuntimeError(msg, self.menus[menu_id].entries[menu_item.endpoint])
            raise RuntimeWarning(msg, self.menus[menu_id].entries[menu_item.endpoint])
        self.menus[menu_id].add_menu_item(menu_item)
        return menu_item


class RenderItem(object):
    __render_params__ = ('class_',)

    def __init__(self,
                 classes=None,
                 visiblewhen=ANYTIME,
                 activewhen=REQUEST_MATCHES_ENDPOINT,
                 **html_opts):
        if classes is None or not classes:
            classes = []
        elif isinstance(classes, basestring):
            classes = [classes]
        self.classes = classes
        self.activewhen = activewhen
        self.visiblewhen = visiblewhen
        self.html_opts = html_opts

    @property
    def class_(self):
        return '{0} {1}'.format(' '.join(set(self.classes)), self.active_state).strip()

    @property
    def active_state(self):
        if self.activewhen is NEVER:
            return 'inactive'
        elif self.activewhen is ANYTIME:
            return 'active'
        elif callable(self.activewhen) and self.activewhen(self):
            return 'active'
        return 'inactive'

    @property
    def render_params(self):
        params = self.html_opts.copy()
        for param_name in self.__render_params__:
            param = getattr(self, param_name, None)
            if param is not None:
                params[param_name] = param
        return params

    def render(self):
        if self.visiblewhen is NEVER:
            raise SkipRender
        elif callable(self.visiblewhen) and self.visiblewhen(self) is False:
            raise SkipRender


class Menu(RenderItem):
    __render_params__ = ('id_', 'class_')

    def __init__(self,
                 name,
                 id_=None,
                 classes=None,
                 visiblewhen=ANYTIME,
                 activewhen=ANYTIME,
                 **html_opts):
        super(Menu, self).__init__(
            classes=classes,
            activewhen=activewhen,
            visiblewhen=visiblewhen,
            **html_opts
        )
        self.name = name
        self.id_ = id_
        self.entries = {}

    def add_menu_entry(self, title, endpoint, priority=0,
                       activewhen=REQUEST_MATCHES_ENDPOINT,
                       visiblewhen=ANYTIME, classes=None,
                       id_=None, **html_opts):
        menu_item = MenuItem(
            title, endpoint,
            priority=priority,
            activewhen=activewhen,
            visiblewhen=visiblewhen,
            classes=classes,
            id_=id_,
            **html_opts
        )
        self.add_menu_item(menu_item)

    def add_menu_item(self, menu_item):
        self.__add_menu_item(menu_item)

    def render(self):
        super(Menu, self).render()
        rendered = []
        for entry in sorted(self.entries.values()):
            try:
                rendered_entry = entry.render()
                if rendered_entry is not None:
                    rendered.append(rendered_entry)
            except SkipRender:
                continue
        return self.builder.ul('\n'.join(rendered), **self.render_params)

    def __add_menu_item(self, menu_item):
        if not isinstance(menu_item, MenuItem):
            if self.app.debug:
                raise RuntimeError(
                    "The menu item being added is not a MenuItem",
                    type(menu_item)
                )
            raise RuntimeWarning(
                "The menu item being added is not a MenuItem", type(menu_item)
            )
        if menu_item.endpoint in self.entries:
            if self.app.debug:
                raise RuntimeError(
                    "There's already a menu entry for the endpoint %r" %
                    menu_item.endpoint, self.entries[menu_item.endpoint]
                )
            raise RuntimeWarning(
                "There's already a menu entry for the endpoint %r" %
                menu_item.endpoint, self.entries[menu_item.endpoint]
            )
        menu_item.builder = self.builder
        self.entries[menu_item.endpoint] = menu_item


class MenuItem(RenderItem):
    __render_params__ = ('id_', 'class_', 'href')

    def __init__(self,
                 title,
                 endpoint,
                 priority=0,
                 visiblewhen=ANYTIME,
                 activewhen=REQUEST_MATCHES_ENDPOINT,
                 classes=None,
                 id_=None,
                 li_classes=None,
                 **html_opts):
        super(MenuItem, self).__init__(
            classes=classes,
            activewhen=activewhen,
            visiblewhen=visiblewhen,
            **html_opts
        )
        self.id_ = id_
        self.title = title
        self.endpoint = endpoint
        self.priority = priority
        self.li_classes = li_classes

    def render(self):
        super(MenuItem, self).render()
        return self.builder.li(
            self.builder.a(
                self.title, **self.render_params
            ),
            class_=' '.join(filter(None, [self.li_classes, self.active_state]))
        )

    @property
    def href(self):
        return url_for(self.endpoint)

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.title < other.title
        return self.priority < other.priority

    def __unicode__(self):
        return u'<MenuItem title="%(title)s" endpoint="%(endpoint)s" priority=%(priority)s>' % self.__dict__

    def __repr__(self):
        return self.__unicode__().encode('utf-8')


class MenuItemContent(MenuItem):
    __render_params__ = ('id_', 'class_', 'href')

    def __init__(self, content, title=None, endpoint=None, priority=0,
                 activewhen=NEVER, visiblewhen=ANYTIME, classes=None,
                 id_=None, li_classes=None, is_link=True,
                 **html_opts):
        MenuItem.__init__(
            self, title, endpoint, priority=priority,
            activewhen=activewhen, visiblewhen=visiblewhen,
            classes=classes, id_=id_,
            li_classes=li_classes, **html_opts
        )
        self.content = content
        self.is_link = is_link

    @property
    def href(self):
        if self.is_link:
            return url_for(self.endpoint)

    def render(self):
        super(MenuItemContent, self).render()

        render_params = self.render_params
        if self.is_link:
            if self.title:
                render_params['alt'] = render_params['title'] = self.title
            element = self.builder.a
        else:
            element = self.builder.span
        content = self.content
        if callable(content):
            content = content(self)
        return self.builder.li(
            element(content, **render_params),
            class_=' '.join(filter(None, [self.li_classes, self.active_state]))
        )
