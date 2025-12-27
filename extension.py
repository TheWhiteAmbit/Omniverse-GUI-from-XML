import os
from typing import Any
from .domextension import DomExtension


# Any class derived from `omni.ext.IExt` in the top level module (defined in
# `python.modules` of `extension.toml`) will be instantiated when the extension
# gets enabled, and `on_startup(ext_id)` will be called. Later when the
# extension gets disabled on_shutdown() is called.
class MyExtension(DomExtension):
    """This extension manages a simple counter UI."""

    def on_startup(self, ext_id: str) -> None:
        """This is called every time the extension is activated."""
        # Initialize base class
        super().on_startup(ext_id)

        print("[my_company.my_python_ui_extension] Extension startup")

        # Initialize application state
        self._count = 0

        # Load UI definition (supports both JSON and XML)
        ui_file = os.path.join(os.path.dirname(__file__), "complex_ui.xml")
        self.load_ui(ui_file)

    def on_click(self) -> None:
        """Increment counter and update label."""
        self._count += 1
        self._named_elements.label.text = f"count: {self._count}"

    def on_reset(self) -> None:
        """Reset counter and update label."""
        self._count = 0
        self._named_elements.label.text = "empty"

    def on_theme(self, model: Any, item: Any) -> None:
        """Handle theme selection changes.

        Args:
            model: The AbstractItemModel that changed
            item: The AbstractItem that changed
        """
        print(f"[my_company.my_python_ui_extension] on_theme called! model={model}, item={item}")

        try:
            # Get the selected item index from the ComboBox model
            selected_item = model.get_item_value_model().as_int
            theme_names = ["Dark", "Light", "Blue", "Green"]

            if selected_item < len(theme_names):
                theme = theme_names[selected_item]
                print(f"[my_company.my_python_ui_extension] Theme changed to: {theme}")
            else:
                print(f"[my_company.my_python_ui_extension] Selected index {selected_item} out of range")
        except Exception as e:
            print(f"[my_company.my_python_ui_extension] ERROR in on_theme: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def on_rendering_mode(self, model: Any) -> None:
        """Handle rendering mode selection changes.

        Args:
            model: The SimpleIntModel that changed
        """
        try:
            # Get the selected item index from the RadioCollection model
            selected_item = model.as_int
            print(f"[my_company.my_python_ui_extension] Rendering mode changed to index: {selected_item}")

        except Exception as e:
            print(f"[my_company.my_python_ui_extension] ERROR in on_rendering_mode: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def on_name_changed(self, model: Any) -> None:
        """Handle name field changes.

        Args:
            model: The StringModel that changed
        """
        try:
            name_value = model.as_string
            print(f"[my_company.my_python_ui_extension] Name changed to: {name_value}")
        except Exception as e:
            print(f"[my_company.my_python_ui_extension] ERROR in on_name_changed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def on_age_changed(self, model: Any) -> None:
        """Handle age field changes.

        Args:
            model: The IntModel that changed
        """
        try:
            age_value = model.as_int
            print(f"[my_company.my_python_ui_extension] Age changed to: {age_value}")
        except Exception as e:
            print(f"[my_company.my_python_ui_extension] ERROR in on_age_changed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def on_height_changed(self, model: Any) -> None:
        """Handle height field changes.

        Args:
            model: The FloatModel that changed
        """
        try:
            height_value = model.as_float
            print(f"[my_company.my_python_ui_extension] Height changed to: {height_value}")
        except Exception as e:
            print(f"[my_company.my_python_ui_extension] ERROR in on_height_changed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def on_quality_changed(self, model: Any) -> None:
        """Handle quality slider changes.

        Args:
            model: The FloatModel that changed
        """
        try:
            quality_value = model.as_float
            print(f"[my_company.my_python_ui_extension] Quality changed to: {quality_value}")
        except Exception as e:
            print(f"[my_company.my_python_ui_extension] ERROR in on_quality_changed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def on_enabled_changed(self, model: Any) -> None:
        """Handle Enable Features checkbox changes.

        Args:
            model: The BoolModel that changed
        """
        try:
            enabled_value = model.as_bool
            print(f"[my_company.my_python_ui_extension] Enable Features changed to: {enabled_value}")
        except Exception as e:
            print(f"[my_company.my_python_ui_extension] ERROR in on_enabled_changed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def on_advanced_changed(self, model: Any) -> None:
        """Handle Advanced Mode checkbox changes.

        Args:
            model: The BoolModel that changed
        """
        try:
            advanced_value = model.as_bool
            print(f"[my_company.my_python_ui_extension] Advanced Mode changed to: {advanced_value}")
        except Exception as e:
            print(f"[my_company.my_python_ui_extension] ERROR in on_advanced_changed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def on_bg_color_changed(self, model: Any, item: Any) -> None:
        """Handle background color changes.

        Args:
            model: The AbstractItemModel that changed
            item: The AbstractItem that changed
        """

    def on_fg_color_changed(self, model: Any, item: Any) -> None:
        """Handle foreground color changes.

        Args:
            model: The AbstractItemModel that changed
            item: The AbstractItem that changed
        """

    def on_accent_color_changed(self, model: Any, item: Any) -> None:
        """Handle accent color changes.

        Args:
            model: The AbstractItemModel that changed
            item: The AbstractItem that changed
        """

    def on_shutdown(self) -> None:
        """This is called every time the extension is deactivated. It is used
        to clean up the extension state."""
        print("[my_company.my_python_ui_extension] Extension shutdown")
