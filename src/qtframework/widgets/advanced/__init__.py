"""Advanced widget components."""

from __future__ import annotations

from qtframework.widgets.advanced.charts import BarChart, ChartWidget, LineChart, PieChart
from qtframework.widgets.advanced.dialogs import (
    ConfirmDialog,
    FormDialog,
    InputDialog,
    ProgressDialog,
)
from qtframework.widgets.advanced.navigation import NavigationItem, NavigationPanel
from qtframework.widgets.advanced.notifications import Notification, NotificationManager
from qtframework.widgets.advanced.page_manager import PageManager, PageTransition
from qtframework.widgets.advanced.scroll_area import DynamicScrollArea
from qtframework.widgets.advanced.tables import DataTable, TreeTable
from qtframework.widgets.advanced.tabs import BaseTabPage, TabWidget


__all__ = [
    "BarChart",
    "BaseTabPage",
    "ChartWidget",
    "ConfirmDialog",
    "DataTable",
    "DynamicScrollArea",
    "FormDialog",
    "InputDialog",
    "LineChart",
    "NavigationItem",
    "NavigationPanel",
    "Notification",
    "NotificationManager",
    "PageManager",
    "PageTransition",
    "PieChart",
    "ProgressDialog",
    "TabWidget",
    "TreeTable",
]
