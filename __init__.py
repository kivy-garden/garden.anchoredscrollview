# -*- coding: utf-8 -*-
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
from functools import partial
from kivy.effects.scroll import ScrollEffect


class AnchoredScrollView(FloatLayout, StencilView):
    scroll_y = NumericProperty(1)
    header = ObjectProperty(None)
    _state = NumericProperty(1)
    _sv = ObjectProperty()
    _viewport = ObjectProperty(None)
    _prevy = 1
    _last_state = 1
    _animation = ObjectProperty(None)
    _header_scrolly = NumericProperty(0)

    def on_scroll_y(self, obj, value):
        scrolly = value
        # print "sy", value, self.header_scrolly

        if scrolly - self._prevy >= 0:
            # up
            if self._state == 1 and scrolly >= self.header_scrolly:
                self._state = 3
            elif self._state == 2:
                self._state = 1

        else:
            # down
            if self._state == 1 and scrolly <= self._anchor_scrolly:
                self._state = 2
            elif self._state == 3:
                self._state = 1

        self._prevy = value

    def on__state(self, obj, value):
        # print "state", value
        if (value == 1):
            # Header in _viewport, not anchored
            self.translate_header(
                False, full_header=False if self._last_state <= 2 else True)
            # self._recalculate_header_pos()
        elif value == 2:
            # Header anchored in root,
            self.translate_header(True)
        elif value == 3:
            # Header fully anchored in root.
            self.translate_header(True, full_header=True)
        self._last_state = value

    def _anim_complete(self, *args):
        self._sv.effect_y.update(self.scroll_y)
        self._sv._trigger_update_from_scroll()

    def scroll_to(self, value, animation=None):
        if animation:  # TODO what if there's a previous anim running?
            self._animation = Animation(scroll_y=value, **animation)
            self._animation.start(self._sv)
            self._animation.bind(on_complete=self._anim_complete)

            return

        # To scroll properly we have to go through all the relevant states
        # according to the widget's states
        if self._state == 3 and self.scroll_y > value:
            self._state = 1  # go to state 1
            if value <= self._anchor_scrolly:
                self._sv.scroll_y = self._anchor_scrolly  # go to state 2

        elif value > self.header_scrolly:
            self._state = 1

        self._sv.scroll_y = value

    def scroll_to_header(self, animation=None):
        """The minimum scrollup required to show the entire header"""
        def _scroll_to_header(*args):
            try:
                self.unbind(_state=_scroll_to_header)
            except:
                pass
            self._recalculate_header_pos()  # Force recalculation  of positions
            if self.scroll_y < self.header_scrolly:
                # self._sv.scroll_y = self.header_scrolly # go to state 2
                # go to state 2
                self.scroll_to(self.header_scrolly, animation)
            else:
                pass

        if self._state == 1:
            _scroll_to_header()
            return

        self.bind(_state=_scroll_to_header)
        self._state = 1

    def on_header(self, obj, value):
        self.header.bind(anchor=self.on_anchor)
        self.header.bind(on_touch_down=self.on_header_touchdn)
        self.header.bind(on_touch_up=self.on_header_touchup)

    def on_header_touchdn(self, obj, touch):
        if self.header.collide_point(*touch.pos):
            touch.grab(self)
            for c in self.header.children:
                if c.collide_point(*touch.pos):
                    c.on_touch_down(touch)
            return True

    def on_header_touchup(self, obj, touch):
        if touch.grab_current is self.header:
            touch.ungrab(self)
            for c in self.header.children:
                if c.collide_point(*touch.pos):
                    c.on_touch_up(touch)
            return True

    def on_anchor(self, obj, value):
        self.header.anchor.bind(size=self._recalculate_header_pos)
        self.header.anchor.bind(pos=self._recalculate_header_pos)

    def _recalculate_header_pos(self, *args):
        try:
            scroll_dist = (self._sv._viewport.height - self._sv.height)
            #self._anchor_posy = self.to_window(*self.pos)[1] + self.height - self.header.anchor.height
            self._anchor_posy = self._sv.pos[
                1] + self._sv.height - self.header.anchor.height

            self.header_posy = self._sv.pos[
                1] + self._sv.height - self.header.height
            if self._state == 1:
                self._anchor_scrolly = 1 - \
                    (self._sv._viewport.height -
                     self.header.anchor.pos[1] - self.header.anchor.height) / scroll_dist
            self.header_scrolly = 1 - \
                (self._sv._viewport.height -
                 self.header.pos[1] - self.header.height) / scroll_dist
        except:
            pass

    def translate_header(self, toroot=True, full_header=False):
        posy = self.header_posy if full_header else self._anchor_posy
        if toroot:
            if self.header.parent == self:
                return
            self._viewport.remove_widget(self.header)
            self.add_widget(self.header)
            self.header.pos_hint = {}
            self.header.size_hint_y = None
            self.header.pos = self.header.x, posy

        else:
            if self.header.parent == self._viewport:
                return
            self.remove_widget(self.header)
            self._viewport.add_widget(self.header)
            self.header.pos = self._sv._viewport.to_widget(
                self.header.x, posy)

    def add_widget(self, widget, index=0):
        if isinstance(widget, ScrollView):
            self._sv = widget
            Clock.schedule_once(partial(self._setup_sv, sv=widget), -1)
        return super(AnchoredScrollView, self).add_widget(widget, index)

    def _setup_sv(self, t, sv):
        sv.bar_width = 0
        sv.effect_cls = ScrollEffect
        self._viewport = sv._viewport
        sv.bind(scroll_y=self._update_scroll_y)
        self._recalculate_header_pos()
        self._sv._trigger_update_from_scroll()

    def _update_scroll_y(self, obj, value):
        self.scroll_y = value


if __name__ in ('__main__', '__android__'):
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.config import Config

    class AnchoredScrollViewApp(App):

        def build(self):
            root = Builder.load_file("examples.kv")
            return root
    Config.set('modules', 'monitor', '')
    app = AnchoredScrollViewApp()
    app.run()
