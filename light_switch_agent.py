# -*- coding: utf-8 -*-
"""
عامل واکنشی ساده (Simple Reflex Agent) برای مسئلهٔ سویچ نور در محیط 2×2

هدف عامل: خاموش کردن همهٔ خانه‌های روشن.
ادراک عامل: فقط خانهٔ جاری (مختصات x,y) + وضعیت چراغ همان خانه.
عامل حافظه ندارد؛ فقط قواعد شرط–عمل (condition-action) اعمال می‌کند.

قواعد (به ترتیب بررسی، اولین تطبیق برنده):
  R1: چراغ خانهٔ جاری روشن است  →  TOGGLE (زدن کلید)
  R2: چراغ خاموش است و آخرین خانه نیست →  MOVE به خانهٔ بعدی در ترتیب ثابت
  R3: در آخرین خانه هستیم و چراغش خاموش است →  HALT (پایان)
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

# نوع عمل: ("TOGGLE", None)  |  ("MOVE", (x, y))  |  ("HALT", None)
Action = Tuple[str, Optional[Tuple[int, int]]]


# --------------------------------------------------------------------------
# 1) محیط: شبکهٔ 2×2 از سویچ‌های نور
# --------------------------------------------------------------------------
class LightEnvironment:
    """محیط 2×2؛ هر خانه یک کلید نور دارد (زدن کلید = تعویض وضعیت)."""

    SIZE = 2

    def __init__(self,
                 lights: Optional[List[List[bool]]] = None,
                 start: Tuple[int, int] = (0, 0),
                 seed: Optional[int] = None) -> None:
        if lights is not None:
            assert len(lights) == self.SIZE and all(len(r) == self.SIZE for r in lights)
            self.lights: List[List[bool]] = [row[:] for row in lights]
        else:
            # حالت اولیهٔ تصادفی (برای آزمایش)
            rng = random.Random(seed)
            self.lights = [[rng.random() < 0.5 for _ in range(self.SIZE)]
                           for _ in range(self.SIZE)]
        self.pos: Tuple[int, int] = start
        self.steps: int = 0

    def percept(self) -> Dict:
        """ادراک لحظه‌ای: فقط وضعیت خانهٔ جاری (هیچ اطلاعات دیگری نداریم)."""
        x, y = self.pos
        return {"pos": self.pos, "light": self.lights[x][y]}

    def execute(self, action: Action) -> None:
        """اجرای عمل عامل روی محیط."""
        kind, target = action
        if kind == "TOGGLE":
            x, y = self.pos
            self.lights[x][y] = not self.lights[x][y]
        elif kind == "MOVE":
            assert target is not None
            nx, ny = target
            assert 0 <= nx < self.SIZE and 0 <= ny < self.SIZE, "حرکت خارج از شبکه!"
            self.pos = (nx, ny)
        elif kind == "HALT":
            pass  # عامل متوقف می‌شود
        else:
            raise ValueError(f"عمل ناشناخته: {kind}")
        self.steps += 1

    def all_lights_off(self) -> bool:
        return all(not on for row in self.lights for on in row)


# --------------------------------------------------------------------------
# 2) عامل واکنشی ساده: قواعد شرط–عمل، بدون حافظه
# --------------------------------------------------------------------------
class SimpleReflexAgent:
    """تابع ادراک–عمل به شکل قواعد شرط–عمل روی ادراک فعلی."""

    # ترتیب ثابت بازدید خانه‌ها (ردیف‌به‌ردیف)
    ORDER: List[Tuple[int, int]] = [(0, 0), (0, 1), (1, 0), (1, 1)]

    @classmethod
    def _next_cell(cls, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """خانهٔ بعدی در ترتیب ثابت؛ اگر آخرین خانه باشد None برمی‌گرداند."""
        i = cls.ORDER.index(pos)
        return cls.ORDER[i + 1] if i < len(cls.ORDER) - 1 else None

    def decide(self, p: Dict) -> Tuple[Action, str]:
        """بررسی قواعد به ترتیب و برگرداندن اولین عملِ تطبیق‌یافته."""
        pos, light = p["pos"], p["light"]

        # R1: اولویت با خاموش کردن چراغ روشن خانهٔ جاری
        if light:
            return ("TOGGLE", None), "R1: چراغ روشن است → زدن کلید"

        # R2: چراغ خاموش است → رفتن به خانهٔ بعدی (اگر خانه‌ای مانده باشد)
        nxt = self._next_cell(pos)
        if nxt is not None:
            return ("MOVE", nxt), f"R2: چراغ خاموش است → رفتن به خانهٔ {nxt}"

        # R3: آخرین خانه بازدید شد → پایان کار
        return ("HALT", None), "R3: آخرین خانه است و خاموش است → پایان"


# --------------------------------------------------------------------------
# 3) اجرا و نمایش
# --------------------------------------------------------------------------
def render(lights: List[List[bool]]) -> str:
    """نمایش شبکه: ● = روشن، ○ = خاموش"""
    return "\n".join("   " + "   ".join("●" if on else "○" for on in row)
                     for row in lights)


def run(env: LightEnvironment, agent: SimpleReflexAgent,
        max_steps: int = 50, verbose: bool = True) -> bool:
    """حلقهٔ ادراک → تصمیم → اجرا تا رسیدن به HALT."""
    if verbose:
        print("وضعیت اولیه:")
        print(render(env.lights))
        print("-" * 66)

    while True:
        p = env.percept()                        # 1) ادراک
        action, rule = agent.decide(p)           # 2 و 3) تصمیم با قاعده
        x, y = p["pos"]
        state = "روشن" if p["light"] else "خاموش"

        if action[0] == "HALT":
            if verbose:
                print(f"گام {env.steps + 1:02d} | خانه ({x},{y}) چراغ {state:6s} | "
                      f"{rule:42s} | HALT")
            break

        if verbose:
            desc = "زدن کلید (TOGGLE)" if action[0] == "TOGGLE" \
                else f"حرکت به {action[1]}"
            print(f"گام {env.steps + 1:02d} | خانه ({x},{y}) چراغ {state:6s} | "
                  f"{rule:42s} | {desc}")

        env.execute(action)                      # 4) اجرا روی محیط

        if env.steps > max_steps:                # 5) محافظ در برابر حلقهٔ بی‌نهایت
            raise RuntimeError("به سقف گام‌ها رسیدیم؛ احتمالاً حلقهٔ بی‌نهایت است!")

    if verbose:
        print("-" * 66)
        print("وضعیت نهایی:")
        print(render(env.lights))
        print(f"تعداد کل اعمال اجراشده: {env.steps}")
        print("همهٔ خانه‌ها خاموش شدند؟",
              "بله ✔" if env.all_lights_off() else "خیر ✘")

    return env.all_lights_off()


def verify_all_states() -> bool:
    """آزمایش قطعی: هر 16 حالت اولیهٔ ممکن باید به همه-خاموش برسد."""
    ok = True
    for mask in range(16):
        lights = [[bool(mask & (1 << (r * 2 + c))) for c in range(2)] for r in range(2)]
        env = LightEnvironment(lights=lights)
        if not run(env, SimpleReflexAgent(), verbose=False):
            ok = False
            print("شکست در حالت:", lights)
    return ok


if __name__ == "__main__":
    # محیط نمونه با چراغ‌های تصادفی
    env = LightEnvironment(seed=7)
    run(env, SimpleReflexAgent())

    print("\n" + "=" * 66)
    print("آزمایش همهٔ 16 حالت اولیهٔ ممکن:")
    print("همهٔ حالت‌ها موفق بودند ✔" if verify_all_states()
          else "برخی حالت‌ها شکست خوردند ✘")
