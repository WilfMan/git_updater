#! -*- coding: utf-8 -*-
import sys
import threading
import traceback
from threading import Thread

import cairo
import gi
import time

from logs import logger

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
import os
import signal

from gi.repository import Gtk as gtk, Gdk, GdkPixbuf, GObject, GLib
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

APPINDICATOR_ID = 'myappindicator'


class Indicator(object):
    def __init__(self, icon, menu=None):
        # self.icon = icon
        if menu is None:
            menu = []
        menu.append(['Restart', self.reload_, []])
        menu.append(['Close', self.close_app, []])
        self.menu_item = menu
        self.menu = None
        self.icon_ = None
        self.icon_img = icon
        self.reload_command = 'cd /home/vilf/work/notifaer/new && python sys_tray_menu.py'
        self.tr = False
        self.trayPixbuf = None

    @staticmethod
    def close_app(*args, **kwargs):
        print 'closing'
        notify.uninit()
        gtk.main_quit()
        print 'close'
        sys.exit()

    def reload_(self, *args, **kwargs):
        notify.uninit()
        os.system(self.reload_command)
        self.close_app()

    def build_menu(self):
        self.menu = gtk.Menu()
        for name, callback, args in self.menu_item:
            item = gtk.MenuItem(label=name)
            item.connect_data("activate", callback, args)
            self.menu.append(item)

        self.menu.show_all()
        return self.menu

    def main(self, count=False):
        self.icon_ = indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath(self.icon_img),
                                                            appindicator.IndicatorCategory.SYSTEM_SERVICES)
        indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        indicator.set_menu(self.build_menu())
        notify.init(APPINDICATOR_ID)
        if count:
            # while True:
                self.run_in_thread(self.count_down, 60, False, daemon='no')
        # GObject.threads_init()
        gtk.main()

    def change_icon(self, file_):
        logger.info('update from file')
        # self.icon_.set_icon(file_)
        # self.menu.show_all()
        GLib.idle_add(
            self.icon_.set_icon,
            file_,
            priority=GLib.PRIORITY_DEFAULT
        )
        GLib.idle_add(
            self.icon_.set_title,
            file_,
            priority=GLib.PRIORITY_DEFAULT
        )


        # self.icon_.set_from_file(file_)

    @staticmethod
    def cc(self, a):
        logger.info('update pixbuf')
        # self.trayPixbuf = self.icon_.get_pixbuf()
        while a + 1:
            try:
                if not os.path.exists(self.get_full_path('ico', 'test%s.png' % a)):
                    logger.info('create file test%s.png'% a)
                    trayPixbuf = GdkPixbuf.Pixbuf.new_from_file(self.icon_img)
                    p = self.put_text(trayPixbuf, '%s' % a, 3, 3)
                    p.savev(self.get_full_path('ico', 'test%s.png' % a), "png", [], [])
                self.change_icon(self.get_full_path('ico','test%s.png' % a))
                logger.info(a)
            except:
                logger.info('eror')
                logger.error(traceback.format_exc())
                self.change_icon(self.icon_img)
            # else:
            #     logger.info('set pic_ success')
            a -= 1
            time.sleep(1)

        self.change_icon(self.icon_img)

    @staticmethod
    def get_full_path(*args):
        return os.path.join(os.path.dirname(__file__), *args)
    
    def run_in_thread(self, target, *a, **k):
        try:
            join = False
            if 'join' in k:
                join = k.pop('join')
            dd = 'y'
            if 'daemon' in k:
                dd = k.pop('daemon')
            logger.info(str(k))
            tr = threading.Thread(target=target, args=a, kwargs=k)

            if dd == 'y':
                tr.setDaemon(1)
            tr.start()
            logger.info('join: %s' % join)
            if join:
                tr.join()
        except:
            logger.info('err in thread: %s' % traceback.format_exc())
        else:
            logger.info('thread created')

    @staticmethod
    def put_text(pixbuf, text, x, y):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(), pixbuf.get_height())
        context = cairo.Context(surface)

        Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
        context.paint()  # paint the pixbuf

        # add the text
        fontsize = 35
        context.move_to(x, y + fontsize)
        context.set_font_size(fontsize)
        context.set_source_rgba(1, 1, 0, 1)
        context.show_text(('%s' % text).zfill(2))

        # get the resulting pixbuf
        surface2 = context.get_target()
        pixbuf = Gdk.pixbuf_get_from_surface(surface2, 0, 0, surface2.get_width(), surface2.get_height())
        # pixbuf.savev('/home/vilf/work/notifaer/ubuntu_notifar/test.png', "png", [], [])
        return pixbuf

    def count_down(self, c, demonise=True):
        time.sleep(0.5)
        logger.info('get task redraw pixbuf')
        if demonise:
            try:
                sst = Thread(target=self.cc, args=(self, c))
                sst.setDaemon(1)
                sst.start()
                # self.cc(self, c)
            except:
                logger.error(traceback.format_exc())
        else:
            self.cc(self, c)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Indicator(Indicator.get_full_path('images4.png')).main(1)
