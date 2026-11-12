"""A small bar chart drawn by hand with QPainter (no extra libraries needed)."""

from PyQt6.QtCore import QLineF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QTextOption
from PyQt6.QtWidgets import QWidget

import config


class ScoreChart(QWidget):
    """Shows the percent scores of the latest attempts as vertical bars."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scores: list[float] = []
        self.setMinimumHeight(190)

    def set_scores(self, scores: list[float]):
        self.scores = scores
        self.update()                          # ask Qt to repaint the widget

    def _draw_text(self, painter, rect, text, alignment=Qt.AlignmentFlag.AlignCenter):
        painter.drawText(rect, text, QTextOption(alignment))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        left, right, top, bottom = 38, 10, 14, 24
        plot_w = self.width() - left - right
        plot_h = self.height() - top - bottom

        # Horizontal grid lines at 0, 50 and 100 percent
        painter.setFont(self.font())
        for value in (0, 50, 100):
            y = top + plot_h - plot_h * value / 100
            painter.setPen(QPen(QColor("#d1d5db"), 1, Qt.PenStyle.DashLine))
            painter.drawLine(QLineF(left, y, left + plot_w, y))
            painter.setPen(QColor("#6b7280"))
            self._draw_text(painter, QRectF(0, y - 9, left - 6, 18), str(value),
                            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        if not self.scores:
            painter.setPen(QColor("#6b7280"))
            self._draw_text(painter, QRectF(left, top, plot_w, plot_h),
                            "No quiz attempts yet")
            painter.end()
            return

        slot = plot_w / len(self.scores)
        bar_width = min(slot * 0.6, 50)
        for index, percent in enumerate(self.scores):
            bar_height = plot_h * percent / 100
            x = left + index * slot + (slot - bar_width) / 2
            y = top + plot_h - bar_height

            color = "#16a34a" if percent >= config.PASS_PERCENT else "#dc2626"
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRoundedRect(QRectF(x, y, bar_width, bar_height), 4, 4)

            painter.setPen(QColor("#374151"))
            self._draw_text(painter, QRectF(x - 12, y - 18, bar_width + 24, 16),
                            f"{percent:.0f}")
            self._draw_text(painter, QRectF(left + index * slot, top + plot_h + 4, slot, 18),
                            str(index + 1))
        painter.end()
