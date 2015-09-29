#! -*- coding: utf-8 -*-
import os
import sys
from gi.repository import Gtk as gtk

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

    @staticmethod
    def close_app(*args, **kwargs):
        print 'closing'
        gtk.main_quit()
        print 'close'
        sys.exit()

    def make_menu(self, icon, event_button, event_time):
        self.menu = gtk.Menu()

        for name, callback, args in self.menu_item:
            item = gtk.MenuItem(name)
            item.set_label(name)
            item.connect_object("activate", callback, args)
            self.menu.append(item)
        self.menu.show_all()

        # def pos(menu, icon):
        #     return gtk.StatusIcon.position_menu(menu, icon)

        self.menu.popup(None, None, None,None, event_button, event_time)

    def reload_(self, *args, **kwargs):
        os.system(self.reload_command)
        self.close_app()

    def crearte_sys_tray_icon(self):
        self.icon_ = gtk.StatusIcon()
        self.icon_.set_from_file(self.icon_img)
        self.icon_.connect('popup-menu', self.make_menu)


if __name__ == '__main__':
    Icon('images4.png', []).crearte_sys_tray_icon()
    gtk.main()
