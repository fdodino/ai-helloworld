# Guía para agentes de IA

<persona>
- **Quién soy:** Desarrollador senior que está aprendiendo a desarrollar agentes de IA.
- Misión de este repositorio: registrar el aprendizaje del libro "Common Sense Guide to AI Engineering"
</persona>

<coding_standards>
  <logic_and_design>
    - **Abstracciones claras:** Responsabilidad única y bien definida.
    - **Declaratividad:** Usar listas por comprensión, en segunda medida funciones de orden superior (`map`, `filter`, `reduce`) sobre loops imperativos (`for`, `break`, `continue`).
    - **Simplicidad:** Soluciones directas antes que complejidad innecesaria. Evitar el "miedo al booleano" (ej: preferir `return x === y` en lugar de `if (x === y) return true else return false`).
    - **While**: muchas veces hay que usar whiles, en ese caso tratar de partir en funciones más chicas, evitar la repetición cuando hay que hacer un do-while, buscar que el while apunte a una variable que pueda luego modificarse antes de volverse a llamar.
  </logic_and_design>

  <style_and_clean_code>
    - **Nombres representativos:** Descriptivos y claros. No usar variables de una letra o nombres genéricos.
    - **DRY (Don't Repeat Yourself):** No duplicar lógica. Reutilizar definiciones de otros archivos.
    - **Cohesión:** Funciones cortas. Si es larga, dividir (divide y vencerás).
    - **Comentarios:** Explicar el "porqué", no el "qué". No agregar comentarios inline en internas. Evitar comentarios inútiles. Prohibido usar comentarios inline en el medio de un método. Se permiten y deben preservarse los comentarios que describan el propósito o comportamiento de un método o test.
    - **Evitar negaciones innecesarias:** Favorecer nombres de funciones y variables que permitan lógica positiva. Evitar la doble negación (ej: facilitar `isValid` o `isUnsafe` para evitar `not isInvalid` o `not isSafe`).
    - **Consistencia:** Mantener estilo uniforme en todo el proyecto.
  </style_and_clean_code>

  <type_safety_and_errors>
    - **Tipado estricto:** Prohibido usar `any` / `never`. Usar `unknown` o tipos específicos/genéricos.
    - **Manejo de errores:** Usar excepciones solo para casos excepcionales. "Fail fast": fallar lo antes posible. **Nunca dejar catch vacío**.
  </type_safety_and_errors>

<workflow_constraints>
  - **Idioma:** Código y comentarios en **Inglés**. Documentación en **Inglés**.
</workflow_constraints>

<ai_interaction_protocol>
  - **No ejecutar scripts sin preguntar**: no ejecutar comandos de git, ni pnpm. Preguntar ANTES para este tipo de comandos. Sí podés hacer `ls` o `cat` para explorar el código.
  - **Prioridad LSP:** Priorizar el uso de herramientas de Language Server Protocol (LSP) para búsquedas semánticas y navegación sobre el uso de `grep` (búsqueda de texto plano).
  - **Scope acotado:** Hacé solo lo que se te pide. No refactorices código no relacionado.
  - **Leé antes de actuar:** Entendé el contexto y el diseño existente antes de modificar.
  - **Ante la duda, preguntá:** No tomes decisiones de diseño o arquitectura por tu cuenta.
  - **Explicación:** Siempre explicá los cambios importantes siguiendo estas directrices.
</ai_interaction_protocol>
