# Sync脚本优化使用指南

新的sync脚本现在支持多种速度级别的检查和同步，适合不同的使用场景。

## 速度级别比较

| 命令 | 速度 | API调用 | 适用场景 |
|------|------|---------|----------|
| `timestamp-check` | ⚡ 超快 | 0次 | 快速检查是否有过期数据 |
| `quick-preview` | 🚀 快速 | N次 (N=限制数量) | 检查少量issues的详细更改 |
| `preview` | 🐌 完整 | 所有issues | 完整检查所有issues |

## 使用方法

### 1. 超快速时间戳检查 (推荐首选)
```bash
# 检查前20个issues的时间戳
python3 sync_issues.py timestamp-check --limit 20

# 只检查最近7天更新的issues
python3 sync_issues.py timestamp-check --recent-only --limit 50

# 检查前100个issues
python3 sync_issues.py timestamp-check --limit 100
```

**优点**: 
- 无API调用，极快
- 可以快速发现哪些issues可能需要同步
- 适合日常检查

**局限**: 
- 只能发现时间戳不一致，不能检测实际内容差异
- 可能有假阳性

### 2. 快速预览 (发现问题后使用)
```bash
# 详细检查前10个issues
python3 sync_issues.py quick-preview --limit 10

# 详细检查最近更新的issues
python3 sync_issues.py quick-preview --recent-only --limit 20
```

**优点**: 
- 调用少量API，相对快速
- 提供详细的更改信息
- 可以发现实际的内容差异

**适用**: 
- 在时间戳检查发现问题后使用
- 检查特定范围的issues

### 3. 完整预览 (谨慎使用)
```bash
# 检查所有issues (可能很慢)
python3 sync_issues.py preview
```

**警告**: 会调用大量API，可能需要很长时间

## 同步操作

### 同步单个issue
```bash
python3 sync_issues.py sync 123
```

### 同步所有更改
```bash
# 预览后确认同步
python3 sync_issues.py quick-preview --limit 10
python3 sync_issues.py sync --auto-confirm
```

## 推荐工作流程

### 日常检查
```bash
# 1. 快速检查是否有更新
python3 sync_issues.py timestamp-check --limit 50

# 2. 如果发现问题，详细检查
python3 sync_issues.py quick-preview --limit 10

# 3. 如果需要，进行同步
python3 sync_issues.py sync --auto-confirm
```

### 定期维护
```bash
# 检查最近活跃的issues
python3 sync_issues.py timestamp-check --recent-only --limit 100
```

### 特定issue调试
```bash
# 检查特定issue
python3 sync_issues.py sync 123
```

## 注意事项

1. **API限制**: GitHub API有速率限制，避免同时运行多个完整检查
2. **网络依赖**: quick-preview和preview需要网络连接
3. **权限要求**: 同步操作需要适当的GitHub权限
4. **备份建议**: 重要同步前建议备份数据

## 故障排除

### 时间戳检查显示假阳性
- 时间戳不一致不一定意味着需要同步
- 使用quick-preview进行详细检查

### API调用失败
- 检查网络连接
- 检查GitHub token权限
- 等待API限制重置

### 同步失败
- 检查具体错误信息
- 确认有修改权限
- 手动检查issue状态
