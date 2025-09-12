# 测试系统迁移指南

## 概述

SAGE Framework 已经从分散的 `tools/tests` 脚本迁移到统一的 `sage dev test` 命令。本文档说明了新旧系统的差异和迁移指南。

## 新旧系统对比

### 旧系统：tools/tests 脚本
- `run_tests.py` - Python 集成测试运行器，支持详细配置
- `test_all_packages.sh` - Bash 脚本，支持并行执行和高级选项
- `quick_test.sh` - 快速测试脚本，适合日常开发

### 新系统：sage dev test 命令
- 统一的 CLI 入口点
- 集成到 SAGE 工具链中
- 支持不同测试类型：all, unit, integration
- 更简洁的接口和一致的用户体验

## 命令对比

### 基本测试

**旧系统：**
```bash
# 使用 Python 脚本
cd tools/tests
python run_tests.py --all

# 使用 Bash 脚本
./test_all_packages.sh

# 快速测试
./quick_test.sh
```

**新系统：**
```bash
# 所有测试
sage dev test

# 单元测试
sage dev test --test-type unit

# 集成测试  
sage dev test --test-type integration

# 详细输出
sage dev test --verbose
```

### 高级选项对比

| 功能 | 旧系统 | 新系统 | 状态 |
|------|--------|--------|------|
| 测试类型选择 | `--unit`, `--integration` | `--test-type unit/integration` | ✅ 已迁移 |
| 详细输出 | `--verbose` | `--verbose` | ✅ 已迁移 |
| 并行执行 | `--jobs N` | 内置优化 | 🔄 重新设计 |
| 超时控制 | `--timeout N` | 内置默认值 | 🔄 重新设计 |
| 测试报告 | `--report file.txt` | 内置日志 | 🔄 重新设计 |
| 失败重跑 | `--failed` | 暂不支持 | ❌ 待实现 |
| 包选择 | `--packages pkg1,pkg2` | 自动发现 | 🔄 重新设计 |

## 迁移步骤

### 1. 立即可用
新的 `sage dev test` 命令已经可以使用，提供基本的测试功能。

### 2. CI/CD 已更新
- `.github/workflows/ci.yml` 已更新使用 `sage dev test`
- `.github/workflows/dev-ci.yml` 已更新使用 `sage dev test`

### 3. 逐步淘汰
`tools/tests` 下的脚本将逐步淘汰，但在过渡期仍可使用。

## 推荐用法

### 日常开发
```bash
# 快速验证
sage dev test --test-type unit

# 详细测试
sage dev test --verbose
```

### CI/CD
```bash
# 单元测试
sage dev test --test-type unit --verbose

# 集成测试
sage dev test --test-type integration --verbose
```

### 完整测试
```bash
# 所有测试
sage dev test --verbose
```

## 暂时保留的功能

以下功能在 `tools/tests` 中暂时保留，等待后续迁移：

1. **高级并行控制** - `test_all_packages.sh` 的 `--jobs` 参数
2. **超时自定义** - `--timeout` 参数的细粒度控制
3. **测试报告生成** - `--report` 功能
4. **失败重跑** - `--failed` 选项
5. **包选择** - 精确的包测试选择

## 后续规划

1. **功能增强**：将旧系统的高级功能逐步集成到 `sage dev test`
2. **完全淘汰**：完成功能迁移后，移除 `tools/tests` 脚本
3. **文档更新**：更新所有相关文档和示例

## 问题反馈

如果在使用新测试系统时遇到问题，请：
1. 检查是否可以用旧系统解决（临时方案）
2. 提交 issue 报告问题
3. 在过渡期可以继续使用旧脚本作为备选

---

**最后更新**：2025-09-13  
**状态**：迁移进行中
