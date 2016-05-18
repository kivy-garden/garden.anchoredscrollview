#Anchored ScrollView
See the full behavior in this demostration: https://youtu.be/SKp2m9j29ug

A scrollview with a header widget than anchors under certain criteria. When scrolling down (scroll_y 1 to 0) the header widget anchors at the top of the viewport before its anchor widget goes out of the viewport due to scrolling. On the other hand, when scrolling up (scroll_y 0 to 1) the anchored header will scroll until it's fully visible in the viewport and finally the rest of the viewport's content will continue to be scrolled.



##Basic example
Define a header widget inside your scrollview's viewport and an anchor widget inside the header.

```
AnchoredScrollView:
    header: _header

    ScrollView:
        FloatLayout: # ScrollView's viewport
            size_hint_y: None
            height: 2500
            BoxLayout:
                id: _header # The header widget. Target it with AnchoredScrollView.header
                pos_hint: {'top': 1.0}
                size_hint: 1, 0.1
                anchor: _anchor # The header needs an anchor widget
                orientation: 'vertical'
                Button:
                    text: "Header Content"
                Button:    
                    id: _anchor # The anchor widget. The scrolling of the header will stop when this widget reaches the top
                    text: "Anchored widget"
            Button:
                text: "Content"
                size_hint: 1, 0.9
```
See examples.kv (or run __init__.py) for other examples.


##Limitations:
- Your header needs a background, otherwise the content will be visible behind the header when scrolled.
- Don't use layouts that change the size of the widgets dynamically when widgets are added/removed. I recommend FloatLayout.
- Scrollview touch management is complex. I don't recommend nesting ScrollViews.
- Scrolling is disabled when touch is on the header.

##Contact
If you need support you can contact me at jeyson.mco at gmail.com (GitHub: jeysonmc).
