# MMPROPS Python 客户端

MMPROPS 物性引擎的 **MIT** Python 客户端。每次调用启动一个 `mmprops` 进程，
读取 JSON 输出；调用之间不保留状态。

```python
from mmprops import flash, props, sat, vle

water = props("water", "300 K", "1 bar")
print(water.values["rho"], water.units["rho"])

boiling = sat("water", "373.15 K")
print(boiling.values["psat"])

two_phase = flash("water", p="1 bar", h="1000 kJ/kg")
print(two_phase.values["t"], two_phase.values["x"])

point = vle("bubble", ["methane", "ethane"], "220 K", x=[0.5, 0.5])
print(point.p, point.y)
```

## 安装

```bash
pip install git+https://github.com/ai4energy/mmprops-python
```

还需要 **MMPROPS 引擎二进制**：

- 免费学术版（非商业用途）：
  <https://github.com/ai4energy/mmprops/releases>
- 放到 `PATH`，或设 `MMPROPS_BIN=/path/to/mmprops`，或传 `binary="/path/to/mmprops"`。
  显式给出的路径不可执行时**响亮报错**。

## API

| 调用 | 含义 |
| --- | --- |
| `props(fluid, t, p, *, data=None, binary=None, timeout=120.0)` | 状态点物性 → `PropertyResult` |
| `sat(fluid, t, *, …)` | 饱和态（psat / rho_l / rho_v / hfg）→ `PropertyResult` |
| `flash(fluid, *, p, h=None, s=None, …)` | p,h 或 p,s 闪蒸 → `PropertyResult` |
| `vle(kind, components, t, *, x=None, y=None, …)` | 二元 VLE 泡/露点 → `VleResult` |
| `envelope(components, t, *, points=21, …)` | T-x-y 包络 → `EnvelopeResult` |
| `db_props(*, …)` / `db_pack(*, …)` / `db_show(name, *, …)` | 注册表与数据包查询 |

`PropertyResult.values` / `.units` 按物性名索引；两相下无定义的量返回 `None`。
数值参数可以直接给数（按 SI 解释），也可以给带单位字符串（如 `"300 K"`）。
`vle` / `envelope` 目前只接受**二元**混合物；`x` / `y` 的长度必须与组分数一致。
失败抛 `MmpropsError`（引擎报错，含 `.op` / `.raw`）、`MmpropsProtocolError`、
`MmpropsTimeout`、`MmpropsBinaryNotFound`。

## 许可

- **本包**：MIT（见 `LICENSE`）。
- **MMPROPS 引擎**：**商业软件，不是 MIT**（见 `LICENSE-ENGINE.md`）。学术/教学/
  个人非商业用途免费；商业用途需取得商业许可（mingtao.li@gmail.com）。本包不含
  引擎代码，只通过公开 JSON 命令行协议调用引擎。

## 开发

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
pytest -q                                      # 协议测试（假 CLI）
MMPROPS_BIN=/path/to/mmprops pytest -q tests/test_integration.py
```

协议测试使用 `tests/fake_mmprops.py`；真机集成只在设置 `MMPROPS_BIN` 时运行。
