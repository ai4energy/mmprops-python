# 发布到 PyPI（准备清单）

当前状态：**未注册**。PyPI 上 `mmprops` 名字目前为空（2026-10-30 检查），但需要
owner 的 PyPI 账号才能创建项目和配置 trusted publisher。

## 一次性配置（owner 操作）

1. 注册/登录 <https://pypi.org>。
2. 创建项目 `mmprops`。
3. 项目 → Settings → Publishing → 添加 **Trusted Publisher**：
   - Owner: `ai4energy`
   - Repository: `mmprops-python`
   - Workflow: `publish.yml`
   - Environment: `pypi`
4. 不需要长期 API token。

## 每次发版

1. 更新 `pyproject.toml` 的 `version` 与 `src/mmprops/__init__.py` 的 `__version__`。
2. 打 tag 并推送：
   ```bash
   git tag -a vX.Y.Z -m "mmprops-python vX.Y.Z"
   git push origin vX.Y.Z
   ```
3. GitHub Release（published）触发 `publish.yml`，或手动 `workflow_dispatch`。
4. 验证：
   ```bash
   python -m venv /tmp/mmprops-check && . /tmp/mmprops-check/bin/activate
   pip install mmprops==X.Y.Z
   python -c "import mmprops; print(mmprops.__version__)"
   ```

## 在注册前

- `pip install git+https://github.com/ai4energy/mmprops-python@vX.Y.Z` 可用。
- 本仓协议测试不需要引擎；集成测试需 `MMPROPS_BIN`。
