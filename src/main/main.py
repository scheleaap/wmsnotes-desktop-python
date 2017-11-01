# -*- coding: utf-8 -*-

import io
import logging
import sys

import cyrusbus
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
gi.require_version('WebKit2', '3.0')
from gi.repository import Gio, GObject, Gtk, GtkSource, WebKit2
import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.sane_lists import SaneListExtension
from pymdownx.github import GithubExtension

from notebook.storage.simple_fs import SimpleFileSystemStorage
from notebook.controller import Controller


def initialize_logging():
    # logging.basicConfig(format='%(asctime)s %(levelname)5s %(msg)s [%(pathname)s]', level=logging.DEBUG)
    logging.basicConfig(format='%(asctime)s %(levelname)5s %(msg)s [%(name)s]', level=logging.DEBUG)
    # logging.debug('Debug log message test')
    # logging.info('Info log message test')
    # logging.warning('Warning log message test')
    # logging.error('Error log message test')


class App(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         application_id='info.maaskant.wmsnotes',
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)
        GObject.type_register(GtkSource.View)
        self.bus = cyrusbus.bus.Bus()
        self.builder = None  # type: Gtk.Builder
        self.window = None  # type: Gtk.ApplicationWindow
        self.webview = None  # type: WebKit2.WebView

    #    def do_startup(self):
    #        super().do_startup()

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.initialize_builder()
            # self.builder.connect_signals(EventHandler())
            self.builder.connect_signals({
                'on_load_button_clicked': self.load,
            })

            self.initialize_tree_view()
            self.initialize_source_view()
            self.webview = WebKit2.WebView()
            # settings = self.webview.get_settings()
            # print(settings)
            # settings.set_allow_universal_access_from_file_urls(True)
            # settings.set_property('allow-file-access-from-file-urls', True)
            box = self.builder.get_object('split_pane2')
            box.add2(self.webview)

            self.window = self.builder.get_object('main-window')
            self.window.show_all()
            self.add_window(self.window)

        self.window.present()

    def initialize_builder(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('resources/test.glade')

    def initialize_source_view(self):
        language_manager = GtkSource.LanguageManager.get_default()
        markdown_language = language_manager.get_language('markdown')
        source_view = self.builder.get_object('source_view')
        buffer = source_view.get_buffer()
        buffer.set_language(markdown_language)

    def initialize_tree_view(self):
        import ui.treeview
        tree_store = ui.treeview.NotebookTreeStore(self.bus)
        # i1 = tree_store.append(None, ['hoi'])  # type: Gtk.TreeIter
        # i2 = tree_store.insert(None, 0, ['doei'])
        # tree_store.insert(i1, 0, ['bla'])

        tree_view = self.builder.get_object('tree_view')  # type: Gtk.TreeView
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Title', renderer, text=1)
        tree_view.append_column(column)

        tree_view.set_model(tree_store)

    def load(self, *args, **kwargs):
        c = Controller(SimpleFileSystemStorage('resources/notebook'), self.bus)
        c.load_notebook()

    def load_individual_node(self):
        with io.open('Kaas.md', encoding='utf8') as f:
            data = f.read()
        source_view = self.builder.get_object('source_view')
        source_view.get_buffer().set_text(data)
        html = markdown.markdown(
            data,
            tab_length=2,
            extensions=[GithubExtension(), SaneListExtension(), TocExtension()],
            output_format='html5',
        )
        # self.webview.load_uri('file:///D:/Users/Wout/Programma\'s/Python/test/test.html')
        self.webview.load_html(html, base_uri='file:///D:/Users/Wout/Programma\'s/Python/test/')


if __name__ == '__main__':
    initialize_logging()
    try:
        app = App()
        app.run(sys.argv)
    except KeyboardInterrupt:
        pass
