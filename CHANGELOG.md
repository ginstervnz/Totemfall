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
