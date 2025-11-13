# PLAN 1: Mejoras Visuales y UX Básicas - Panel de Búsqueda Global

**Objetivo**: Implementar mejoras rápidas de interfaz y experiencia de usuario que mejoren significativamente la usabilidad del panel de búsqueda global sin cambios arquitectónicos complejos.

**Tiempo estimado**: 2-3 horas
**Dificultad**: ⭐⭐☆☆☆ (Baja-Media)
**Prioridad**: 🔥🔥🔥🔥🔥 (Crítica)

---

## FASE 1.1: Implementar Scroll Horizontal

### 📋 Objetivo
Permitir que el panel de búsqueda global muestre barras de desplazamiento horizontal cuando los items tienen contenido largo que excede el ancho del panel.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 1.1.1: Habilitar Scroll Horizontal en QScrollArea
**Línea**: ~209

**Código Actual**:
```python
scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
```

**Código Nuevo**:
```python
scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
```

#### 1.1.2: Configurar Política de Tamaño del Contenedor
**Línea**: Después de crear `self.items_container` (~233)

**Agregar**:
```python
# Configurar política de tamaño para permitir expansión horizontal
from PyQt6.QtWidgets import QSizePolicy
self.items_container.setSizePolicy(
    QSizePolicy.Policy.MinimumExpanding,  # Horizontal: puede expandirse
    QSizePolicy.Policy.Preferred          # Vertical: tamaño preferido
)
```

#### 1.1.3: Actualizar Import
**Línea**: ~4

**Modificar**:
```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QSizePolicy
```

### ✅ Criterios de Éxito
- ✅ Items con contenido largo muestran scroll horizontal
- ✅ Items con contenido corto no muestran scroll horizontal
- ✅ La experiencia de scroll es fluida
- ✅ El scroll vertical sigue funcionando correctamente

---

## FASE 1.2: Implementar Badge de Filtros Activos

### 📋 Objetivo
Mostrar un badge visual en el header del panel que indique cuántos filtros están activos actualmente, proporcionando feedback visual inmediato al usuario.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 1.2.1: Agregar Widget de Badge en el Header
**Línea**: Después de crear `self.header_label` (~125)

**Agregar**:
```python
# Filter badge (shows number of active filters)
self.filter_badge = QLabel()
self.filter_badge.setVisible(False)
self.filter_badge.setStyleSheet("""
    QLabel {
        background-color: #ff6b00;
        color: white;
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 9pt;
        font-weight: bold;
    }
""")
self.filter_badge.setToolTip("Filtros activos")
header_layout.addWidget(self.filter_badge)
```

#### 1.2.2: Crear Método `update_filter_badge()`
**Ubicación**: Después del método `on_filters_cleared()` (~428)

**Agregar**:
```python
def update_filter_badge(self):
    """Actualizar badge de filtros activos en el header"""
    filter_count = 0

    # Contar filtros avanzados activos
    if self.current_filters:
        filter_count += len(self.current_filters)

    # Contar búsqueda activa
    if hasattr(self, 'search_bar') and self.search_bar:
        if hasattr(self.search_bar, 'search_input'):
            search_text = self.search_bar.search_input.text().strip()
            if search_text:
                filter_count += 1

    # Mostrar/ocultar badge según la cantidad de filtros
    if filter_count > 0:
        self.filter_badge.setText(f"🔍 {filter_count}")
        self.filter_badge.setVisible(True)
        tooltip_parts = []
        if self.current_filters:
            tooltip_parts.append(f"{len(self.current_filters)} filtro(s) avanzado(s)")
        if hasattr(self, 'search_bar') and self.search_bar and self.search_bar.search_input.text().strip():
            tooltip_parts.append(f"Búsqueda activa")
        self.filter_badge.setToolTip(" | ".join(tooltip_parts))
    else:
        self.filter_badge.setVisible(False)
```

#### 1.2.3: Llamar a `update_filter_badge()` en Eventos Relevantes
**Modificar métodos**:

1. `on_search_changed()` - Al final del método (~410):
```python
# Update filter badge when search changes
self.update_filter_badge()
```

2. `on_filters_changed()` - Al inicio (~415):
```python
# Update filter badge
self.update_filter_badge()
```

3. `on_filters_cleared()` - Al inicio (~423):
```python
# Update filter badge
self.update_filter_badge()
```

### ✅ Criterios de Éxito
- ✅ Badge aparece cuando hay filtros o búsqueda activa
- ✅ Badge muestra el número correcto de filtros
- ✅ Badge desaparece cuando se limpian todos los filtros
- ✅ Tooltip del badge muestra detalles de filtros activos
- ✅ Estilo visual es consistente con el tema de la aplicación

---

## FASE 1.3: Implementar Botón "Copiar Todos los Visibles"

### 📋 Objetivo
Agregar funcionalidad para copiar al portapapeles el contenido de todos los items visibles después de aplicar filtros y búsqueda.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 1.3.1: Agregar Botón en la Barra de Filtros
**Línea**: Después del botón de filtros avanzados (~191)

**Agregar**:
```python
# Botón "Copiar Todos los Visibles"
self.copy_all_button = QPushButton("📋 Copiar Todos")
self.copy_all_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
self.copy_all_button.setStyleSheet("""
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
            stop:0 #00ff88,
            stop:1 #00ccff
        );
    }
    QPushButton:pressed {
        background-color: #252525;
    }
""")
self.copy_all_button.setToolTip("Copiar el contenido de todos los items visibles actualmente")
self.copy_all_button.clicked.connect(self.on_copy_all_visible)
filters_button_layout.addWidget(self.copy_all_button)
```

#### 1.3.2: Implementar Método `on_copy_all_visible()`
**Ubicación**: Después de `update_filter_badge()` (~460)

**Agregar**:
```python
def on_copy_all_visible(self):
    """Copiar al portapapeles el contenido de todos los items visibles"""
    # Obtener todos los widgets de items actualmente en el layout
    visible_items = []
    for i in range(self.items_layout.count() - 1):  # -1 para excluir el stretch
        widget = self.items_layout.itemAt(i).widget()
        if widget and hasattr(widget, 'item'):
            visible_items.append(widget.item)

    if not visible_items:
        logger.warning("No visible items to copy")
        return

    # Construir texto para copiar
    content_parts = []
    for item in visible_items:
        # Formato: [Categoría] Label: Contenido
        category_info = f"[{item.category_icon} {item.category_name}]" if hasattr(item, 'category_name') else ""
        item_text = f"{category_info} {item.label}: {item.content}"
        content_parts.append(item_text)

    # Copiar al portapapeles
    full_content = "\n".join(content_parts)

    try:
        import pyperclip
        pyperclip.copy(full_content)
        logger.info(f"Copied {len(visible_items)} items to clipboard")

        # Feedback visual (opcional)
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Copiado",
            f"Se copiaron {len(visible_items)} item(s) al portapapeles"
        )
    except Exception as e:
        logger.error(f"Error copying to clipboard: {e}")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(
            self,
            "Error",
            f"Error al copiar al portapapeles: {e}"
        )
```

### ✅ Criterios de Éxito
- ✅ Botón aparece en la barra de filtros
- ✅ Copia correctamente todos los items visibles
- ✅ Incluye información de categoría en el formato copiado
- ✅ Muestra feedback visual después de copiar
- ✅ Maneja errores correctamente

---

## FASE 1.4: Ajustes de Estilos y Mejoras de UX

### 📋 Objetivo
Mejorar la consistencia visual y la experiencia de usuario del panel de búsqueda global.

### 🔧 Archivos a Modificar
- `src/views/global_search_panel.py`

### 📝 Tareas

#### 1.4.1: Mejorar Estilos del Scrollbar Horizontal
**Línea**: En el stylesheet de `scroll_area` (~211)

**Agregar**:
```python
QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 10px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #555555;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #666666;
}
```

#### 1.4.2: Agregar Contador de Items Visibles
**Ubicación**: En el método `display_items()` (~335)

**Modificar título del header**:
```python
def display_items(self, items):
    """Display a list of items"""
    logger.info(f"Displaying {len(items)} items")

    # Actualizar título con contador
    self.header_label.setText(f"🌐 Búsqueda Global ({len(items)} items)")

    # Clear existing items
    self.clear_items()

    # ... resto del código
```

#### 1.4.3: Mejorar Atributo WA_QuitOnClose
**Línea**: Después de `setWindowOpacity()` (~85)

**Agregar**:
```python
# No cerrar la aplicación al cerrar esta ventana
self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
```

### ✅ Criterios de Éxito
- ✅ Scrollbar horizontal tiene estilo consistente con el vertical
- ✅ Header muestra contador de items visibles
- ✅ Cerrar ventana no cierra la aplicación
- ✅ Estilos son consistentes con el tema futurista

---

## 📊 RESUMEN DEL PLAN 1

### Funcionalidades Implementadas
1. ✅ **Scroll Horizontal**: Para items con contenido largo
2. ✅ **Badge de Filtros**: Feedback visual de filtros activos
3. ✅ **Copiar Todos**: Exportar resultados de búsqueda
4. ✅ **Mejoras de UX**: Contador de items, estilos mejorados

### Archivos Modificados
- `src/views/global_search_panel.py` (único archivo)

### Líneas de Código Aproximadas
- **Agregadas**: ~150 líneas
- **Modificadas**: ~10 líneas

### Testing Recomendado
1. Probar scroll horizontal con items de diferentes longitudes
2. Verificar badge con diferentes combinaciones de filtros
3. Copiar todos los items y verificar formato
4. Verificar contador de items en diferentes búsquedas
5. Probar cierre de ventana

---

## 🚀 Siguientes Pasos
Después de completar el **PLAN 1**, continuar con:
- **PLAN 2**: Filtrado y Organización Avanzada
- **PLAN 3**: Sistema de Paneles Anclados para Búsqueda Global
