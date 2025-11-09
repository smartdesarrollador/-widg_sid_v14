PROMPT GENERADO

Genera un archivo JSON para Widget Sidebar siguiendo EXACTAMENTE esta estructura:

{
"category_id": 26,
"defaults": {
"type": "TEXT",
"tags": "lista_test",
"is_favorite": 0,
"is_sensitive": 0,
"is_list": 1,
"list_group": "lista_test_7"
},
"items": [
{
"label": "nombre corto descriptivo del paso",
"content": "comando/url/texto completo aquí",
"description": "descripción opcional del item"
},
{
"label": "otro paso",
"content": "otro comando/contenido",
"description": "otra descripción"
}
]
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTEXTO DE LA TAREA:
📁 Categoría: new (ID: 26)
📝 Tipo de items: TEXT (Texto plano, notas, descripciones generales)
🏷️ Tags por defecto: "lista_test"
⭐ Favoritos por defecto: NO
🔒 Sensibles por defecto: NO
📝 Lista secuencial: SÍ - Grupo "lista_test_7" (los items se crearán en orden)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REGLAS IMPORTANTES:

1. ESTRUCTURA:

   - Cada item DEBE tener "label" (max 200 caracteres) y "content" (requerido)
   - El "label" debe ser descriptivo pero conciso
   - El "content" debe ser el comando/url/texto completo y funcional

2. PERSONALIZACIÓN POR ITEM:

   - Puedes sobreescribir "type", "tags", "is_favorite", "is_sensitive" en items individuales
   - Ejemplo: si un item específico necesita ser CODE aunque el default sea TEXT
   - Los valores individuales tienen prioridad sobre "defaults"
   - IMPORTANTE: Como se creará una lista, NO necesitas incluir "is_list" ni "list_group" en cada item
   - El sistema asignará automáticamente el orden secuencial (orden_lista: 0, 1, 2, ...)
   - Los items se ejecutarán/mostrarán en el orden en que aparezcan en el array

3. CANTIDAD:

   - Genera entre 1 y 50 items según la complejidad del contexto
   - Para tareas simples: 5-10 items
   - Para tareas complejas: 15-30 items
   - Para flujos completos: 30-50 items

4. CALIDAD DEL CONTENIDO:

   - Para tipo CODE: comandos funcionales y completos (no pseudocódigo)
   - Para tipo URL: URLs completas y válidas (https://...)
   - Para tipo PATH: rutas absolutas o relativas válidas
   - Para tipo TEXT: texto útil y relevante

5. FORMATO JSON:
   - NO agregues comentarios en el JSON (no es válido)
   - NO agregues texto antes o después del JSON
   - USA comillas dobles, NO comillas simples
   - Escapa caracteres especiales correctamente (\n, \t, \", etc.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LO QUE EL USUARIO NECESITA:
Dame los pasos de una receta para realizar una postre cheesecake

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANTE: Responde ÚNICAMENTE con el JSON válido, sin texto adicional antes o después.
El JSON debe empezar con { y terminar con }.
