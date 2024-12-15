# Bullet Dodge Web Game

## Project Overview

This project marks my first foray into **game development**, focusing on implementing simple physics and time loop mechanics. Inspired by the popular **Google Chrome Dino game**, this web-based game challenges the player to dodge bullets by jumping over them. 

The project emphasizes:
- Game mechanics such as **collision detection**, **object motion**, and **player interaction**.
- Progressive difficulty by increasing bullet speed and frequency over time.
- Dynamic game states like winning or losing based on collision or survival.

---

## Key Features

1. **Core Mechanics**:
   - The player controls a character ("dyno") that can **jump** to dodge incoming bullets.
   - Bullets move horizontally across the screen at increasing speed as the game progresses.
   - Collision detection ensures the game ends if the dyno and a bullet collide.

2. **Dynamic Difficulty**:
   - The frequency of bullets (`bullet.occur`) decreases over time, increasing challenge.
   - Bullet speed (`bullet.objectSpeed`) increases incrementally to make dodging harder.
   - Randomized bullet generation adds variability to the gameplay.

3. **Winning State**:
   - The player wins by surviving until all bullets are spawned and dodged.

4. **User Interface**:
   - Displays the number of bullets left to dodge (`occ`) and the current bullet speed (`speed`).

---

## Code Explanation

### **Main Game Function**
The game logic is implemented in the `game()` function, which handles all interactions between the **world**, **dyno**, and **bullet** objects.

```javascript
function game(world, dyno, bullet) {
    // Handle dyno's jump logic
    timeJump = dyno.jump(timeJump, jump_time);

    // Move bullets across the screen
    bullet.move();

    // Reduce jump height after reaching a peak
    if (timeJump == 6) timeJump--;

    // Disable jump button if dyno is not on the ground
    jumpbtn.disabled = (world.onFloor(dyno.location) > 0);

    // Check for collision between dyno and bullets
    if (bullet.obj.length != 0 && world.checkCollision(dyno, bullet.obj)) {
        EndInterval();  // End the game on collision
    }

    // Spawn bullets at intervals and increase difficulty
    if (time % bullet.occur == 50) {
        bullet.create();

        // Random chance to add additional bullets
        let rand_bullet_addition = Math.floor(Math.random() * 15);
        if (rand_bullet_addition == 10) {
            bullet.create(); bullet.create();
        }
        if (rand_bullet_addition == 5 || rand_bullet_addition == 13 || rand_bullet_addition == 4) {
            bullet.create();
        }

        // Increment speed and decrease interval between bullets
        bullet.objectSpeed += 0.2;
        bullet.occur -= 1;
        jump_time += 0.015;
    }

    // End game if all bullets are dodged
    if (bullet.occur <= 50) {
        ctx.strokeText("END! U WON!!!", 450, 150);
        EndInterval();
    }

    // Update UI elements
    occ.innerHTML = "Bullets Left => " + (bullet.occur - 50);
    speed.innerHTML = "Bullet Speed => " + bullet.objectSpeed.toFixed(2);
    time++;
}
```

### **Key Components**

1. **Dyno (Player Character)**:
   - Handles jumping logic with adjustable jump height and time (`timeJump` and `jump_time`).
   - Uses collision detection to determine if the game ends.

2. **Bullet**:
   - Moves across the screen and increases speed over time (`bullet.objectSpeed`).
   - Bullets are spawned at intervals defined by `bullet.occur` and can be randomized for added challenge.

3. **World**:
   - Checks if the dyno is on the floor (`world.onFloor()`).
   - Detects collisions between the dyno and bullets (`world.checkCollision()`).

4. **Game States**:
   - The game ends either when the player collides with a bullet or when all bullets are dodged.

---

## How to Play

1. **Objective**:
   - Dodge all bullets by jumping over them to win the game.

2. **Controls**:
   - Press the **Jump button** to make the dyno jump.

3. **Winning the Game**:
   - Successfully avoid all bullets until the `bullet.occur` value reaches 50.

4. **Losing the Game**:
   - Collide with a bullet to lose the game.

---

## Future Enhancements

1. **Improved Graphics**:
   - Add animations and sprites for the dyno and bullets to enhance visual appeal.

2. **Audio Effects**:
   - Introduce sound effects for jumping, collisions, and winning the game.

3. **Mobile Compatibility**:
   - Optimize controls for touch screens to support mobile devices.

4. **Dynamic Obstacles**:
   - Introduce new types of obstacles and power-ups for variety.

5. **Score System**:
   - Implement a scoring mechanism to track player performance.

---

## Technologies Used

- **HTML5 Canvas**: For rendering the game graphics.
- **JavaScript**: For game logic and physics.
- **CSS**: For basic styling and layout.
  
---

## Acknowledgment

This project was inspired by the **Google Chrome Dino game** and serves as a foundation for exploring game development concepts like physics simulation and event loops.