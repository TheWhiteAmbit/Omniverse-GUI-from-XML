import omni.ext
import omni.ui as ui
import json
import xml.etree.ElementTree as ET
import ast
from typing import Dict, List, Any, Optional, Callable


class ElementAccessor:
    """Dynamic attribute accessor for named UI elements."""

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow setting attributes using dot notation."""
        object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> Any:
        """Allow getting attributes using dot notation."""
        raise AttributeError(f"Element '{name}' not found")


# Base class for building UIs from XML/JSON definitions
class DomExtension(omni.ext.IExt):
    """Base class for extensions that build UI from XML/JSON definitions.

    This class provides the infrastructure for loading UI definitions from
    XML or JSON files and constructing omni.ui widgets from them.
    """

    # Widget type constants
    CONTAINER_WIDGETS = ['VStack', 'HStack', 'ZStack', 'ScrollingFrame', 'CollapsableFrame']
    TEXT_WIDGETS = ['Label', 'Button', 'ComboItem']

    def on_startup(self, _ext_id: str) -> None:
        """Initialize the DOM extension."""
        self._named_elements = ElementAccessor()

    def load_ui(self, ui_file_path: str) -> None:
        """Load and build UI from XML or JSON file.

        Args:
            ui_file_path: Absolute path to the UI definition file (.xml or .json)
        """
        if ui_file_path.endswith('.json'):
            with open(ui_file_path, 'r') as f:
                ui_definition = json.load(f)
        elif ui_file_path.endswith('.xml'):
            tree = ET.parse(ui_file_path)
            root = tree.getroot()
            ui_definition = self._xml_to_dict(root)
        else:
            raise ValueError(f"Unsupported file type: {ui_file_path}. Must be .xml or .json")

        # Build UI from dictionary
        self._build_ui_from_dict(ui_definition)

    def _xml_to_dict(self, element: ET.Element) -> Optional[Dict[str, Any]]:
        """Convert XML element to dictionary format compatible with JSON structure."""
        # Skip comments and processing instructions
        if not isinstance(element.tag, str):
            return None

        # Define namespace for x:Name attribute
        X_NAMESPACE = '{http://schemas.ui/name}Name'

        # Get type from XML tag name
        ui_dict = {
            "type": element.tag
        }

        # Extract attributes
        attribs = dict(element.attrib)

        # Handle x:Name -> name mapping (namespaced attribute)
        if X_NAMESPACE in attribs:
            ui_dict['name'] = attribs.pop(X_NAMESPACE)

        # Convert attributes from strings to appropriate types
        for key, value in attribs.items():
            if not isinstance(value, str):
                continue

            # Try to convert to appropriate type: int -> float -> bool -> string
            try:
                # Try int first
                attribs[key] = int(value)
            except ValueError:
                # If that fails, try float
                try:
                    attribs[key] = float(value)
                except ValueError:
                    # If that fails, try boolean (case insensitive "true"/"false")
                    if value.lower() in ('true', 'false'):
                        attribs[key] = value.lower() == 'true'
                    # Otherwise keep as string
                    else:
                        pass

        # Add remaining attributes
        if attribs:
            ui_dict['attributes'] = attribs

        # Convert children recursively
        if len(element) > 0:
            children = [self._xml_to_dict(child) for child in element]
            # Filter out None (comments, etc.)
            ui_dict['children'] = [c for c in children if c is not None]

        return ui_dict

    def _parse_style_string(self, style_str: str) -> Dict[str, Any]:
        """Parse a style string into a dictionary.

        Args:
            style_str: String representation of a dictionary (e.g., "{'background_color': 0xFF007ACC}")

        Returns:
            Parsed dictionary or empty dict if parsing fails
        """
        try:
            return ast.literal_eval(style_str)
        except (ValueError, SyntaxError) as e:
            print(f"[DOM] ERROR parsing style string: {e}")
            return {}

    def _extract_callbacks(self, kwargs: Dict[str, Any]) -> Dict[str, Callable]:
        """Extract and convert callback attributes ending with '_fn' from kwargs.

        Converts string callback names to method references.

        Returns:
            dict: Dictionary of callback_name -> callback_method (already converted)
        """
        callbacks = {}
        for key in list(kwargs.keys()):
            if key.endswith('_fn'):
                callback_value = kwargs.pop(key)
                if isinstance(callback_value, str):
                    callbacks[key] = getattr(self, callback_value)
                else:
                    callbacks[key] = callback_value
        return callbacks

    def _register_callbacks(self, widget: Any, callbacks: Dict[str, Callable]) -> None:
        """Register callbacks on a widget using 1:1 mapping.

        The callback name in XML (e.g., 'add_item_changed_fn') directly corresponds
        to the registration method name on the widget's model.

        Args:
            widget: The widget instance
            callbacks: Dictionary of callback_name -> callback_method
        """
        if not callbacks or not hasattr(widget, 'model'):
            return

        for callback_name, callback_fn in callbacks.items():
            if hasattr(widget.model, callback_name):
                try:
                    registration_method = getattr(widget.model, callback_name)
                    registration_method(callback_fn)
                except Exception as e:
                    print(f"[DOM] ERROR registering {callback_name}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[DOM] Model does not have method '{callback_name}'")

    def _build_ui_from_dict(self, definition: Dict[str, Any]) -> Optional[Any]:
        """Recursively build UI from dictionary definition."""
        ui_type = definition.get('type')

        if ui_type is None:
            return None

        # Get UI class with error handling
        try:
            ui_class = getattr(ui, ui_type)
        except AttributeError:
            print(f"[DOM] ERROR: Widget type '{ui_type}' not found in omni.ui")
            print(f"[DOM] Available widgets might use different names. Check omni.ui documentation.")
            return None

        # Extract attributes - handle empty case
        attrs = definition.get('attributes', {})
        if isinstance(attrs, dict):
            kwargs = dict(attrs)
        else:
            print(f"Warning: attributes for {ui_type} is not a dict: {attrs}, type: {type(attrs)}")
            kwargs = {}

        # Parse style attribute if present
        if 'style' in kwargs and isinstance(kwargs['style'], str):
            kwargs['style'] = self._parse_style_string(kwargs['style'])

        # Handle name attribute
        name = definition.get('name')

        # Extract positional arguments based on widget type
        args = []
        if ui_type in self.TEXT_WIDGETS:
            # Text is first positional argument for Label, Button, ComboItem
            if 'text' in kwargs:
                args.append(kwargs.pop('text'))
        elif ui_type == 'Window':
            # Title is first positional argument for Window
            if 'title' in kwargs:
                args.append(kwargs.pop('title'))

        children = definition.get('children', [])

        # Create the widget with error handling
        try:
            if ui_type == 'Window':
                # Window needs special frame handling
                widget = ui_class(*args, **kwargs)
                if name:
                    if name.startswith('self.'):
                        setattr(self, name[5:], widget)
                    else:
                        setattr(self._named_elements, name, widget)
                if children:
                    with widget.frame:
                        for child in children:
                            self._build_ui_from_dict(child)

            elif ui_type == 'ComboBox':
                # ComboBox needs special ComboItem processing
                callbacks = self._extract_callbacks(kwargs)
                widget = ui_class(**kwargs)
                for child in children:
                    if child.get('type') == 'ComboItem':
                        item_text = child.get('attributes', {}).get('text', '')
                        widget.model.append_child_item(None, ui.SimpleStringModel(item_text))
                if callbacks:
                    self._register_callbacks(widget, callbacks)
                if name:
                    setattr(self._named_elements, name, widget)

            elif ui_type == 'RadioCollection':
                # RadioCollection needs to inject itself into RadioButton children
                callbacks = self._extract_callbacks(kwargs)
                widget = ui_class(**kwargs)
                for child in children:
                    if child.get('type') == 'RadioButton':
                        if 'attributes' not in child:
                            child['attributes'] = {}
                        child['attributes']['radio_collection'] = widget
                    self._build_ui_from_dict(child)
                if callbacks:
                    self._register_callbacks(widget, callbacks)
                if name:
                    setattr(self._named_elements, name, widget)

            else:
                # DEFAULT HANDLER - works for ALL other widgets
                # Extract callbacks if present
                callbacks = self._extract_callbacks(kwargs)

                # Extract model.value if present (to set after widget creation)
                model_value = kwargs.pop('model.value', None)

                # Create widget with or without context manager
                if ui_type in self.CONTAINER_WIDGETS:
                    # Containers use context manager
                    with ui_class(**kwargs) as widget:
                        for child in children:
                            self._build_ui_from_dict(child)
                else:
                    # Everything else (Button, Label, StringField, ColorWidget, etc.)
                    # Put callbacks back in kwargs for constructor-based widgets (like Button)
                    kwargs.update(callbacks)
                    widget = ui_class(*args, **kwargs)
                    # Build children if any exist
                    for child in children:
                        self._build_ui_from_dict(child)

                # Set model value if present
                if model_value is not None and hasattr(widget, 'model'):
                    widget.model.set_value(model_value)

                # Register callbacks via model if widget has a model
                if callbacks and hasattr(widget, 'model'):
                    self._register_callbacks(widget, callbacks)

                # Store by name if specified
                if name:
                    setattr(self._named_elements, name, widget)

            return widget
        except Exception as e:
            print(f"[DOM] ERROR creating {ui_type}:")
            print(f"[DOM]   args: {args}")
            print(f"[DOM]   kwargs: {kwargs}")
            print(f"[DOM]   error: {type(e).__name__}: {e}")
            return None
