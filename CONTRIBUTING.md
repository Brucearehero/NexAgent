# 贡献指南

感谢你愿意为 NexAgent 贡献代码！

## 开发环境设置

```bash
# 克隆项目
git clone https://github.com/yourname/NexAgent.git
cd NexAgent

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright（可选）
playwright install chromium
```

## 开发规范

### 代码风格
- 遵循 PEP 8
- Python 类型注解使用 Type hints
- 异步代码使用 `async/await`

### 提交规范
- 使用清晰的提交信息
- 提交前运行测试

### 测试
```bash
# 运行所有测试
pytest tests/

# 运行单个测试文件
pytest tests/test_agent.py
```

## 分支管理

- `main` - 主分支，稳定版本
- `develop` - 开发分支
- `feature/*` - 新功能
- `fix/*` - 修复

## Pull Request 流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 问题反馈

发现 Bug 或有新功能想法？欢迎：
- 提交 [Issue](https://github.com/yourname/NexAgent/issues)
- 参与讨论

## 许可证

提交代码即表示你同意你的贡献将按照 MIT 许可证开源。
