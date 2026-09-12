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