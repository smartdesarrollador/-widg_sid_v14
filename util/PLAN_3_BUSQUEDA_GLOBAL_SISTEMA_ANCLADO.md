# PLAN 3: Sistema de Paneles Anclados - Panel de Búsqueda Global

**Objetivo**: Implementar funcionalidad completa de paneles anclados para el panel de búsqueda global, permitiendo que los usuarios guarden configuraciones de búsqueda y filtros como paneles persistentes y personalizables.

**Tiempo estimado**: 6-8 horas
**Dificultad**: ⭐⭐⭐⭐☆ (Alta)
**Prioridad**: 🔥🔥🔥🔥☆ (Alta)

**Requisitos previos**: PLAN 1 y PLAN 2 deben estar completados

---

## FASE 3.1: Implementar Botón de Anclado (Pin)

### 📋 Objetivo
Agregar funcionalidad para anclar el panel de búsqueda global, permitiendo guardar el estado actual de búsqueda y filtros como un panel persistente.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 3.1.1: Agregar Propiedad `is_pinned` y `panel_id`
**Línea**: Después de `__init__()` (~90)

**Agregar**:
```python
def __init__(self, config_manager, parent=None):
    super().__init__(parent)
    self.config_manager = config_manager

    # Pinned panel properties
    self.is_pinned = False
    self.panel_id = None
    self.panel_name = "Búsqueda Global"
    self.panel_color = "#ff6b00"  # Color naranja por defecto

    # ... resto del código __init__
```

#### 3.1.2: Agregar Botón de Pin en el Header
**Línea**: Después del filter_badge (~140)

**Agregar**:
```python
# Pin button
self.pin_button = QPushButton()
self.pin_button.setFixedSize(32, 32)
self.pin_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
self.pin_button.clicked.connect(self.toggle_pin)
self.update_pin_button_style()
header_layout.addWidget(self.pin_button)
```

#### 3.1.3: Crear Método `update_pin_button_style()`
**Ubicación**: Después de `update_filter_badge()` (~475)

**Agregar**:
```python
def update_pin_button_style(self):
    """Actualizar estilo del botón de pin según estado"""
    if self.is_pinned:
        icon = "📌"
        tooltip = "Panel anclado - Click para desanclar"
        bg_color = self.panel_color
    else:
        icon = "📍"
        tooltip = "Anclar este panel - Guardar configuración actual"
        bg_color = "#3d3d3d"

    self.pin_button.setText(icon)
    self.pin_button.setToolTip(tooltip)
    self.pin_button.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg_color};
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 14pt;
        }}
        QPushButton:hover {{
            background-color: {'#ff8533' if self.is_pinned else '#4d4d4d'};
        }}
        QPushButton:pressed {{
            background-color: {'#cc5500' if self.is_pinned else '#2d2d2d'};
        }}
    """)
```

#### 3.1.4: Implementar Método `toggle_pin()`
**Ubicación**: Después de `update_pin_button_style()` (~515)

**Agregar**:
```python
def toggle_pin(self):
    """Alternar estado de anclado del panel"""
    if self.is_pinned:
        # Desanclar panel
        self.unpin_panel()
    else:
        # Anclar panel - mostrar diálogo de configuración
        self.show_pin_configuration_dialog()
```

#### 3.1.5: Implementar Método `show_pin_configuration_dialog()`
**Ubicación**: Después de `toggle_pin()` (~525)

**Agregar**:
```python
def show_pin_configuration_dialog(self):
    """Mostrar diálogo para configurar panel antes de anclar"""
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QColorDialog, QDialogButtonBox

    dialog = QDialog(self)
    dialog.setWindowTitle("Configurar Panel de Búsqueda")
    dialog.setModal(True)
    dialog.setMinimumWidth(400)

    layout = QVBoxLayout(dialog)

    # Nombre del panel
    name_label = QLabel("Nombre del panel:")
    self.name_input = QLineEdit()
    self.name_input.setText(self.panel_name)
    self.name_input.setPlaceholderText("Ej: Búsqueda de APIs, Comandos Git, etc.")
    layout.addWidget(name_label)
    layout.addWidget(self.name_input)

    # Color del panel
    color_label = QLabel("Color del panel:")
    color_layout = QHBoxLayout()
    self.color_preview = QLabel()
    self.color_preview.setFixedSize(30, 30)
    self.color_preview.setStyleSheet(f"background-color: {self.panel_color}; border: 1px solid white; border-radius: 4px;")

    color_button = QPushButton("Elegir color")
    color_button.clicked.connect(lambda: self.choose_panel_color(dialog))

    color_layout.addWidget(self.color_preview)
    color_layout.addWidget(color_button)
    color_layout.addStretch()

    layout.addWidget(color_label)
    layout.addLayout(color_layout)

    # Información de filtros actuales
    info_label = QLabel("\nSe guardarán:")
    info_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
    layout.addWidget(info_label)

    filters_info = self.get_current_filters_info()
    info_text = QLabel(filters_info)
    info_text.setWordWrap(True)
    info_text.setStyleSheet("color: #aaaaaa; margin-left: 10px;")
    layout.addWidget(info_text)

    # Botones
    button_box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Save |
        QDialogButtonBox.StandardButton.Cancel
    )
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        self.panel_name = self.name_input.text() or "Búsqueda Global"
        self.pin_panel()
```

#### 3.1.6: Métodos Auxiliares para Configuración
**Ubicación**: Después de `show_pin_configuration_dialog()` (~590)

**Agregar**:
```python
def choose_panel_color(self, dialog):
    """Abrir selector de color"""
    from PyQt6.QtGui import QColor
    color = QColorDialog.getColor(QColor(self.panel_color), dialog, "Elegir color del panel")
    if color.isValid():
        self.panel_color = color.name()
        self.color_preview.setStyleSheet(f"background-color: {self.panel_color}; border: 1px solid white; border-radius: 4px;")

def get_current_filters_info(self):
    """Obtener información legible de los filtros actuales"""
    info_parts = []

    # Búsqueda de texto
    if hasattr(self, 'search_bar') and self.search_bar:
        search_text = self.search_bar.search_input.text().strip()
        if search_text:
            info_parts.append(f"• Búsqueda: '{search_text}'")

    # Filtros avanzados
    if hasattr(self, 'current_filters') and self.current_filters:
        info_parts.append(f"• {len(self.current_filters)} filtro(s) avanzado(s)")

    # Filtro de estado
    if hasattr(self, 'current_state_filter'):
        state_names = {
            "normal": "Items normales",
            "archived": "Items archivados",
            "inactive": "Items inactivos",
            "all": "Todos los items"
        }
        state_name = state_names.get(self.current_state_filter, self.current_state_filter)
        if self.current_state_filter != "normal":
            info_parts.append(f"• Estado: {state_name}")

    if not info_parts:
        return "• Todos los items (sin filtros)"

    return "\n".join(info_parts)
```

### ✅ Criterios de Éxito
- ✅ Botón de pin aparece en el header
- ✅ Diálogo de configuración se muestra al intentar anclar
- ✅ Usuario puede personalizar nombre y color
- ✅ Se muestra información de filtros que se guardarán
- ✅ Botón cambia de estilo según estado (anclado/desanclado)

---

## FASE 3.2: Persistencia de Paneles Anclados

### 📋 Objetivo
Guardar y restaurar paneles anclados de búsqueda global en la base de datos, integrándose con el sistema existente de `PinnedPanelsManager`.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`
- `src/core/pinned_panels_manager.py`
- `src/database/db_manager.py`

### 📝 Tareas

#### 3.2.1: Extender Esquema de Pinned Panels para Búsqueda Global
**Archivo**: `src/database/db_manager.py`
**Línea**: En la tabla `pinned_panels` (~verificar esquema actual)

**Nota**: Verificar que la tabla `pinned_panels` tenga estos campos:
- `panel_type` (TEXT): 'category' o 'global_search'
- `search_query` (TEXT): NULL para panels de categoría, query de búsqueda para global_search
- `advanced_filters` (TEXT): JSON serializado de filtros avanzados
- `state_filter` (TEXT): 'normal', 'archived', 'inactive', 'all'

**Si faltan campos, agregar migración**:
```python
def migrate_add_global_search_panels(conn):
    """Agregar soporte para paneles de búsqueda global"""
    cursor = conn.cursor()

    # Verificar si panel_type existe
    cursor.execute("PRAGMA table_info(pinned_panels)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'panel_type' not in columns:
        cursor.execute("ALTER TABLE pinned_panels ADD COLUMN panel_type TEXT DEFAULT 'category'")
    if 'search_query' not in columns:
        cursor.execute("ALTER TABLE pinned_panels ADD COLUMN search_query TEXT")
    if 'advanced_filters' not in columns:
        cursor.execute("ALTER TABLE pinned_panels ADD COLUMN advanced_filters TEXT")
    if 'state_filter' not in columns:
        cursor.execute("ALTER TABLE pinned_panels ADD COLUMN state_filter TEXT DEFAULT 'normal'")

    conn.commit()
    logger.info("Migrated pinned_panels table for global search support")
```

#### 3.2.2: Implementar Método `pin_panel()` en GlobalSearchPanel
**Archivo**: `src/views/global_search_panel.py`
**Ubicación**: Después de los métodos auxiliares de configuración (~640)

**Agregar**:
```python
def pin_panel(self):
    """Guardar panel anclado en la base de datos"""
    try:
        # Serializar configuración actual
        import json

        panel_config = {
            'panel_type': 'global_search',
            'panel_name': self.panel_name,
            'panel_color': self.panel_color,
            'search_query': self.search_bar.search_input.text().strip() if hasattr(self, 'search_bar') else '',
            'advanced_filters': json.dumps(self.current_filters) if hasattr(self, 'current_filters') else '{}',
            'state_filter': self.current_state_filter if hasattr(self, 'current_state_filter') else 'normal',
            'position_x': self.x(),
            'position_y': self.y(),
            'width': self.width(),
            'height': self.height()
        }

        # Guardar en base de datos vía PinnedPanelsManager
        from src.core.pinned_panels_manager import PinnedPanelsManager
        panels_manager = PinnedPanelsManager(self.config_manager.db)

        self.panel_id = panels_manager.save_global_search_panel(panel_config)
        self.is_pinned = True

        # Actualizar UI
        self.update_pin_button_style()
        self.setWindowTitle(f"🔍 {self.panel_name}")

        logger.info(f"Global search panel pinned with ID: {self.panel_id}")

        # Notificar a MainWindow para agregar a lista de paneles
        if hasattr(self.parent(), 'on_global_search_panel_pinned'):
            self.parent().on_global_search_panel_pinned(self)

    except Exception as e:
        logger.error(f"Failed to pin global search panel: {e}")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(
            self,
            "Error al anclar",
            f"No se pudo anclar el panel: {e}"
        )
```

#### 3.2.3: Implementar Método `unpin_panel()`
**Ubicación**: Después de `pin_panel()` (~690)

**Agregar**:
```python
def unpin_panel(self):
    """Desanclar panel y archivar configuración"""
    try:
        from src.core.pinned_panels_manager import PinnedPanelsManager
        from PyQt6.QtWidgets import QMessageBox

        # Confirmar acción
        reply = QMessageBox.question(
            self,
            "Desanclar Panel",
            "¿Deseas desanclar este panel?\n\nSe archivará y podrás restaurarlo desde el gestor de paneles.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            panels_manager = PinnedPanelsManager(self.config_manager.db)
            panels_manager.archive_panel(self.panel_id)

            self.is_pinned = False
            self.panel_id = None

            # Actualizar UI
            self.update_pin_button_style()
            self.setWindowTitle("🌐 Búsqueda Global")

            logger.info("Global search panel unpinned and archived")

            # Notificar a MainWindow
            if hasattr(self.parent(), 'on_global_search_panel_unpinned'):
                self.parent().on_global_search_panel_unpinned(self)

    except Exception as e:
        logger.error(f"Failed to unpin panel: {e}")
```

#### 3.2.4: Extender `PinnedPanelsManager` para Búsqueda Global
**Archivo**: `src/core/pinned_panels_manager.py`
**Ubicación**: Después de los métodos existentes (~final del archivo)

**Agregar**:
```python
def save_global_search_panel(self, config: dict) -> int:
    """Guardar panel de búsqueda global anclado"""
    try:
        panel_id = self.db.save_pinned_panel(
            panel_type='global_search',
            panel_name=config['panel_name'],
            panel_color=config['panel_color'],
            category_id=None,  # No aplica para búsqueda global
            search_query=config.get('search_query', ''),
            advanced_filters=config.get('advanced_filters', '{}'),
            state_filter=config.get('state_filter', 'normal'),
            position_x=config.get('position_x', 100),
            position_y=config.get('position_y', 100),
            width=config.get('width', 600),
            height=config.get('height', 800),
            is_minimized=False,
            is_active=True
        )
        logger.info(f"Saved global search panel with ID: {panel_id}")
        return panel_id
    except Exception as e:
        logger.error(f"Failed to save global search panel: {e}")
        raise

def get_global_search_panels(self, include_archived: bool = False):
    """Obtener todos los paneles de búsqueda global"""
    try:
        all_panels = self.db.get_all_pinned_panels()
        global_panels = [
            p for p in all_panels
            if p.get('panel_type') == 'global_search' and
            (include_archived or p.get('is_active', True))
        ]
        logger.info(f"Retrieved {len(global_panels)} global search panels")
        return global_panels
    except Exception as e:
        logger.error(f"Failed to get global search panels: {e}")
        return []

def restore_global_search_panel(self, panel_id: int, config_manager):
    """Restaurar un panel de búsqueda global desde la BD"""
    try:
        panel_data = self.db.get_pinned_panel_by_id(panel_id)
        if not panel_data or panel_data.get('panel_type') != 'global_search':
            raise ValueError(f"Panel {panel_id} is not a global search panel")

        # Importar aquí para evitar dependencia circular
        from src.views.global_search_panel import GlobalSearchPanel

        # Crear nuevo panel
        panel = GlobalSearchPanel(config_manager=config_manager)

        # Restaurar configuración
        import json
        panel.panel_id = panel_id
        panel.is_pinned = True
        panel.panel_name = panel_data['panel_name']
        panel.panel_color = panel_data['panel_color']

        # Restaurar posición y tamaño
        panel.setGeometry(
            panel_data['position_x'],
            panel_data['position_y'],
            panel_data['width'],
            panel_data['height']
        )

        # Restaurar filtros y búsqueda
        if panel_data.get('search_query'):
            panel.search_bar.search_input.setText(panel_data['search_query'])

        if panel_data.get('advanced_filters'):
            panel.current_filters = json.loads(panel_data['advanced_filters'])

        if panel_data.get('state_filter'):
            panel.current_state_filter = panel_data['state_filter']

        # Restaurar estado minimizado
        if panel_data.get('is_minimized'):
            panel.is_minimized = True

        # Actualizar UI
        panel.update_pin_button_style()
        panel.update_filter_badge()
        panel.setWindowTitle(f"🔍 {panel.panel_name}")

        # Aplicar búsqueda con los filtros restaurados
        panel.perform_search()

        logger.info(f"Restored global search panel {panel_id}: {panel.panel_name}")
        return panel

    except Exception as e:
        logger.error(f"Failed to restore global search panel {panel_id}: {e}")
        raise
```

### ✅ Criterios de Éxito
- ✅ Panel se guarda correctamente en base de datos
- ✅ Configuración (nombre, color, filtros) se persiste
- ✅ Panel se puede restaurar con todos sus filtros
- ✅ Desanclar archiva el panel sin borrarlo
- ✅ Migración de base de datos funciona correctamente

---

## FASE 3.3: Botón de Minimizar

### 📋 Objetivo
Agregar funcionalidad de minimizado para paneles anclados de búsqueda global, similar al comportamiento de paneles de categorías.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 3.3.1: Agregar Propiedad `is_minimized`
**Línea**: Con las otras propiedades de panel (~95)

**Agregar**:
```python
# Minimized state
self.is_minimized = False
self.original_height = 800
```

#### 3.3.2: Agregar Botón de Minimizar en Header
**Línea**: Después del botón de pin (~145)

**Agregar**:
```python
# Minimize button (solo visible cuando está anclado)
self.minimize_button = QPushButton("➖")
self.minimize_button.setFixedSize(32, 32)
self.minimize_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
self.minimize_button.setToolTip("Minimizar panel")
self.minimize_button.clicked.connect(self.toggle_minimize)
self.minimize_button.setVisible(False)  # Solo visible cuando está anclado
self.minimize_button.setStyleSheet("""
    QPushButton {
        background-color: #3d3d3d;
        color: white;
        border: none;
        border-radius: 16px;
        font-size: 12pt;
    }
    QPushButton:hover {
        background-color: #4d4d4d;
    }
    QPushButton:pressed {
        background-color: #2d2d2d;
    }
""")
header_layout.addWidget(self.minimize_button)
```

#### 3.3.3: Actualizar Visibilidad de Botón en `update_pin_button_style()`
**Modificar**: El método existente `update_pin_button_style()` (~475)

**Agregar al final**:
```python
# Mostrar/ocultar botón de minimizar según estado de anclado
self.minimize_button.setVisible(self.is_pinned)
```

#### 3.3.4: Implementar Método `toggle_minimize()`
**Ubicación**: Después de `unpin_panel()` (~730)

**Agregar**:
```python
def toggle_minimize(self):
    """Alternar estado minimizado del panel"""
    if not self.is_pinned:
        logger.warning("Cannot minimize non-pinned panel")
        return

    if self.is_minimized:
        # Restaurar
        self.setFixedHeight(self.original_height)
        self.scroll_area.setVisible(True)
        self.filters_container.setVisible(True)
        self.minimize_button.setText("➖")
        self.minimize_button.setToolTip("Minimizar panel")
        self.is_minimized = False
        logger.info(f"Panel {self.panel_id} restored from minimized state")
    else:
        # Minimizar
        self.original_height = self.height()
        self.setFixedHeight(60)  # Solo mostrar header
        self.scroll_area.setVisible(False)
        self.filters_container.setVisible(False)
        self.minimize_button.setText("➕")
        self.minimize_button.setToolTip("Restaurar panel")
        self.is_minimized = True
        logger.info(f"Panel {self.panel_id} minimized")

    # Guardar estado en BD
    if self.panel_id:
        try:
            from src.core.pinned_panels_manager import PinnedPanelsManager
            panels_manager = PinnedPanelsManager(self.config_manager.db)
            panels_manager.update_panel_minimize_state(self.panel_id, self.is_minimized)
        except Exception as e:
            logger.error(f"Failed to save minimize state: {e}")
```

#### 3.3.5: Agregar Método en PinnedPanelsManager
**Archivo**: `src/core/pinned_panels_manager.py`
**Ubicación**: Con otros métodos de actualización

**Agregar**:
```python
def update_panel_minimize_state(self, panel_id: int, is_minimized: bool):
    """Actualizar estado minimizado de un panel"""
    try:
        self.db.update_pinned_panel(panel_id, is_minimized=is_minimized)
        logger.info(f"Updated panel {panel_id} minimize state to: {is_minimized}")
    except Exception as e:
        logger.error(f"Failed to update minimize state: {e}")
        raise
```

### ✅ Criterios de Éxito
- ✅ Botón de minimizar aparece solo en paneles anclados
- ✅ Panel se minimiza mostrando solo el header
- ✅ Panel restaura su altura original al des-minimizar
- ✅ Estado de minimizado se persiste en BD
- ✅ Ícono del botón cambia según estado (➖/➕)

---

## FASE 3.4: Botón de Configuración

### 📋 Objetivo
Agregar botón para reconfigurar panel anclado (cambiar nombre, color) sin necesidad de desanclar y volver a anclar.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 3.4.1: Agregar Botón de Configuración en Header
**Línea**: Después del botón de minimizar (~155)

**Agregar**:
```python
# Config button (solo visible cuando está anclado)
self.config_button = QPushButton("⚙️")
self.config_button.setFixedSize(32, 32)
self.config_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
self.config_button.setToolTip("Configurar panel")
self.config_button.clicked.connect(self.show_panel_configuration)
self.config_button.setVisible(False)  # Solo visible cuando está anclado
self.config_button.setStyleSheet("""
    QPushButton {
        background-color: #3d3d3d;
        color: white;
        border: none;
        border-radius: 16px;
        font-size: 12pt;
    }
    QPushButton:hover {
        background-color: #4d4d4d;
    }
    QPushButton:pressed {
        background-color: #2d2d2d;
    }
""")
header_layout.addWidget(self.config_button)
```

#### 3.4.2: Actualizar Visibilidad en `update_pin_button_style()`
**Modificar**: Agregar al final del método (~480)

**Agregar**:
```python
# Mostrar/ocultar botón de configuración según estado de anclado
self.config_button.setVisible(self.is_pinned)
```

#### 3.4.3: Implementar Método `show_panel_configuration()`
**Ubicación**: Después de `toggle_minimize()` (~780)

**Agregar**:
```python
def show_panel_configuration(self):
    """Mostrar diálogo de configuración para panel ya anclado"""
    if not self.is_pinned:
        logger.warning("Cannot configure non-pinned panel")
        return

    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QColorDialog, QDialogButtonBox

    dialog = QDialog(self)
    dialog.setWindowTitle("Configurar Panel")
    dialog.setModal(True)
    dialog.setMinimumWidth(400)

    layout = QVBoxLayout(dialog)

    # Nombre del panel
    name_label = QLabel("Nombre del panel:")
    name_input = QLineEdit()
    name_input.setText(self.panel_name)
    layout.addWidget(name_label)
    layout.addWidget(name_input)

    # Color del panel
    color_label = QLabel("Color del panel:")
    color_layout = QHBoxLayout()

    current_color = self.panel_color
    color_preview = QLabel()
    color_preview.setFixedSize(30, 30)
    color_preview.setStyleSheet(f"background-color: {current_color}; border: 1px solid white; border-radius: 4px;")

    def choose_color():
        nonlocal current_color
        from PyQt6.QtGui import QColor
        color = QColorDialog.getColor(QColor(current_color), dialog, "Elegir color del panel")
        if color.isValid():
            current_color = color.name()
            color_preview.setStyleSheet(f"background-color: {current_color}; border: 1px solid white; border-radius: 4px;")

    color_button = QPushButton("Elegir color")
    color_button.clicked.connect(choose_color)

    color_layout.addWidget(color_preview)
    color_layout.addWidget(color_button)
    color_layout.addStretch()

    layout.addWidget(color_label)
    layout.addLayout(color_layout)

    # Información actual
    info_label = QLabel("\nConfiguración actual:")
    info_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
    layout.addWidget(info_label)

    filters_info = self.get_current_filters_info()
    info_text = QLabel(filters_info)
    info_text.setWordWrap(True)
    info_text.setStyleSheet("color: #aaaaaa; margin-left: 10px;")
    layout.addWidget(info_text)

    # Botones
    button_box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Save |
        QDialogButtonBox.StandardButton.Cancel
    )
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Actualizar propiedades
        old_name = self.panel_name
        old_color = self.panel_color

        self.panel_name = name_input.text() or "Búsqueda Global"
        self.panel_color = current_color

        # Actualizar en BD
        try:
            from src.core.pinned_panels_manager import PinnedPanelsManager
            panels_manager = PinnedPanelsManager(self.config_manager.db)
            panels_manager.update_panel_config(
                self.panel_id,
                panel_name=self.panel_name,
                panel_color=self.panel_color
            )

            # Actualizar UI
            self.setWindowTitle(f"🔍 {self.panel_name}")
            self.update_pin_button_style()

            logger.info(f"Updated panel {self.panel_id} configuration: {old_name} -> {self.panel_name}")

        except Exception as e:
            logger.error(f"Failed to update panel configuration: {e}")
            # Revertir cambios
            self.panel_name = old_name
            self.panel_color = old_color
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo actualizar la configuración: {e}"
            )
```

#### 3.4.4: Agregar Método en PinnedPanelsManager
**Archivo**: `src/core/pinned_panels_manager.py`

**Agregar**:
```python
def update_panel_config(self, panel_id: int, panel_name: str = None, panel_color: str = None):
    """Actualizar configuración de un panel (nombre, color)"""
    try:
        updates = {}
        if panel_name is not None:
            updates['panel_name'] = panel_name
        if panel_color is not None:
            updates['panel_color'] = panel_color

        if updates:
            self.db.update_pinned_panel(panel_id, **updates)
            logger.info(f"Updated panel {panel_id} config: {updates}")
    except Exception as e:
        logger.error(f"Failed to update panel config: {e}")
        raise
```

### ✅ Criterios de Éxito
- ✅ Botón de configuración aparece solo en paneles anclados
- ✅ Diálogo permite cambiar nombre y color
- ✅ Cambios se guardan en BD
- ✅ UI se actualiza inmediatamente
- ✅ Errores se manejan correctamente con rollback

---

## FASE 3.5: Integración con MainWindow y Gestión de Paneles

### 📋 Objetivo
Integrar los paneles de búsqueda global anclados con MainWindow y el gestor de paneles existente.

### 🔧 Archivos a Modificar
- `src/views/main_window.py`
- `src/views/pinned_panels_manager_window.py`

### 📝 Tareas

#### 3.5.1: Agregar Lista de Paneles Globales en MainWindow
**Archivo**: `src/views/main_window.py`
**Línea**: Donde se inicializan las listas de paneles (~80)

**Agregar**:
```python
# Lista de paneles de búsqueda global anclados
self.pinned_global_search_panels = []
```

#### 3.5.2: Implementar Métodos de Callback en MainWindow
**Ubicación**: Con otros métodos de gestión de paneles (~550)

**Agregar**:
```python
def on_global_search_panel_pinned(self, panel):
    """Callback cuando se ancla un panel de búsqueda global"""
    if panel not in self.pinned_global_search_panels:
        self.pinned_global_search_panels.append(panel)
        logger.info(f"Added global search panel {panel.panel_id} to pinned list")

        # Actualizar gestor de paneles si está abierto
        if hasattr(self, 'panels_manager_window') and self.panels_manager_window.isVisible():
            self.panels_manager_window.refresh_panels_list()

def on_global_search_panel_unpinned(self, panel):
    """Callback cuando se desancla un panel de búsqueda global"""
    if panel in self.pinned_global_search_panels:
        self.pinned_global_search_panels.remove(panel)
        logger.info(f"Removed global search panel {panel.panel_id} from pinned list")

        # Actualizar gestor de paneles si está abierto
        if hasattr(self, 'panels_manager_window') and self.panels_manager_window.isVisible():
            self.panels_manager_window.refresh_panels_list()
```

#### 3.5.3: Restaurar Paneles Globales al Inicio
**Ubicación**: En el método de inicialización o al final de `__init__()` (~200)

**Agregar**:
```python
def restore_pinned_global_search_panels(self):
    """Restaurar paneles de búsqueda global anclados desde la BD"""
    try:
        global_panels_data = self.controller.pinned_panels_manager.get_global_search_panels()

        for panel_data in global_panels_data:
            try:
                panel = self.controller.pinned_panels_manager.restore_global_search_panel(
                    panel_data['id'],
                    self.config_manager
                )

                # Configurar panel parent
                panel.setParent(None)  # Ventana independiente

                # Agregar a lista
                self.pinned_global_search_panels.append(panel)

                # Mostrar panel
                panel.show()

                logger.info(f"Restored global search panel: {panel_data['panel_name']}")

            except Exception as e:
                logger.error(f"Failed to restore global search panel {panel_data['id']}: {e}")

        logger.info(f"Restored {len(self.pinned_global_search_panels)} global search panels")

    except Exception as e:
        logger.error(f"Failed to restore pinned global search panels: {e}")

# Llamar al final de __init__:
# self.restore_pinned_global_search_panels()
```

#### 3.5.4: Actualizar Gestor de Paneles para Búsqueda Global
**Archivo**: `src/views/pinned_panels_manager_window.py`
**Ubicación**: Modificar método `load_panels()` (~250)

**Modificar**:
```python
def load_panels(self):
    """Cargar todos los paneles (categorías y búsqueda global)"""
    self.panels_list.clear()

    try:
        # Obtener estado del filtro
        status = self.status_filter_combo.currentData()
        include_archived = (status == "archived")

        # Cargar paneles de categorías
        category_panels = self.pinned_panels_manager.get_pinned_panels()

        # Cargar paneles de búsqueda global
        global_panels = self.pinned_panels_manager.get_global_search_panels(include_archived=include_archived)

        # Combinar y ordenar por fecha
        all_panels = []

        for panel in category_panels:
            if panel.get('is_active', True) != include_archived:
                panel['panel_type'] = 'category'
                all_panels.append(panel)

        for panel in global_panels:
            panel['panel_type'] = 'global_search'
            all_panels.append(panel)

        # Ordenar por fecha de creación (más reciente primero)
        all_panels.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Crear widgets
        for panel_data in all_panels:
            item_widget = PanelListItemWidget(panel_data, self)
            list_item = QListWidgetItem(self.panels_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.panels_list.addItem(list_item)
            self.panels_list.setItemWidget(list_item, item_widget)

        logger.info(f"Loaded {len(all_panels)} panels (categories + global search)")

    except Exception as e:
        logger.error(f"Failed to load panels: {e}")
```

#### 3.5.5: Actualizar `PanelListItemWidget` para Búsqueda Global
**Ubicación**: En el `__init__` de `PanelListItemWidget` (~320)

**Modificar la sección de información del panel**:
```python
# Información del panel
if panel_data.get('panel_type') == 'global_search':
    # Panel de búsqueda global
    import json
    info_parts = []

    if panel_data.get('search_query'):
        info_parts.append(f"Búsqueda: '{panel_data['search_query'][:30]}...'")

    filters = json.loads(panel_data.get('advanced_filters', '{}'))
    if filters:
        info_parts.append(f"{len(filters)} filtro(s)")

    state_filter = panel_data.get('state_filter', 'normal')
    if state_filter != 'normal':
        state_names = {"archived": "Archivados", "inactive": "Inactivos", "all": "Todos"}
        info_parts.append(f"Estado: {state_names.get(state_filter, state_filter)}")

    if not info_parts:
        info_parts.append("Sin filtros")

    info_text = " | ".join(info_parts)
    panel_icon = "🔍"
else:
    # Panel de categoría (código existente)
    category = self.parent().config_manager.get_category_by_id(panel_data['category_id'])
    info_text = f"{category.icon} {category.name}" if category else f"Categoría ID: {panel_data['category_id']}"
    panel_icon = category.icon if category else "📁"

self.info_label = QLabel(info_text)
```

#### 3.5.6: Actualizar `_focus_panel()` para Búsqueda Global
**Ubicación**: Modificar método existente (~380)

**Modificar**:
```python
def _focus_panel(self, panel_id: int):
    """Enfocar y activar un panel existente"""
    # Buscar en paneles de categorías
    for panel in self.main_window.pinned_panels:
        if panel.panel_id == panel_id:
            self._activate_panel(panel)
            return

    # Buscar en paneles de búsqueda global
    for panel in self.main_window.pinned_global_search_panels:
        if panel.panel_id == panel_id:
            self._activate_panel(panel)
            return

    logger.warning(f"Panel {panel_id} not found in active panels")

def _activate_panel(self, panel):
    """Activar y mostrar un panel"""
    if hasattr(panel, 'is_minimized') and panel.is_minimized:
        logger.info(f"Panel {panel.panel_id} is minimized, restoring...")
        panel.toggle_minimize()

    if not panel.isVisible():
        logger.info(f"Panel {panel.panel_id} is hidden, showing...")
        panel.show()

    panel.raise_()
    panel.activateWindow()
    panel.setFocus()
    logger.info(f"Panel {panel.panel_id} focused and activated")
```

### ✅ Criterios de Éxito
- ✅ Paneles globales se guardan en lista separada en MainWindow
- ✅ Paneles globales se restauran al inicio de la aplicación
- ✅ Gestor de paneles muestra paneles de categorías y búsqueda global juntos
- ✅ Distinción visual entre tipos de paneles en el gestor
- ✅ Operaciones (abrir, restaurar, eliminar) funcionan para ambos tipos

---

## FASE 3.6: Menú Contextual para Búsqueda Global

### 📋 Objetivo
Agregar menú contextual (click derecho) en paneles de búsqueda global anclados con opciones relevantes.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 3.6.1: Implementar `contextMenuEvent()`
**Ubicación**: Después de `show_panel_configuration()` (~850)

**Agregar**:
```python
def contextMenuEvent(self, event):
    """Mostrar menú contextual al hacer click derecho"""
    if not self.is_pinned:
        return  # Solo para paneles anclados

    from PyQt6.QtWidgets import QMenu

    menu = QMenu(self)
    menu.setStyleSheet("""
        QMenu {
            background-color: #2d2d2d;
            color: white;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 5px;
        }
        QMenu::item {
            padding: 8px 20px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #3d3d3d;
        }
    """)

    # Acción: Actualizar resultados
    refresh_action = menu.addAction("🔄 Actualizar resultados")
    refresh_action.triggered.connect(self.refresh_search_results)

    menu.addSeparator()

    # Acción: Guardar filtros actuales
    save_filters_action = menu.addAction("💾 Guardar filtros actuales")
    save_filters_action.triggered.connect(self.save_current_filters)

    # Acción: Limpiar todos los filtros
    clear_filters_action = menu.addAction("🧹 Limpiar todos los filtros")
    clear_filters_action.triggered.connect(self._clear_all_filters)

    menu.addSeparator()

    # Acción: Copiar todos los visibles
    copy_all_action = menu.addAction("📋 Copiar todos los items visibles")
    if hasattr(self, 'copy_all_button'):
        copy_all_action.triggered.connect(self.on_copy_all_visible)
    else:
        copy_all_action.setEnabled(False)

    # Acción: Crear lista con resultados
    create_list_action = menu.addAction("📝 Crear lista con resultados")
    if hasattr(self, 'create_list_button'):
        create_list_action.triggered.connect(self.on_create_list_clicked)
    else:
        create_list_action.setEnabled(False)

    menu.addSeparator()

    # Acción: Abrir gestor de paneles
    manager_action = menu.addAction("📌 Abrir gestor de paneles")
    manager_action.triggered.connect(self._open_panels_manager)

    # Acción: Configurar panel
    config_action = menu.addAction("⚙️ Configurar panel")
    config_action.triggered.connect(self.show_panel_configuration)

    menu.addSeparator()

    # Acción: Información del panel
    info_action = menu.addAction("ℹ️ Información del panel")
    info_action.triggered.connect(self._show_panel_info)

    menu.exec(event.globalPos())

def refresh_search_results(self):
    """Refrescar resultados de búsqueda"""
    logger.info("Refreshing search results...")
    if hasattr(self, 'perform_search'):
        self.perform_search()
    elif hasattr(self, 'search_bar'):
        self.search_bar.on_search_changed()

def save_current_filters(self):
    """Guardar configuración actual de filtros en BD"""
    if not self.is_pinned:
        logger.warning("Cannot save filters for non-pinned panel")
        return

    try:
        import json
        from src.core.pinned_panels_manager import PinnedPanelsManager

        panels_manager = PinnedPanelsManager(self.config_manager.db)

        # Actualizar en BD
        updates = {
            'search_query': self.search_bar.search_input.text().strip() if hasattr(self, 'search_bar') else '',
            'advanced_filters': json.dumps(self.current_filters) if hasattr(self, 'current_filters') else '{}',
            'state_filter': self.current_state_filter if hasattr(self, 'current_state_filter') else 'normal'
        }

        panels_manager.db.update_pinned_panel(self.panel_id, **updates)

        logger.info(f"Saved current filters for panel {self.panel_id}")

        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Filtros guardados",
            "La configuración actual de filtros se ha guardado correctamente."
        )

    except Exception as e:
        logger.error(f"Failed to save filters: {e}")

def _clear_all_filters(self):
    """Limpiar todos los filtros aplicados"""
    # Limpiar búsqueda
    if hasattr(self, 'search_bar') and self.search_bar:
        self.search_bar.search_input.clear()

    # Limpiar filtros avanzados
    if hasattr(self, 'current_filters'):
        self.current_filters = {}

    # Resetear filtro de estado
    if hasattr(self, 'current_state_filter'):
        self.current_state_filter = "normal"
        if hasattr(self, 'state_filter_combo'):
            self.state_filter_combo.setCurrentIndex(0)

    # Actualizar UI
    self.update_filter_badge()

    # Refrescar resultados
    self.refresh_search_results()

    logger.info("Cleared all filters")

def _open_panels_manager(self):
    """Abrir ventana de gestión de paneles"""
    if hasattr(self.parent(), 'show_pinned_panels_manager'):
        self.parent().show_pinned_panels_manager()

def _show_panel_info(self):
    """Mostrar información detallada del panel"""
    from PyQt6.QtWidgets import QMessageBox

    info_parts = [
        f"<b>Nombre:</b> {self.panel_name}",
        f"<b>ID:</b> {self.panel_id}",
        f"<b>Color:</b> {self.panel_color}",
        "<br><b>Configuración actual:</b>",
    ]

    # Filtros
    filters_info = self.get_current_filters_info()
    info_parts.append(filters_info.replace("\n", "<br>"))

    # Estadísticas
    visible_items = 0
    if hasattr(self, 'items_layout'):
        visible_items = self.items_layout.count() - 1  # -1 para stretch

    info_parts.append(f"<br><b>Items visibles:</b> {visible_items}")

    QMessageBox.information(
        self,
        "Información del Panel",
        "<br>".join(info_parts)
    )
```

### ✅ Criterios de Éxito
- ✅ Click derecho muestra menú contextual
- ✅ Todas las opciones funcionan correctamente
- ✅ Estilo del menú es consistente con la aplicación
- ✅ Solo aparece en paneles anclados
- ✅ Feedback visual apropiado para cada acción

---

## 📊 RESUMEN DEL PLAN 3

### Funcionalidades Implementadas
1. ✅ **Botón de Anclado (Pin)**: Guardar panel de búsqueda global como panel persistente
2. ✅ **Persistencia en BD**: Guardar/restaurar configuración completa de paneles
3. ✅ **Botón de Minimizar**: Colapsar/expandir paneles anclados
4. ✅ **Botón de Configuración**: Cambiar nombre y color de paneles
5. ✅ **Integración MainWindow**: Gestión centralizada de paneles globales
6. ✅ **Gestor de Paneles**: Visualización unificada de categorías y búsqueda global
7. ✅ **Menú Contextual**: Click derecho con opciones rápidas

### Archivos Modificados
- `src/views/global_search_panel.py` (principal, ~500 líneas agregadas)
- `src/core/pinned_panels_manager.py` (~150 líneas agregadas)
- `src/database/db_manager.py` (migración de esquema)
- `src/views/main_window.py` (~100 líneas agregadas)
- `src/views/pinned_panels_manager_window.py` (~50 líneas modificadas)

### Líneas de Código Aproximadas
- **Agregadas**: ~800 líneas
- **Modificadas**: ~100 líneas

### Base de Datos - Campos Agregados
Tabla `pinned_panels`:
- `panel_type` (TEXT): 'category' | 'global_search'
- `search_query` (TEXT): Query de búsqueda para paneles globales
- `advanced_filters` (TEXT): JSON de filtros avanzados
- `state_filter` (TEXT): 'normal' | 'archived' | 'inactive' | 'all'

### Testing Recomendado

#### Pruebas Unitarias
1. Anclar panel de búsqueda global con diferentes filtros
2. Verificar persistencia en BD después de reiniciar app
3. Restaurar panel y verificar todos los filtros
4. Minimizar/restaurar panel anclado
5. Cambiar configuración (nombre, color) de panel
6. Desanclar panel y verificar que se archiva (no se borra)
7. Restaurar panel archivado desde gestor

#### Pruebas de Integración
1. Crear múltiples paneles globales anclados simultáneos
2. Mezclar paneles de categorías y búsqueda global
3. Verificar interacción con gestor de paneles
4. Probar menú contextual en todos los estados
5. Verificar que desanclar no afecta a otros paneles

#### Pruebas de UI
1. Verificar visibilidad de botones según estado (anclado/desanclado)
2. Comprobar tooltips y feedback visual
3. Verificar estilos y colores personalizados
4. Probar diálogos de configuración
5. Verificar comportamiento de minimizado

### Consideraciones de Rendimiento
- Caché de resultados de búsqueda para paneles anclados
- Debouncing en actualizaciones de filtros (300ms)
- Lazy loading de items en paneles grandes
- Limitación de paneles anclados simultáneos (máximo 10 recomendado)

### Posibles Extensiones Futuras
- Atajos de teclado personalizados por panel (Ctrl+1, Ctrl+2, etc.)
- Compartir configuración de paneles entre usuarios
- Templates de búsqueda predefinidos
- Exportar/importar paneles anclados
- Widgets de panel adicionales (gráficos, estadísticas)

---

## 🚀 Orden de Implementación

Para implementar este plan de manera óptima, seguir este orden:

1. **FASE 3.1**: Botón de anclado - Base de funcionalidad
2. **FASE 3.2**: Persistencia - Guardar/restaurar de BD
3. **FASE 3.5**: Integración MainWindow - Gestión centralizada
4. **FASE 3.3**: Botón minimizar - Funcionalidad adicional
5. **FASE 3.4**: Botón configuración - Personalización
6. **FASE 3.6**: Menú contextual - Accesos rápidos

Este orden asegura que cada fase construye sobre la anterior y minimiza refactorización.

---

## 📋 Checklist Final

Antes de considerar el PLAN 3 completo, verificar:

- [ ] Todos los tests pasan
- [ ] No hay errores en logs
- [ ] Migración de BD ejecuta sin problemas
- [ ] UI es responsive y no hay lags
- [ ] Código está documentado
- [ ] No hay memory leaks (verificar con profiler)
- [ ] Funcionalidad probada en Windows 10 y 11
- [ ] Integración con PLAN 1 y PLAN 2 funciona correctamente
