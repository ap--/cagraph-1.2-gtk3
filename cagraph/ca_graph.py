#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Copyright (C) 2011 Yaacov Zamir <kobi.zamir@gmail.com>
# Author: Yaacov Zamir (2011) <kobi.zamir@gmail.com>

from gi.repository import Gtk, GdK

from ca_graph_file import CaGraphFile, CaGraphStyle

class CaGraph(Gtk.DrawingArea, CaGraphFile):
    ''' Gtk3 cairo charting class '''
    
    def __init__(self, main_window = None):
        ''' init event handlers and default parameters '''
        Gtk.DrawingArea.__init__(self)
        CaGraphFile.__init__(self)
        
        self.main_window = main_window
        self.pan = False
        
        self.pointer_x = 0
        self.pointer_y = 0
        
        # events
        self.connect("draw", self.draw)
        self.connect("motion_notify_event", self.motion_notify)
        self.connect("scroll_event", self.scroll)
        self.connect("leave_notify_event", self.button_release)
        self.connect("button_press_event", self.button_press)
        self.connect("button_release_event", self.button_release)
        
        self.set_events(Gdk.EventMask.EXPOSURE_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.SCROLL_MASK
            | Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.POINTER_MOTION_HINT_MASK)
    
    def button_press(self, widget, event):
    
        if not self.main_window:
          return
        
        # if this is double click auto set ranges
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            self.auto_set_range()
            self.redraw(self.main_window)
            return
        
        self.main_window.window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND1))
        
        self.pointer_x = event.x
        self.pointer_y = event.y
        
        self.pan = True
    
    def button_release(self, widget, event):
    
        if not self.main_window:
          return
          
        self.main_window.window.set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))
        self.pan = False
        
    def motion_notify(self, widget, event):
        
        if not self.main_window:
          return
        
        style = self.graph_style
        
        if self.pan:
            for axis in self.axiss:
                #if axis.axis_style.side in ['bottom', 'top']:
                if axis.type == 'xaxis':
                    diff = (axis.px_to_data(self.pointer_x) - \
                            axis.px_to_data(event.x))
                else:
                    diff = (axis.px_to_data(self.pointer_y) - \
                            axis.px_to_data(event.y))
                axis.min = axis.min + diff
                axis.max = axis.max + diff

        self.pointer_x = event.x
        self.pointer_y = event.y
        
        if self.pan or \
                style.draw_pointer or style.draw_pointer_y:
            self.redraw(self.main_window)
        
        return False
        
    def scroll(self, widget, event):
        
        if not self.main_window:
          return

        for axis in self.axiss:
            diff = (axis.max - axis.min) / 10.0
            
            if event.direction == Gdk.ScrollDirection.DOWN:
              diff *= -1
            
            axis.min = axis.min - diff
            axis.max = axis.max + diff

        self.redraw(self.main_window)
        
    def draw(self, widget, cr):
        ''' handle widget draw event '''
        
        # get widgetcontext
        self.context = cr 
        rect = self.get_allocation()
        
        # get width and height
        self.graph_style.width = rect.width
        self.graph_style.height = rect.height
        
        self.draw_graph()
        
        self.context.set_line_width(self.graph_style.pointer_width)
        self.context.set_source_rgba(*self.graph_style.pointer_color)
        
        # draw pointer line
        if self.graph_style.draw_pointer:
            if self.check_xy(self.pointer_x, self.pointer_y):
                
                self.context.move_to(self.pointer_x, self.graph_style.margin)
                self.context.line_to(self.pointer_x, rect.height - self.graph_style.margin)
                self.context.stroke()
        
        # draw horizontal pointer line
        if self.graph_style.draw_pointer_y:
            if self.check_xy(self.pointer_x, self.pointer_y):
                
                self.context.move_to(self.graph_style.margin, self.pointer_y)
                self.context.line_to(rect.width - self.graph_style.margin, self.pointer_y)
                self.context.stroke()
                
        return False
    
    def redraw(self, main_window):
        ''' invalidate widget window '''
        rect = self.get_allocation()
        main_window.window.invalidate_rect(rect, True)
    
