import math


class Ball:
    def __init__(self, r=2, vel=1, dir=[0, 1]):
        self.x = 0.0
        self.y = 0.0
        self.r = r
        self.vel = vel
        self.dir = dir
        self.obstacle_crosses: list[int] = []  # per obstacle: +1=L->R, -1=R->L, 0=none

    # ── main move ─────────────────────────────────────────────────────────────

    def move(self, l_paddle, r_paddle, board):
        self.obstacle_crosses = [0] * len(board.obstacles)

        nx = self.x + self.vel * self.dir[1]
        ny = self.y + self.vel * self.dir[0]

        nx, ny = self._handle_obstacles(nx, ny, board.obstacles)

        # Paddle collisions — self.x/y already updated by obstacle handler on hit
        if self.dir[1] > 0:
            c1 = self.x < r_paddle.x
            c2 = r_paddle.y <= ny <= r_paddle.y + r_paddle.length
            c3 = nx >= r_paddle.x
            if c1 and c3 and c2:
                self.y = (self.dir[0] / self.dir[1]) * (r_paddle.x - self.x) + self.y
                self.x = r_paddle.x
                self.dir[1] = -self.dir[1]
                self.handle_paddle_collision(r_paddle)
                return
        else:
            c1 = self.x > l_paddle.x
            c2 = l_paddle.y <= ny <= l_paddle.y + l_paddle.length
            c3 = nx <= l_paddle.x
            if c1 and c3 and c2:
                self.y = (self.dir[0] / self.dir[1]) * (l_paddle.x - self.x) + self.y
                self.x = l_paddle.x
                self.dir[1] = -self.dir[1]
                self.handle_paddle_collision(l_paddle)
                return

        self.x = nx
        self.y = ny

        if self.y <= 0:
            self.y = 0
            self.dir[0] = abs(self.dir[0])
        elif self.y >= board.size - 1:
            self.y = board.size - 1
            self.dir[0] = -abs(self.dir[0])

        if self.x <= 0:
            board.increment_score(2)
            board.reset_ball()
        elif self.x >= board.size - 1:
            board.increment_score(1)
            board.reset_ball()

    # ── obstacle handling ─────────────────────────────────────────────────────

    def _handle_obstacles(self, nx: float, ny: float, obstacles) -> tuple[float, float]:
        """
        Zone-based entry detection (x_start < x_end) or thin-wall crossing
        (x_start == x_end). Both reduce to the same interpolation — only the
        'entering' predicate differs.

        HIT  → reflect dir[1], place ball just outside entry face, recurse.
        PASS → record crossing direction, continue.
        """
        if not obstacles:
            return nx, ny

        travel_right = self.dir[1] > 0
        sorted_obs = sorted(enumerate(obstacles), key=lambda e: e[1].x_start,
                            reverse=not travel_right)

        for idx, obs in sorted_obs:
            if obs.x_start == obs.x_end:
                # ── thin wall: strict crossing over the single x coordinate ──
                # Use a half-pixel tolerance so floating point can't land
                # exactly on the wall and skip it.
                wall_x = obs.x_start
                if travel_right:
                    entering = self.x < wall_x and nx >= wall_x
                else:
                    entering = self.x > wall_x and nx <= wall_x
                face_x = wall_x
            else:
                # ── zone: ball was fully outside, now entering the slab ───────
                if travel_right:
                    entering = self.x < obs.x_start and nx >= obs.x_start
                    face_x   = obs.x_start
                else:
                    entering = self.x > obs.x_end and nx <= obs.x_end
                    face_x   = obs.x_end

            if not entering:
                continue

            # Parametric intersection with the entry face
            t         = (face_x - self.x) / (nx - self.x)   # t in (0, 1]
            y_at_face = self.y + t * (ny - self.y)

            if obs.contains_y(y_at_face):
                # ── HIT ──────────────────────────────────────────────────
                self.x    = face_x - 1e-3 if travel_right else face_x + 1e-3
                self.y    = y_at_face
                self.dir[1] = -self.dir[1]

                rem = 1.0 - t
                nx  = self.x + self.vel * self.dir[1] * rem
                ny  = self.y + self.vel * self.dir[0] * rem
                return self._handle_obstacles(nx, ny, obstacles)
            else:
                # ── GAP ──────────────────────────────────────────────────
                self.obstacle_crosses[idx] = 1 if travel_right else -1

        return nx, ny

    # ── paddle collision ──────────────────────────────────────────────────────

    def handle_paddle_collision(self, paddle, transfer_factor=0.3):
        paddle_center = paddle.y + paddle.length // 2
        offset        = self.y - paddle_center
        self.dir[0]  += offset * transfer_factor
        magnitude     = math.sqrt(self.dir[0] ** 2 + self.dir[1] ** 2)
        self.dir[0]  /= magnitude
        self.dir[1]  /= magnitude