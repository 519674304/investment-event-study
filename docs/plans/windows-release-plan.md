Document ID: PLAN-WINDOWS-RELEASE
Status: Approved
Approved by: 用户
Approved at: 2026-08-12
Depends on: PLAN-MARKET, PLAN-INFORMATION-EVENTS, PLAN-CHART, ARCH-TECHNICAL
Supersedes:

# Windows 发布实施计划

## PLAN-RELEASE-001：启动器与单实例

- 需求：REQ-SEC-001、REQ-REL-001、AC-CORE-004。
- 上下文/职责：应用启动生命周期、RESP-PRESENT。
- ADR：ADR-001、ADR-007。
- 目标：双击启动、动态本机端口、单实例复用、健康后开浏览器、关闭窗口停服务。
- 文件：`launcher/`、健康接口、Windows 快捷方式生成脚本和启动集成测试。
- 测试：端口占用、重复启动、健康超时、浏览器打开失败、正常关闭和异常退出。
- 完成证据：无开发命令完成启动和停止；第二次双击只打开已有实例。

## PLAN-RELEASE-002：迁移、恢复和日志

- 需求：REQ-REL-001—004、REQ-SEC-002—003。
- 上下文/职责：全部持久化职责和结构化问题接收器。
- ADR：ADR-005、ADR-007、ADR-008。
- 文件：迁移启动流程、SQLite 一致性备份、恢复检查、滚动日志和问题转换器。
- 步骤：启动前检测版本；迁移前一致性备份；迁移失败阻止启动；启用 WAL/外键/busy timeout；实现日志脱敏和请求 ID；异常退出后完整性检查。
- 测试：从上一 schema 升级、故意迁移失败、活动 WAL 备份、磁盘只读、数据库损坏副本和日志轮转。
- 完成证据：失败迁移可恢复原库；错误页面无堆栈而日志保留原因。

## PLAN-RELEASE-003：发布包与验收环境

- 需求：AC-CORE-001、AC-CORE-002、AC-CORE-003、AC-CORE-004、REQ-REL-001、REQ-SEC-001。
- 上下文/职责：全系统。
- ADR：ADR-007。
- 依赖：PLAN-RELEASE-001—002。
- 目标：生成不要求用户安装 Python/Node 依赖的版本化 Windows 发布目录和桌面快捷方式。
- 文件：构建脚本、版本清单、安装/升级说明、发布烟雾测试。
- 测试：全新 Windows 用户目录、中文路径、无管理员权限、升级保留数据、卸载应用不误删用户数据。
- 回滚：新版本与用户数据分离；升级失败可启动上一应用版本读取迁移前备份。
- 完成证据：CP-5 和 PLAN-ACCEPTANCE-001 全部通过。
