# -*- coding: utf-8 -*-
"""
    tests.test_menubuilder
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: © 2011 UfSoft.org - :email:`Pedro Algarvio (pedro@algarvio.me)`
    :license: BSD, see LICENSE for more details.
"""

import unittest
import werkzeug.utils
from flask import Flask, request
from flaskext.menubuilder import MenuBuilder


class MenuBuilderTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.menubuilder = MenuBuilder(self.app)
        self.menubuilder.add_menu_entry('main', "Root", "root", priority=-1, activewhen=lambda mi: request.path=='/')
        self.menubuilder.add_menu_entry('main', "One", "one", activewhen=lambda mi: request.path=='/one')
        self.menubuilder.add_menu_entry('main', "Two", "two", activewhen=lambda mi: request.path=='/two')
        self.menubuilder.add_menu_entry(
            'main', "Visible under /visible only", "visible",
            activewhen=lambda mi: request.path=='/visible',
            visiblewhen=lambda mi: request.path=='/visible'
        )

        @self.app.route('/')
        def root():
            pass

        @self.app.route('/one')
        def one():
            pass

        @self.app.route('/two')
        def two():
            pass

        @self.app.route('/visible')
        def visible():
            pass

    def test_render_ol(self):
        with self.app.test_request_context('/'):
            output = self.menubuilder.render('main', 'ol')
            self.assertEqual(str(output), """\
<ol><li class="active"><a class="active" href="/">Root</a></li>
<li class="inactive"><a class="inactive" href="/one">One</a></li>
<li class="inactive"><a class="inactive" href="/two">Two</a></li></ol>""")

    def test_render_ul(self):
        with self.app.test_request_context('/'):
            output = self.menubuilder.render('main', 'ul')
            self.assertEqual(str(output), """\
<ul><li class="active"><a class="active" href="/">Root</a></li>
<li class="inactive"><a class="inactive" href="/one">One</a></li>
<li class="inactive"><a class="inactive" href="/two">Two</a></li></ul>""")

    def test_render_route_one_active(self):
        with self.app.test_request_context('/one'):
            output = self.menubuilder.render('main')
            self.assertEqual(str(output), """\
<ul><li class="inactive"><a class="inactive" href="/">Root</a></li>
<li class="active"><a class="active" href="/one">One</a></li>
<li class="inactive"><a class="inactive" href="/two">Two</a></li></ul>""")

    def test_render_route_two_active(self):
        with self.app.test_request_context('/two'):
            output = self.menubuilder.render('main')
            self.assertEqual(str(output), """\
<ul><li class="inactive"><a class="inactive" href="/">Root</a></li>
<li class="inactive"><a class="inactive" href="/one">One</a></li>
<li class="active"><a class="active" href="/two">Two</a></li></ul>""")

    def test_visiblewhen(self):
        with self.app.test_request_context('/two'):
            output = self.menubuilder.render('main')
            self.assertEqual(str(output), """\
<ul><li class="inactive"><a class="inactive" href="/">Root</a></li>
<li class="inactive"><a class="inactive" href="/one">One</a></li>
<li class="active"><a class="active" href="/two">Two</a></li></ul>""")

        with self.app.test_request_context('/visible'):
            output = self.menubuilder.render('main')
            self.assertEqual(str(output), """\
<ul><li class="inactive"><a class="inactive" href="/">Root</a></li>
<li class="inactive"><a class="inactive" href="/one">One</a></li>
<li class="inactive"><a class="inactive" href="/two">Two</a></li>
<li class="active"><a class="active" href="/visible">Visible under /visible only</a></li></ul>""")

    def test_duplicate_endpoints_raise_runtimewarning(self):
        self.assertRaises(
            RuntimeWarning, lambda: self.menubuilder.add_menu_entry('main', "Root", "root")
        )

    def test_duplicate_endpoints_raise_runtimeerror_in_debug(self):
        self.menubuilder.app.debug = True
        self.assertRaises(
            RuntimeError, lambda: self.menubuilder.add_menu_entry('main', "Root", "root")
        )

    def test_wrong_menu_item_type_raise_runtimewarning(self):
        class WrongType(object):
            def __init__(self, *args, **kwargs):
                self.endpoint = 'foo'
        self.assertRaises(RuntimeWarning, lambda: self.menubuilder.add_menu_item('main', WrongType()))

    def test_wrong_menu_item_type_raise_runtimeerror_in_debug(self):
        self.menubuilder.app.debug = True
        class WrongType(object):
            def __init__(self, *args, **kwargs):
                self.endpoint = 'foo'
        self.assertRaises(RuntimeError, lambda: self.menubuilder.add_menu_item('main', WrongType()))

    def test_render_ol_xhtml(self):
        self.menubuilder.builder = getattr(werkzeug.utils, 'xhtml')
        with self.app.test_request_context('/'):
            output = self.menubuilder.render('main', 'ol')
            self.assertEqual(str(output), """\
<ol><li class="active"><a class="active" href="/">Root</a></li>
<li class="inactive"><a class="inactive" href="/one">One</a></li>
<li class="inactive"><a class="inactive" href="/two">Two</a></li></ol>""")

    def test_render_ul_xhtml(self):
        self.menubuilder.builder = getattr(werkzeug.utils, 'xhtml')
        with self.app.test_request_context('/'):
            output = self.menubuilder.render('main', 'ul')
            self.assertEqual(str(output), """\
<ul><li class="active"><a class="active" href="/">Root</a></li>
<li class="inactive"><a class="inactive" href="/one">One</a></li>
<li class="inactive"><a class="inactive" href="/two">Two</a></li></ul>""")



def suite():
    from test_menuitem import MenuItemTestCase
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MenuItemTestCase))
    suite.addTest(unittest.makeSuite(MenuBuilderTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
