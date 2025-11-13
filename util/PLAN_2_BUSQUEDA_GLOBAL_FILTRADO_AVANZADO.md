# PLAN 2: Filtrado y Organización Avanzada - Panel de Búsqueda Global

**Objetivo**: Implementar capacidades avanzadas de filtrado y organización que permitan a los usuarios gestionar mejor los resultados de búsqueda global, incluyendo acceso a items archivados y creación de listas desde resultados.

**Tiempo estimado**: 4-5 horas
**Dificultad**: ⭐⭐⭐☆☆ (Media)
**Prioridad**: 🔥🔥🔥🔥☆ (Alta)

**Prerequisitos**: PLAN 1 completado

---

## FASE 2.1: Implementar Filtro de Estado (Normal/Archivados/Inactivos/Todos)

### 📋 Objetivo
Agregar un ComboBox que permita filtrar items por su estado: Normal (activos), Archivados, Inactivos o ver Todos. Esto permite acceder a items archivados desde la búsqueda global.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 2.1.1: Agregar Variable de Estado en `__init__()`
**Línea**: Después de `self.current_filters = {}` (~39)

**Agregar**:
```python
self.current_state_filter = "normal"  # Filtro de estado actual: normal, archived, inactive, all
```

#### 2.1.2: Crear Widget ComboBox de Filtro de Estado
**Ubicación**: Después de crear `self.copy_all_button` (después de completar PLAN 1)

**Agregar**:
```python
# ComboBox para filtro de estado
self.state_filter_combo = QComboBox()
self.state_filter_combo.addItem("📄 Normal", "normal")
self.state_filter_combo.addItem("📦 Archivados", "archived")
self.state_filter_combo.addItem("⏸️ Inactivos", "inactive")
self.state_filter_combo.addItem("📋 Todos", "all")
self.state_filter_combo.setCurrentIndex(0)  # Default: Normal
self.state_filter_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
self.state_filter_combo.setStyleSheet("""
    QComboBox {
        background-color: #252525;
        color: #ffffff;
        border: 1px solid #3d3d3d;
        border-radius: 4px;
        padding: 6px 12px;
        font-size: 10pt;
        min-width: 120px;
    }
    QComboBox:hover {
        border: 1px solid #f093fb;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #ffffff;
        margin-right: 5px;
    }
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #3d3d3d;
        selection-background-color: #f093fb;
    }
""")
self.state_filter_combo.setToolTip("Filtrar items por estado")
self.state_filter_combo.currentIndexChanged.connect(self.on_state_filter_changed)
filters_button_layout.addWidget(self.state_filter_combo)
```

#### 2.1.3: Implementar Método `on_state_filter_changed()`
**Ubicación**: Después de `on_copy_all_visible()` (~520)

**Agregar**:
```python
def on_state_filter_changed(self, index):
    """Handle cuando cambia el filtro de estado"""
    state_filter = self.state_filter_combo.itemData(index)
    self.current_state_filter = state_filter
    logger.info(f"State filter changed to: {state_filter}")

    # Re-aplicar búsqueda con nuevo filtro de estado
    current_query = self.search_bar.search_input.text()
    self.on_search_changed(current_query)

    # Update filter badge
    self.update_filter_badge()
```

#### 2.1.4: Crear Método `filter_items_by_state()`
**Ubicación**: Después de `on_state_filter_changed()` (~535)

**Agregar**:
```python
def filter_items_by_state(self, items):
    """Filtrar items por estado (activo/archivado/inactivo)

    Args:
        items: Lista de items a filtrar

    Returns:
        Lista filtrada de items
    """
    if self.current_state_filter == "all":
        # Mostrar todos los items
        return items

    filtered = []
    for item in items:
        # Verificar estado del item en la base de datos
        if self.db_manager:
            item_data = self.db_manager.get_item(int(item.id))
            if item_data:
                is_active = item_data.get('is_active', True)
                is_archived = item_data.get('is_archived', False)

                # Aplicar filtro según selección
                if self.current_state_filter == "normal":
                    # Solo items activos y no archivados
                    if is_active and not is_archived:
                        filtered.append(item)
                elif self.current_state_filter == "archived":
                    # Solo items archivados
                    if is_archived:
                        filtered.append(item)
                elif self.current_state_filter == "inactive":
                    # Solo items inactivos (no activos y no archivados)
                    if not is_active and not is_archived:
                        filtered.append(item)

    return filtered
```

#### 2.1.5: Integrar Filtro de Estado en `on_search_changed()`
**Modificar método `on_search_changed()` (~371)**

**Agregar después de aplicar filtros avanzados** (~378):
```python
# Aplicar filtros avanzados primero
filtered_items = self.filter_engine.apply_filters(self.all_items, self.current_filters)
logger.debug(f"Items after advanced filters: {len(filtered_items)}")

# Aplicar filtro de estado
filtered_items = self.filter_items_by_state(filtered_items)
logger.debug(f"Items after state filter: {len(filtered_items)}")

# Luego aplicar búsqueda si hay query
# ... resto del código
```

#### 2.1.6: Actualizar `update_filter_badge()` para incluir filtro de estado
**Modificar método `update_filter_badge()`**

**Agregar después de contar filtros avanzados**:
```python
# Contar filtro de estado (si no es 'normal')
if self.current_state_filter != "normal":
    filter_count += 1

# ... resto del código

# En el tooltip, agregar:
if self.current_state_filter != "normal":
    tooltip_parts.append(f"Estado: {self.current_state_filter}")
```

### ✅ Criterios de Éxito
- ✅ ComboBox aparece en la barra de filtros
- ✅ Filtra correctamente por cada estado (Normal/Archivados/Inactivos/Todos)
- ✅ Badge de filtros cuenta el filtro de estado si no es "normal"
- ✅ Se puede acceder a items archivados
- ✅ Filtro de estado se combina correctamente con otros filtros

---

## FASE 2.2: Implementar Botón "Crear Lista" desde Búsqueda Global

### 📋 Objetivo
Permitir crear listas avanzadas utilizando los items visibles en la búsqueda global, con un diálogo para seleccionar la categoría destino.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 2.2.1: Agregar Referencia a ListController en `__init__()`
**Modificar firma del `__init__()` (~32)**

**Agregar parámetro**:
```python
def __init__(self, db_manager=None, config_manager=None, list_controller=None, parent=None):
    super().__init__(parent)
    self.db_manager = db_manager
    self.config_manager = config_manager
    self.list_controller = list_controller  # Agregar esta línea
    # ... resto del código
```

#### 2.2.2: Agregar Botón "Crear Lista"
**Ubicación**: Después de `self.state_filter_combo` (en FASE 2.1)

**Agregar**:
```python
# Botón "Crear Lista"
self.create_list_button = QPushButton("➕ Crear Lista")
self.create_list_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
self.create_list_button.setStyleSheet("""
    QPushButton {
        background-color: #252525;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 10pt;
        font-weight: bold;
        text-align: left;
    }
    QPushButton:hover {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #ff6ec7,
            stop:1 #7873f5
        );
    }
    QPushButton:pressed {
        background-color: #252525;
    }
    QPushButton:disabled {
        background-color: #1a1a1a;
        color: #666666;
    }
""")
self.create_list_button.setToolTip("Crear lista avanzada desde los items visibles")
self.create_list_button.clicked.connect(self.on_create_list_clicked)
filters_button_layout.addWidget(self.create_list_button)
```

#### 2.2.3: Implementar Método `on_create_list_clicked()`
**Ubicación**: Después de `filter_items_by_state()` (~580)

**Agregar**:
```python
def on_create_list_clicked(self):
    """Abrir diálogo para crear lista desde items visibles"""
    if not self.list_controller:
        logger.warning("Cannot create list: no list controller available")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(
            self,
            "Error",
            "Funcionalidad de listas no disponible"
        )
        return

    # Obtener items visibles
    visible_items = []
    for i in range(self.items_layout.count() - 1):
        widget = self.items_layout.itemAt(i).widget()
        if widget and hasattr(widget, 'item'):
            visible_items.append(widget.item)

    if not visible_items:
        logger.warning("No visible items to create list from")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(
            self,
            "Sin Items",
            "No hay items visibles para crear una lista"
        )
        return

    # Abrir diálogo de selección de categoría y creación de lista
    from views.dialogs.create_list_from_search_dialog import CreateListFromSearchDialog

    creator_dialog = CreateListFromSearchDialog(
        items=visible_items,
        db_manager=self.db_manager,
        config_manager=self.config_manager,
        list_controller=self.list_controller,
        parent=self
    )

    creator_dialog.list_created.connect(self.on_list_created_from_dialog)
    creator_dialog.exec()
```

#### 2.2.4: Implementar Método `on_list_created_from_dialog()`
**Ubicación**: Después de `on_create_list_clicked()` (~625)

**Agregar**:
```python
def on_list_created_from_dialog(self, list_name: str, category_id: int, item_ids: list):
    """Handle cuando se crea una lista desde el diálogo"""
    logger.info(f"List '{list_name}' created in category {category_id} with {len(item_ids)} items")

    from PyQt6.QtWidgets import QMessageBox
    QMessageBox.information(
        self,
        "Lista Creada",
        f"Lista '{list_name}' creada exitosamente con {len(item_ids)} items"
    )
```

#### 2.2.5: Crear Diálogo `CreateListFromSearchDialog`
**Nuevo archivo**: `src/views/dialogs/create_list_from_search_dialog.py`

**Contenido completo**:
```python
"""
Diálogo para crear lista desde búsqueda global
Permite seleccionar categoría destino y configurar la lista
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QComboBox, QListWidget,
                             QListWidgetItem, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class CreateListFromSearchDialog(QDialog):
    """Diálogo para crear lista desde búsqueda global"""

    # Señal emitida cuando se crea la lista: (list_name, category_id, item_ids)
    list_created = pyqtSignal(str, int, list)

    def __init__(self, items, db_manager, config_manager, list_controller, parent=None):
        super().__init__(parent)
        self.items = items
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.list_controller = list_controller

        self.init_ui()

    def init_ui(self):
        """Inicializar UI del diálogo"""
        self.setWindowTitle("Crear Lista desde Búsqueda")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        # No cerrar app al cerrar diálogo
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)

        layout = QVBoxLayout(self)

        # Título
        title = QLabel("📋 Crear Lista Avanzada")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Nombre de la lista
        name_group = QGroupBox("Nombre de la Lista")
        name_layout = QVBoxLayout(name_group)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Comandos Git Útiles")
        name_layout.addWidget(self.name_input)

        layout.addWidget(name_group)

        # Selección de categoría
        category_group = QGroupBox("Categoría Destino")
        category_layout = QVBoxLayout(category_group)

        self.category_combo = QComboBox()
        self.load_categories()
        category_layout.addWidget(self.category_combo)

        layout.addWidget(category_group)

        # Items a incluir
        items_group = QGroupBox(f"Items a Incluir ({len(self.items)} items)")
        items_layout = QVBoxLayout(items_group)

        # Checkbox para seleccionar todos
        self.select_all_checkbox = QCheckBox("Seleccionar todos")
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        items_layout.addWidget(self.select_all_checkbox)

        # Lista de items
        self.items_list = QListWidget()
        for item in self.items:
            category_info = f"[{item.category_name}]" if hasattr(item, 'category_name') else ""
            list_item = QListWidgetItem(f"{category_info} {item.label}")
            list_item.setData(Qt.ItemDataRole.UserRole, item.id)
            list_item.setCheckState(Qt.CheckState.Checked)
            self.items_list.addItem(list_item)

        items_layout.addWidget(self.items_list)
        layout.addWidget(items_group)

        # Botones
        buttons_layout = QHBoxLayout()

        create_btn = QPushButton("✅ Crear Lista")
        create_btn.clicked.connect(self.create_list)
        buttons_layout.addWidget(create_btn)

        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        # Estilos
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #00aaff;
            }
            QLineEdit, QComboBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #00aaff;
            }
        """)

    def load_categories(self):
        """Cargar categorías disponibles"""
        if not self.config_manager:
            return

        categories = self.config_manager.get_all_categories()
        for category in categories:
            self.category_combo.addItem(
                f"{category.icon} {category.name}",
                category.id
            )

    def toggle_select_all(self, state):
        """Seleccionar/deseleccionar todos los items"""
        check_state = Qt.CheckState.Checked if state == Qt.CheckState.Checked.value else Qt.CheckState.Unchecked
        for i in range(self.items_list.count()):
            item = self.items_list.item(i)
            item.setCheckState(check_state)

    def create_list(self):
        """Crear la lista con los items seleccionados"""
        # Validar nombre
        list_name = self.name_input.text().strip()
        if not list_name:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Debes proporcionar un nombre para la lista")
            return

        # Obtener categoría seleccionada
        category_id = self.category_combo.currentData()
        if not category_id:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Debes seleccionar una categoría")
            return

        # Obtener items seleccionados
        selected_item_ids = []
        for i in range(self.items_list.count()):
            item = self.items_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                item_id = item.data(Qt.ItemDataRole.UserRole)
                selected_item_ids.append(item_id)

        if not selected_item_ids:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Debes seleccionar al menos un item")
            return

        # Crear lista usando ListController
        try:
            self.list_controller.create_list_from_items(
                list_name=list_name,
                category_id=int(category_id),
                item_ids=[int(id) for id in selected_item_ids]
            )

            # Emitir señal
            self.list_created.emit(list_name, int(category_id), [int(id) for id in selected_item_ids])

            # Cerrar diálogo
            self.accept()

        except Exception as e:
            logger.error(f"Error creating list: {e}", exc_info=True)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error al crear lista: {e}")
```

#### 2.2.6: Actualizar `main_window.py` para pasar `list_controller`
**Modificar creación de `GlobalSearchPanel` en `main_window.py`**

**Buscar** (~411):
```python
self.global_search_panel = GlobalSearchPanel(
    db_manager=db_manager,
    config_manager=self.config_manager
)
```

**Reemplazar con**:
```python
self.global_search_panel = GlobalSearchPanel(
    db_manager=db_manager,
    config_manager=self.config_manager,
    list_controller=self.controller.list_controller
)
```

### ✅ Criterios de Éxito
- ✅ Botón "Crear Lista" aparece en la barra de filtros
- ✅ Diálogo muestra todos los items visibles
- ✅ Se puede seleccionar categoría destino
- ✅ Se puede seleccionar qué items incluir
- ✅ Lista se crea correctamente en la base de datos
- ✅ Feedback visual de éxito/error

---

## FASE 2.3: Mejorar Motor de Búsqueda

### 📋 Objetivo
Optimizar el motor de búsqueda para hacerlo más rápido y relevante.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 2.3.1: Agregar Búsqueda por Nombre de Categoría
**Modificar `on_search_changed()` (~387)**

**Agregar en el loop de búsqueda**:
```python
# Search in category name
if hasattr(item, 'category_name') and item.category_name:
    if query_lower in item.category_name.lower():
        search_results.append(item)
        continue
```

#### 2.3.2: Implementar Debouncing para Búsqueda
**Agregar en `__init__()` después de crear `search_engine`**:
```python
# Timer para debouncing de búsqueda
self.search_timer = QTimer()
self.search_timer.setSingleShot(True)
self.search_timer.timeout.connect(self._perform_search)
self.pending_search_query = ""
```

**Modificar `on_search_changed()`**:
```python
def on_search_changed(self, query: str):
    """Handle search query change with debouncing"""
    self.pending_search_query = query
    self.search_timer.start(300)  # 300ms debounce

def _perform_search(self):
    """Perform the actual search after debounce"""
    query = self.pending_search_query
    logger.debug(f"_perform_search called with query='{query}'")
    # ... resto del código actual de on_search_changed
```

#### 2.3.3: Agregar Import de QTimer
**Línea**: ~5

**Modificar**:
```python
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QEvent, QTimer
```

### ✅ Criterios de Éxito
- ✅ Búsqueda incluye nombre de categoría
- ✅ Debouncing funciona (no busca en cada tecla)
- ✅ Búsqueda es más rápida y fluida
- ✅ Resultados son relevantes

---

## 📊 RESUMEN DEL PLAN 2

### Funcionalidades Implementadas
1. ✅ **Filtro de Estado**: Normal/Archivados/Inactivos/Todos
2. ✅ **Crear Lista**: Desde resultados de búsqueda global
3. ✅ **Búsqueda Mejorada**: Con debouncing y búsqueda en categorías

### Archivos Modificados
- `src/views/global_search_panel.py`
- `src/views/main_window.py` (integración ListController)

### Archivos Nuevos
- `src/views/dialogs/create_list_from_search_dialog.py`

### Líneas de Código Aproximadas
- **Agregadas**: ~350 líneas
- **Modificadas**: ~20 líneas

### Testing Recomendado
1. Probar filtro de estado con diferentes tipos de items
2. Crear listas desde búsqueda global con diferentes categorías
3. Verificar debouncing de búsqueda
4. Probar búsqueda por nombre de categoría
5. Verificar combinación de todos los filtros

---

## 🚀 Siguientes Pasos
Después de completar el **PLAN 2**, continuar con:
- **PLAN 3**: Sistema de Paneles Anclados para Búsqueda Global
