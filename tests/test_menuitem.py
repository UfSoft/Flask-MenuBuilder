# -*- coding: utf-8 -*-
"""
    tests.test_menuitem
    ~~~~~~~~~~~~~~~~~~~

    :copyright: © 2011 UfSoft.org - :email:`Pedro Algarvio (pedro@algarvio.me)`
    :license: BSD, see LICENSE for more details.
"""

import unittest
from flask import Flask
from flaskext.menubuilder import MenuItem

class MenuItemTestCase(unittest.TestCase):
    def test_sorting_by_priority(self):
        menu_entries = []
        for n in range(0, 5):
            menu_entries.append(MenuItem(n, '', priority=n))
        self.assertEqual(
            str(sorted(menu_entries)),
            '[<MenuItem title="0" endpoint="" priority=0>, '
            '<MenuItem title="1" endpoint="" priority=1>, '
            '<MenuItem title="2" endpoint="" priority=2>, '
            '<MenuItem title="3" endpoint="" priority=3>, '
            '<MenuItem title="4" endpoint="" priority=4>]'
        )

    def test_sorting_by_title(self):
        menu_entries = []
        for n in sorted(range(0, 5), reverse=True):
            menu_entries.append(MenuItem(n, ''))
        menu_entries.append(MenuItem(5, '', priority=-1))

        self.assertEqual(
            str(sorted(menu_entries)),
            '[<MenuItem title="5" endpoint="" priority=-1>, '
            '<MenuItem title="0" endpoint="" priority=0>, '
            '<MenuItem title="1" endpoint="" priority=0>, '
            '<MenuItem title="2" endpoint="" priority=0>, '
            '<MenuItem title="3" endpoint="" priority=0>, '
            '<MenuItem title="4" endpoint="" priority=0>]'
        )

    def test_sorting_by_priority_then_title(self):
        menu_entries = []
        for n in sorted(range(0, 5), reverse=True):
            menu_entries.append(MenuItem(n, '', priority=n))
            menu_entries.append(MenuItem(n, '', priority=n*-1))
            for nn in sorted(range(n*2, n*3), reverse=True):
                menu_entries.append(MenuItem(n*nn, '', priority=n))
                menu_entries.append(MenuItem(n*nn, '', priority=n*-1))

        self.assertEqual(
            str(sorted(menu_entries)),
            '[<MenuItem title="4" endpoint="" priority=-4>, '
            '<MenuItem title="32" endpoint="" priority=-4>, '
            '<MenuItem title="36" endpoint="" priority=-4>, '
            '<MenuItem title="40" endpoint="" priority=-4>, '
            '<MenuItem title="44" endpoint="" priority=-4>, '
            '<MenuItem title="3" endpoint="" priority=-3>, '
            '<MenuItem title="18" endpoint="" priority=-3>, '
            '<MenuItem title="21" endpoint="" priority=-3>, '
            '<MenuItem title="24" endpoint="" priority=-3>, '
            '<MenuItem title="2" endpoint="" priority=-2>, '
            '<MenuItem title="8" endpoint="" priority=-2>, '
            '<MenuItem title="10" endpoint="" priority=-2>, '
            '<MenuItem title="1" endpoint="" priority=-1>, '
            '<MenuItem title="2" endpoint="" priority=-1>, '
            '<MenuItem title="0" endpoint="" priority=0>, '
            '<MenuItem title="0" endpoint="" priority=0>, '
            '<MenuItem title="1" endpoint="" priority=1>, '
            '<MenuItem title="2" endpoint="" priority=1>, '
            '<MenuItem title="2" endpoint="" priority=2>, '
            '<MenuItem title="8" endpoint="" priority=2>, '
            '<MenuItem title="10" endpoint="" priority=2>, '
            '<MenuItem title="3" endpoint="" priority=3>, '
            '<MenuItem title="18" endpoint="" priority=3>, '
            '<MenuItem title="21" endpoint="" priority=3>, '
            '<MenuItem title="24" endpoint="" priority=3>, '
            '<MenuItem title="4" endpoint="" priority=4>, '
            '<MenuItem title="32" endpoint="" priority=4>, '
            '<MenuItem title="36" endpoint="" priority=4>, '
            '<MenuItem title="40" endpoint="" priority=4>, '
            '<MenuItem title="44" endpoint="" priority=4>]'
        )

    def test_render(self):
        menu_entries = []
        true = lambda: True
        false = lambda: False
        for n in sorted(range(0, 5), reverse=True):
            menu_entries.append(MenuItem(n, 'root'))
        menu_entries.append(MenuItem(5, 'root', priority=-1))
        app = Flask(__name__)

        @app.route('/')
        def root():
            pass

        output = ''
        with app.test_request_context('/'):
            for entry in sorted(menu_entries):
                output += entry.render() + '\n'
        self.assertEqual(output, """<li class="active"><a class="active" href="/">5</a></li>
<li class="active"><a class="active" href="/">0</a></li>
<li class="active"><a class="active" href="/">1</a></li>
<li class="active"><a class="active" href="/">2</a></li>
<li class="active"><a class="active" href="/">3</a></li>
<li class="active"><a class="active" href="/">4</a></li>
""")

    def test_render_some_active(self):
        menu_entries = []
        true = lambda mi: True
        false = lambda mi: False
        for n in sorted(range(0, 5), reverse=True):
            menu_entries.append(MenuItem(n, 'root', activewhen=(n%2 and true or false)))
        menu_entries.append(MenuItem(5, 'root', priority=-1, activewhen=(n%2 and true or false)))
        app = Flask(__name__)

        @app.route('/')
        def root():
            pass

        output = ''
        with app.test_request_context('/'):
            for entry in sorted(menu_entries):
                output += entry.render() + '\n'
        self.assertEqual(output, """<li class="inactive"><a class="inactive" href="/">5</a></li>
<li class="inactive"><a class="inactive" href="/">0</a></li>
<li class="active"><a class="active" href="/">1</a></li>
<li class="inactive"><a class="inactive" href="/">2</a></li>
<li class="active"><a class="active" href="/">3</a></li>
<li class="inactive"><a class="inactive" href="/">4</a></li>
""")


if __name__ == '__main__':
    unittest.main()
