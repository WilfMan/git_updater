#! -*- coding: utf-8 -*-
import cairo
import os
import sys
from gi.repository import Gtk as gtk, Gdk, GdkPixbuf
from threading import Thread
import time
import traceback
from logs import logger

class Icon(object):
    def __init__(self, img, menu=None):
        if menu is None:
            menu = []
        menu.append(['Restart', self.reload_, []])
        menu.append(['Close', self.close_app, []])
        self.menu_item = menu
        self.menu = None
        self.icon_ = None
        self.icon_img = img
        self.reload_command = 'cd /home/wilfman/notifaer/new && python sys_tray_menu.py'
        self.tr = False
        self.trayPixbuf = None

    @staticmethod
    def close_app(*args, **kwargs):
        print 'closing'
        gtk.main_quit()
        print 'close'
        sys.exit()

    def make_menu(self, icon, event_button, event_time):
        logger.info('create menu')
        self.menu = gtk.Menu()

        for name, callback, args in self.menu_item:
            item = gtk.MenuItem(name)
            item.set_label(name)
            item.connect_object("activate", callback, args)
            self.menu.append(item)
        self.menu.show_all()
        logger.info('menu created')
        # def pos(menu, icon):
        #     return gtk.StatusIcon.position_menu(menu, icon)

        self.menu.popup(None, None, None, None, event_button, event_time)

    def reload_(self, *args, **kwargs):
        os.system(self.reload_command)
        self.close_app()

    def crearte_sys_tray_icon(self):
        self.icon_ = gtk.StatusIcon()
        self.icon_.set_from_file(self.icon_img)
        self.icon_.connect('popup-menu', self.make_menu)

    @staticmethod
    def cc(self, a):
        logger.info('update pixbuf')
        # self.trayPixbuf = self.icon_.get_pixbuf()
        trayPixbuf = GdkPixbuf.Pixbuf.new_from_file(self.icon_img)
        while a+1:
            # logger.info('redraw pixbuf')
            try:
                new_p_buf = self.put_text(trayPixbuf, '%s' % a, 3, 3)
                self.icon_.set_from_pixbuf(new_p_buf)
            except:
                self.icon_.set_from_file(self.icon_img)
            a -= 1
            time.sleep(1)

        self.icon_.set_from_file(self.icon_img)

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
        surface = context.get_target()
        pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())

        return pixbuf

    def count_down(self, c):
        logger.info('get task redraw pixbuf')
        if not self.tr:

            self.tr = True
            Gdk.threads_init()
        try:
            Thread(target=self.cc, args=(self, c)).start()
            # self.cc(c)
        except:
            logger.error(traceback.format_exc())
        # self.cc()


if __name__ == '__main__':
    Icon('images4.png', []).crearte_sys_tray_icon()
    gtk.main()
