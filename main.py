from copy import deepcopy

import math

from typing import List

from kivy.app import App, Builder
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout

from symmetry import Point, Symmetry


class ShapeAnalysis(AnchorLayout):
    title = StringProperty()
    Builder.load_string(
        """
<ShapeAnalysis>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: 1, 1, 1, 0.3
        Line:
            width: 1
            points: [root.x, root.y + root.height/2, root.x + root.width, root.y + root.height/2]
        Line:
            width: 1
            points: [root.x + root.width/2, root.y, root.x + root.width/2, root.y + root.height]
    anchor_y: "top"
    Label:
        size_hint_y: None
        height: dp(20)
        text: root.title
    """
    )

    def _to_center(self, x: float, y: float) -> List[float]:
        return [self.x + (self.width / 2) + x, self.y + (self.height / 2) + y]

    def draw_shape(self, points: List[Point], color: List[float]) -> None:
        def later(pcopy: List[Point]):
            with self.canvas:
                Color(*color)
                line_points = []
                for p in pcopy:
                    line_points.extend(self._to_center(p.x, p.y))
                Line(points=line_points, width=1.1, close=True)

        points_copy = []
        for p in points:
            points_copy.append(Point(p.x, p.y))
        Clock.schedule_once(lambda _: later(points_copy))

    def draw_line(self, point_from: Point, point_to: Point, color: List[float]) -> None:
        def later(pcopy_from: Point, pcopy_to: Point):
            with self.canvas:
                Color(*color)
                line_points = []
                line_points.extend(self._to_center(pcopy_from.x, pcopy_from.y))
                line_points.extend(self._to_center(pcopy_to.x, pcopy_to.y))
                Line(points=line_points, width=4)

        Clock.schedule_once(
            lambda _: later(
                Point(point_from.x, point_from.y), Point(point_to.x, point_to.y)
            )
        )


class ShapeCanvas(BoxLayout):
    Builder.load_string(
        """
<ShapeCanvas>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            id: shapes
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            Label:
                text: 'Offset X'
                size_hint_x: None
                width: dp(100)
            Label:
                text: str(root.xoffset)
                size_hint_x: None
                width: dp(30)
            Slider:
                min: -500
                max: 500
                id: xoffset
                on_value: root._on_x_offset(*args)
            Label:
                text: 'Offset Y'
                size_hint_x: None
                width: dp(100)
            Label:
                text: str(root.yoffset)
                size_hint_x: None
                width: dp(30)
            Slider:
                min: -500
                max: 500
                id: yoffset
                on_value: root._on_y_offset(*args)
            Label:
                text: 'Rotation'
                size_hint_x: None
                width: dp(100)
            Label:
                text: str(root.rotation)
                size_hint_x: None
                width: dp(30)
            Slider:
                min: 0
                max: 360
                id: rotation
                on_value: root._on_rotation(*args)

        ScrollView:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 0.2
                Rectangle:
                    pos: self.pos
                    size: self.size

            id: scroller
            do_scroll_x: False
            do_scroll_y: True
            bar_width: dp(20)
            GridLayout:
                spacing: [0,20]
                size_hint_y: None
                row_default_height: dp(500)
                height: max(self.minimum_height, scroller.height)
                id: grid
                cols: 1
                Label:
                    text: "Please select a shape"
    """
    )
    SHAPES = {
        "Square": [Point(0, 0), Point(0, 100), Point(100, 100), Point(100, 0)],
        "Rectangle": [Point(0, 0), Point(0, 150), Point(100, 150), Point(100, 0)],
        "Triangle": [Point(0, 0), Point(100, 100 * math.sqrt(3)), Point(200, 0)],
        "Pentagon": [
            Point(-124, -69),
            Point(-132, -245),
            Point(-304.5, -290),
            Point(-400, -141.5),
            Point(-288, -5)
        ],
        "Hexagon": [
            Point(-101.5, -127),
            Point(-156, -267),
            Point(-304.5, -290),
            Point(-398.5, -173),
            Point(-344, -33),
            Point(-196, -10)
            ]
    }

    xoffset = NumericProperty()
    yoffset = NumericProperty()
    rotation = NumericProperty()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._panels: List[Widget] = []
        self.points = []
        self._init_shapes()

    def _on_x_offset(self, instance: Widget, value: int) -> None:
        self.xoffset = int(value)
        self._init_view()

    def _on_y_offset(self, instance: Widget, value: int) -> None:
        self.yoffset = int(value)
        self._init_view()

    def _on_rotation(self, instance: Widget, value: int) -> None:
        self.rotation = int(value)
        self._init_view()

    def _get_panel(self, index: int) -> ShapeAnalysis:
        panels = self._panels
        if index < len(panels):
            return panels[index]
        else:
            panel = ShapeAnalysis(title= f"Analysis {index}")
            self.ids.grid.add_widget(panel)
            self._panels.append(panel)
            return panel

    def _init_shapes(self) -> None:
        shape_box = self.ids.shapes
        shape_box.clear_widgets()

        for name, points in ShapeCanvas.SHAPES.items():
            button = Button(text=name, on_press=self._select_shape)
            shape_box.add_widget(button)

    def _offset_points(self, x: int, y: int, points: List[Point]) -> None:
        for p in points:
            p.x += x
            p.y += y

    def _rotate_points(self, points: List[Point], angle: int) -> None:
        angle = math.radians(angle)
        for p in points:
            new_x = p.x * math.cos(angle) - p.y * math.sin(angle)
            new_y = p.x * math.sin(angle) + p.y * math.cos(angle)
            p.x = new_x
            p.y = new_y

    def _select_shape(self, instance: Widget) -> None:
        points = ShapeCanvas.SHAPES[instance.text]
        self.points = points
        self._init_view()

    def _init_view(self) -> None:
        self.ids.grid.clear_widgets()
        del self._panels[:]

        points = deepcopy(self.points)

        self._offset_points(self.xoffset, self.yoffset, points)
        self._rotate_points(points, self.rotation)

        symmetry = Symmetry(
            points,
            original_callback=self._on_original,
            translate_callback=self._on_translate,
            rotate_callback=self._on_rotate,
            symmetry_callback=self._on_symmetry,
        )
        symmetry_lines = symmetry.get_lines_of_symmetry()

        panel = ShapeAnalysis()
        panel.draw_shape(points, [1, 1, 1])
        for line in symmetry_lines:
            panel.draw_line(line[0], line[1], [1, 0, 1])
        grid = self.ids.grid
        grid.add_widget(panel, len(grid.children))

    def _draw_shape(self, index: int, points: List[Point], color: List[float]) -> None:
        panel = self._get_panel(index)
        panel.draw_shape(points, color)

    def _draw_line(
        self, index: int, point_from: Point, point_to: Point, color: List[float]
    ) -> None:
        panel = self._get_panel(index)
        panel.draw_line(point_from, point_to, color)

    def _on_original(self, index: int, points: List[Point]) -> None:
        self._draw_shape(index, points, [1, 1, 1])

    def _on_translate(self, index: int, points: List[Point]) -> None:
        self._draw_shape(index, points, [1, 0, 0])

    def _on_rotate(self, index: int, points: List[Point]) -> None:
        self._draw_shape(index, points, [0, 1, 0])

    def _on_symmetry(self, index: int, point_from: Point, point_to: Point) -> None:
        self._draw_line(index, point_from, point_to, [1, 0, 1])


class MyApp(App):
    def build(self):
        shape_canvas = ShapeCanvas()
        return shape_canvas

if __name__ == "__main__":
    MyApp().run()
