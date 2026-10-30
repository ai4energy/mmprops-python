"""最小示例：水状态点与饱和态（学术版即可运行）。

    export MMPROPS_BIN=/path/to/mmprops
    python examples/water.py
"""

from __future__ import annotations

from mmprops import props, sat


def main() -> None:
    water = props("water", "300 K", "1 bar")
    print(f"rho = {water.values['rho']:.6f} {water.units['rho']}")

    boiling = sat("water", "373.15 K")
    print(f"psat = {boiling.values['psat']:.6f} {boiling.units['psat']}")


if __name__ == "__main__":
    main()
