# Changelog - Totemfall

Todas las adiciones, cambios y correcciones de este proyecto serán documentadas en este archivo.

## [v0.1.0] - Estructura Base y Movimiento del Jugador

### Añadido
- **Entorno Virtual y Framework:** Configuración inicial del proyecto utilizando Pygame y el framework Gale.
- **Máquina de Estados (Game States):** Implementación de la arquitectura de estados principales (`MainMenuState`, `PlayState`, `OptionsState`) para un flujo de juego limpio.
- **Entidad Player Independiente:** Creación de la clase `Player` utilizando su propia máquina de estados (`PlayerIdleState`, `PlayerWalkState`).
- **Sistema de Animación:** Integración de `gale.animation` para reproducir fluidamente los *sprites* del mago (idle y walk) basándose en una cuadrícula exacta de 26x18 píxeles.
- **Renderizado del Nivel:** Implementación de la plataforma de defensa (`sprStairs.png`) en la parte superior del `PlayState`, reservando espacio (HUD) para la futura interfaz.
- **Cursor Táctico:** Se ocultó el cursor nativo de Windows y se reemplazó por un *crosshair* personalizado (`sprCursor.png`) que sigue el mouse en coordenadas virtuales escaladas.
- **Matemática de Disparo (Fundamentos):** Incorporación de la lógica trigonométrica (`math.atan2`) que calcula el ángulo exacto entre el centro del jugador y el cursor del mouse, preparando el terreno para el sistema de *Object Pooling* de proyectiles.

### Cambiado
- **Controles del Sistema:** Se eliminó la salida accidental del juego con `ESC`. Ahora se requiere presionar la combinación `Ctrl + Q` para cerrar la aplicación de forma segura.

## [v0.2.0] - Sistema de Combate, IA y Game Feel

### Añadido
- **Sistema de Colisiones (Hitboxes):** Implementación de lógica física entre entidades (enemigos, proyectiles y estructuras) para el registro de impactos.
- **Efectos de Partículas (Sangre):** Integración del sistema `ParticleSystem` del framework Gale para emitir salpicaduras de sangre direccionales al registrar daño en los enemigos.
- **Retroalimentación Visual (Game Feel):** Adición de destellos blancos al recibir daño usando saturación de color (`BLEND_RGB_ADD`) y transiciones de estado en proyectiles para reproducir animaciones de explosión al impactar.
- **IA Cuerpo a Cuerpo (Batilisk):** Creación de la entidad `Batilisk` con lógica de persecución matemática (*Pathfinding*), un estado dedicado de ataque (`EnemyAttackState`) y un efecto visual de tajo de espada que calcula y rota dinámicamente hacia el objetivo.
- **IA a Distancia (Goblin):** Creación de la entidad arquera `Goblin` con su propio *Object Pool* de flechas independientes.
- **Lógica de Rango y Movimiento (Strafing):** Implementación de `EnemyRangedWalkState` para calcular distancias euclidianas (rango de visión), y `EnemyRangedAttackState` con comportamiento de pasos laterales y pausas tácticas para tensar el arco, evitando que el enemigo sea un blanco estático.

##  Generación Procedural, Multimundos y Físicas

### Añadido
- **Arquitectura Procedural Base:** Creación de la clase padre `ProceduralRoom` encargada de generar la estructura de los niveles.
- **Algoritmos de Mapas:** Implementación de *Path Carving* (garantizando rutas de escape), Autómatas Celulares (suavizado para rellenar huecos trampa) y Clustering (agrupación orgánica de bloques).
- **Despeje de Arena (Arena Clearing):** Lógica matemática para mantener el centro del mapa y las esquinas despejadas, favoreciendo el espacio para el combate.
- **Sistema de Multimundos:** Creación de 5 entornos distintos (`SwampRoom`, `InfernoRoom`, `CatacombsRoom`, `RockRoom`, `WaterRoom`) aplicando herencia orientada a objetos (DRY) para heredar la lógica procedural pero inyectar texturas únicas.
- **Progresión Modular:** Implementación de un gestor de niveles en `PlayState` que aumenta la densidad de obstáculos del nivel 1 al 8, y cambia de mundo automáticamente utilizando el operador módulo (`%`).
- **Físicas Dinámicas de Proyectiles:** Se añadió el método `get_collision_rect()` a los proyectiles para calcular hitboxes dinámicas en tiempo real que respetan su rotación y su patrón de onda (`wobble`).
- **Detección de Colisiones AABB:** Los proyectiles mágicos ahora detectan correctamente los bloques sólidos y se desactivan (destruyen) al impactar contra los muros de la arena.
- **Temporizador Antirrebote (Debounce):** Inclusión de un *cooldown* en la lectura de inputs del teclado para evitar que un solo toque registre múltiples pulsaciones (Key Bouncing) al cambiar de nivel.

### Cambiado
- **Refactorización y Optimización:** Se optimizó la complejidad de la generación de la matriz espacial de los mapas fusionando bucles anidados y utilizando *Set Comprehensions* (operaciones nativas rápidas en Python).
- **Ajuste de Padding Visual:** Modificación matemática de `TILE_SIZE_Y` en las configuraciones globales para aplastar los *sprites* y eliminar los huecos transparentes, logrando muros visualmente sólidos y conectados.

## [v0.3.0] - Agregado de enemigos, vida del totem Y primeras Oleadas

### Añadido
- **Arquitectura Procedural para la generacion de enemigos:** Cracion de la clase `WaveManager.py` que gestiona la generacion de los enemigos en el nivel.
- **Algoritmos de Mapas con enemigos:** Implementación de tipos especificos de enemigos por tipo de mundo.
- **Agregado de los tipos de enmigos:** Implementacion de los diferentes mounstros que va a tener el juego.


## [v0.4.0] - Cinemáticas, Físicas Avanzadas y Estadísticas (Kill Tracker)

### Añadido
- **Cinemáticas de Nivel:** Implementación de secuencias de victoria (ascenso al cielo) y entrada triunfal (aterrizaje al nuevo nivel) utilizando el motor de interpolación matemática (`Timer.tween`).
- **Efecto de Transición (Iris Wipe):** Sistema visual de cierre y apertura circular entre escenas construido con el lienzo de Pygame utilizando enmascaramiento por color clave (`set_colorkey`).
- **Cinemática de Derrota (Time Freeze):** Implementación del patrón de "Congelamiento de Tiempo" que detiene la lógica del motor para ejecutar una explosión de partículas y el hundimiento del Tótem antes del cambio de estado.
- **Sistema de Estadísticas (Kill Tracker):** Recolección dinámica de bajas en un diccionario (`kill_counts`) que identifica el tipo de monstruo derrotado mediante su atributo `texture_id`.
- **UI en Cuadrícula Dinámica (Grid Layout):** Rediseño matemático del `GameOverState` para organizar el reporte de bajas en una cuadrícula auto-centrada de hasta 7 columnas, capaz de escalar y mostrar múltiples sprites y multiplicadores de texto ("x N") sin solapamientos.

### Cambiado
- **Sistema de Seguro de Arma (Weapon Safety):** Implementación de una bandera de comunicación (`can_shoot`) entre el `PlayState` y el `Player` para suspender el gasto de maná, bloqueando los disparos durante las cinemáticas o en ausencia de enemigos.
- **Renderizado y Vida de Partículas:** 

### Corregido
- **Deslizamiento de Muros (Wall Sliding):** Se rediseñó el motor físico `_move_with_collisions` en `BaseEnemy` aplicando Conservación de Inercia. Los enemigos ahora transfieren el 100% de su aceleración al eje libre, erradicando la pérdida artificial de velocidad (fricción de pared).
- **Vibración de Enemigos (Target Jittering):** Se incorporó un "Radio de Ataque" (Stopping Distance de 15 píxeles) en el algoritmo de supervivencia (Plan B). Los monstruos cuerpo a cuerpo ahora frenan en seco al rodear el Tótem, eliminando el temblor de colisión AABB.
- **Limpieza Instantánea de Proyectiles:** Se solucionó el problema de *fuego fantasma* desintegrando forzosamente cualquier misil vivo en pantalla en el milisegundo exacto en que inicia una cinemática.
- **Agregado tipos de cartas:** Implementacion de los diferentes tipos de cartas que daran poderes al jugador.

## [v0.4.0] - Sistema de Invocación, UI "Juice" y Efectos Visuales

### Añadido
- **Efectos de Interfaz (Juice) para Cartas:** Implementación de animaciones de entrada (`tweening`), escalado dinámico al pasar el cursor con marco dorado, partículas mágicas integradas y auto-ajuste inteligente de texto.
- **Manipulación del Tiempo (Slow-Mo):** Agregado un efecto de dilatación temporal que ralentiza la acción al elegir una mejora y recupera la velocidad gradualmente al reanudar el combate.
- **Vórtices de Experiencia Animados:** Creacion de los orbes de exp usando texturas animadas utilizando el sistema de animaciones del framework.
- **Sistema de Invocación de Aliados:** Creación de la clase proxy `Ally.py`, capaz de clonar cualquier enemigo del nivel actual, sobrescribiendo su IA para que defienda al jugador (marcado con un diamante azul).
- **Mazo de Cartas Evolutivo:** El gestor de cartas ahora inyecta opciones avanzadas (daño extra para aliados y ranuras de invocación adicionales) únicamente después de que el jugador desbloquea la habilidad base.
- **Formaciones Defensivas Tácticas:** Los monstruos aliados transicionan a un "Modo Guardián", marchando hacia posiciones de escolta predefinidas frente al obelisco cuando se limpia la oleada.
- **Sistema de Aggro Dinámico e Intercepción:** Los enemigos evalúan la distancia en tiempo real para priorizar el combate contra los aliados más cercanos en lugar del obelisco. Los proyectiles enemigos ahora también impactan y dañan a las invocaciones.
- **Animaciones de Aparición (Spawn Drop):** Tanto enemigos como aliados ingresan al campo de batalla cayendo desde el cielo con un efecto de rebote, detonando un nuevo sistema de partículas de impacto (`DustEffect.py`) al tocar el suelo.


## [v0.5.0] - Persistencia, Top Global y Modo Infinito

### Añadido
- **Persistencia de Datos Local:** Implementación del módulo `json` en las configuraciones globales para escribir y leer un archivo `save_data.json` que almacena el nombre del jugador en el disco duro.
- **Registro de Jugador Estilo Arcade:** Creación del `NameInputState`, una interfaz que permite al usuario registrar un nombre de 5 letras utilizando la navegación por teclado (flechas y Enter), emulando las máquinas recreativas clásicas.
- **Integración de Top Global (Dreamlo):** Conexión HTTP nativa con la API de Dreamlo para el envío y lectura de puntajes. El proceso se ejecuta en un hilo secundario (`threading`) durante el `GameOverState` y `VictoryState` para evitar bloqueos en el renderizado (congelamiento de fotogramas).
- **Fondo Dinámico en el Menú Principal:** Integración de una imagen de fondo (`menu_bg`) que se escala automáticamente a la resolución virtual del juego. Se implementó un filtro oscuro semitransparente (`SRCALPHA` a 100 de opacidad) superpuesto al fondo para garantizar la legibilidad y contraste del texto del menú.
- **Modo Supervivencia (Infinito/Aleatorio):** Nueva característica post-victoria ("Keep Playing") que inyecta una bandera (`random_mode`) al `PlayState`. Esto altera la generación para cargar mundos aleatorios (del 1 al 40), estandariza la ganancia de puntos (100 pts fijos por baja) y cambia el identificador del HUD a "Level: INF", manteniendo intacto el progreso previo del jugador.
- **Submenús Horizontales:** Rediseño arquitectónico en las pantallas de fin de juego para soportar opciones en el eje X, calculando dinámicamente las posiciones al 35% y 70% del ancho de la pantalla y mapeando las teclas `Left`/`Right`.
- **Personalización del Sistema Operativo:** Integración de la función nativa `pygame.display.set_icon()` para inyectar dinámicamente un *sprite* del juego (el mago) como ícono en la ventana del sistema, además de la parametrización del título de la aplicación.

### Cambiado
- **Expansión del Menú Principal:** Se reestructuró la lista de opciones y el enrutamiento del `MainMenuState`. Ahora el jugador puede navegar entre cuatro opciones completas: *Play* (inicia la partida), *Global Top* (conecta con la API de Dreamlo), *Change Name* (modifica el archivo `.json` de persistencia) y *Exit* (cierra el juego de forma segura).
- **Estandarización de Navegación:** Se corrigió la dirección matemática del cursor en el `MainMenuState` para ajustarse a los estándares de UX.
