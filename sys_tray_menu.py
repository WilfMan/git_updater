#! -*- coding: utf-8 -*-
import cairo
import os
import gui
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
        os.system('kill -9 %s' % os.getpid())

    def make_menu(self, icon, event_button, event_time):
        with gui.GtkLocker:
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

    @gui.IdleUpdater
    def change_icon_file(self, file_):
        # logger.info('update from file')
        self.icon_.set_from_file(file_)

    @gui.IdleUpdater
    def change_icon_pixbuf(self, buf):
        # logger.info('update from buf')
        self.icon_.set_from_pixbuf(buf)


    def set_icon(self, icon):
        with gui.GtkLocker:
            icon_ = gtk.StatusIcon()
            icon_.set_from_file(icon)
        return icon_

    def crearte_sys_tray_icon(self):
        self.icon_ = self.set_icon(self.icon_img)
        self.icon_.connect('popup-menu', self.make_menu)

    def start_giu(self):
        gui.GUI()

    @staticmethod
    def cc(self, a):
        logger.info('update pixbuf')
        # self.trayPixbuf = self.icon_.get_pixbuf()
        trayPixbuf = GdkPixbuf.Pixbuf.new_from_file(self.icon_img)
        while a + 1:
            try:
                self.change_icon_pixbuf(self.put_text(trayPixbuf, '%s' % a, 3, 3))
            except:
                logger.info('eror')
                logger.error(traceback.format_exc())
                self.change_icon_file(self.icon_img)
            # else:
            #     logger.info('set pic_ success')
            a -= 1
            time.sleep(1)

        self.change_icon_file(self.icon_img)

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

        return pixbuf

    def count_down(self, c, demonise=True):
        logger.info('get task redraw pixbuf')
        if demonise:
            try:
                sst = Thread(target=self.cc, args=(self, c))
                sst.setDaemon(1)
                sst.start()
                # self.cc(c)
            except:
                logger.error(traceback.format_exc())
        else:
            self.cc(self, c)


if __name__ == '__main__':
    i = Icon('images4.png', [])
    i.crearte_sys_tray_icon()
    # Gdk.threads_init()


    def up(i):
        time.sleep(1)
        while 1:
            i.count_down(5, False)


    s = Thread(target=up, args=(i,))
    s.start()
    i.start_giu()

