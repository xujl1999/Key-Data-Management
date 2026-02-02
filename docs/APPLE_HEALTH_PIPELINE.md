# Apple Health 数据管线改进方案

**调研日期**: 2026-02-02
**调研人**: Pi (AI Assistant)

## 当前痛点

- 现方案：iPhone 快捷指令录制手势 → 导出健康数据 → 上传 OneDrive
- 问题：
  - 容易遗忘执行
  - 经常失败（需要解锁手机才能运行）
  - 手动操作繁琐

## 推荐方案

### 方案一：Health Auto Export（推荐 ⭐⭐⭐⭐⭐）

**App**: [Health Auto Export - JSON+CSV](https://apps.apple.com/us/app/health-auto-export-json-csv/id1115567069)

**特点**:
- 免费 App，4.3 星评分
- 支持自动化导出（定时任务）
- 导出格式：JSON、CSV
- 支持目标：
  - iCloud Drive
  - Google Drive
  - Dropbox
  - REST API / Webhook
  - MQTT / Home Assistant

**自动化设置步骤**:
1. 下载 Health Auto Export App
2. 选择要导出的指标（心率、步数、睡眠等）
3. 设置自动化：
   - 在 App 内创建 Automation
   - 或使用 iOS Shortcuts 触发
4. 目标设置为 iCloud Drive 或 REST API
5. Windows 端通过 iCloud for Windows 同步

**优势**:
- 真正的自动化，无需手动操作
- 可配置导出频率（每日/每周）
- 支持 Webhook，可直接推送到自己的服务器

### 方案二：Health Export CSV

**App**: [Health Export CSV](https://apps.apple.com/sa/app/health-export-csv/id1477944755)

**价格**: 约 ¥45 (12.99 SAR)

**特点**:
- 专注 CSV 导出
- 可与 Shortcuts 集成
- 适合导出后用 Excel/Python 分析

### 方案三：Shortcuts + Webhook（自建）

**流程**:
1. 创建 iOS Shortcut，获取健康数据
2. 发送到自己的 REST API 端点
3. 服务器接收并写入数据库/文件

**适合**:
- 需要完全自定义数据格式
- 已有自己的服务器/API

## 关键注意事项

1. **解锁要求**: Health 数据通常需要 iPhone 解锁才能运行自动化
2. **数据聚合**: 可选择导出聚合数据（日均值）而不是原始数据
3. **iCloud 同步**: 导出到 iCloud Drive 可自动同步到 Windows

## 推荐实施路径

### 短期（1-2 天）
1. 下载 Health Auto Export
2. 配置每日导出到 iCloud Drive
3. Windows 安装 iCloud for Windows
4. 验证数据同步

### 中期（1 周）
1. 配置 REST API Webhook
2. 在 data-management 项目添加接收端点
3. 自动解析并更新 health/data/*.csv

### 长期
1. 完全自动化：手机自动导出 → API 接收 → 仪表盘更新
2. 添加数据质量监控（检测漏数据）
3. 设置 Discord 提醒（数据更新状态）

## 下一步行动

- [ ] 让用户下载 Health Auto Export App
- [ ] 配置导出到 iCloud Drive
- [ ] 或：配置 Webhook 到本地服务器

---

**调研结论**: 推荐使用 **Health Auto Export** App，配合 iCloud Drive 或 REST API Webhook，可实现真正的自动化数据同步，彻底解决"容易遗忘、经常失败"的问题。
