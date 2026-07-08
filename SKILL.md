---
name: "api-test"
description: "API接口测试技能，支持新增接口测试、修改接口测试和回归测试。当用户提到'接口测试'、'API测试'、'接口联调'、'回归测试'等关键词时触发。"
---

# API接口测试技能

## 技能概述

本技能用于存量项目的接口测试，支持以下场景：
- 新项目/新模块的接口测试
- 旧模块新增接口的测试
- 旧模块修改接口的测试及回归测试

## 工作流程

### 首次工作流（新建测试用例）- 阶段1：生成测试用例

1. **触发条件**: 用户提到"接口测试"、"API测试"、"接口联调"等关键词
2. **信息收集**: AI询问用户以下信息：
   - 项目地址（base_url）
   - 测试模块名称
   - 是否需要创建测试账号（是/否）
   - 已有账号信息（如不创建）
   - 新增/修改的接口列表及说明
   - 可能受影响的接口（回归测试）
3. **生成测试用例文档**: AI生成测试用例文档（.md格式），保存到 `{project_root}/{module_name}/test_cases.md`
4. **阶段结束**: AI告知用户测试用例文档已生成，等待用户确认

**AI输出示例**:
```
测试用例文档已生成：{project_root}/{module_name}/test_cases.md

请审核测试用例，确认无误后回复：
- "测试用例没问题，继续执行"
- "需要修改测试用例，..."

注意：此文件不会被git跟踪
```

### 首次工作流（新建测试用例）- 阶段2：执行测试

**触发条件**: 用户回复"测试用例没问题"、"可以继续"、"确认执行"等确认性语句

1. **脚本编写**: AI创建测试脚本文件，保存到 `{project_root}/{module_name}/test_script.py`
2. **脚本运行**: 执行测试脚本
3. **报告输出**: AI生成测试报告（.md格式），保存到 `{project_root}/{module_name}/test_report.md`
4. **工作流结束**: AI告知用户测试报告路径

**AI输出示例**:
```
测试报告已生成：{project_root}/{module_name}/test_report.md

测试结果摘要：
- 总测试数: {total}
- 通过: {passed}
- 失败: {failed}
- 通过率: {pass_rate}%

详细报告请查看上述文件。
注意：此文件不会被git跟踪
```

### 非首次工作流（已有测试用例）

**触发条件**: 用户提到"重新跑测试"、"运行测试"、"执行测试"等

1. **查找测试脚本**: 在 `{project_root}/{module_name}/` 目录下查找 `test_script.py`
2. **脚本运行**: 执行已有测试脚本
3. **报告输出**: AI更新测试报告（.md格式），保存到 `{project_root}/{module_name}/test_report.md`
4. **工作流结束**: AI告知用户测试报告路径

## 文件存储规则

### 文件位置

所有测试相关文件存储在项目模块目录下：

```
{project_root}/{module_name}/
├── test_cases.md          # 测试用例文档（用户审核）
├── test_script.py         # 测试脚本（可执行）
└── test_report.md         # 测试报告（输出）
```

### Git忽略规则

以下文件需要添加到项目的 `.gitignore` 中：

```gitignore
# API测试相关文件
*/test_cases.md
*/test_script.py
*/test_report.md
```

**重要**: AI在生成文件时，应主动检查并更新项目的 `.gitignore` 文件。

## 测试用例文档格式 (test_cases.md)

```markdown
# {module_name} 模块接口测试用例

## 基本信息

| 项目地址 | {base_url} |
| 测试模块 | {module_name} |
| 认证方式 | {auth_type} |
| 生成时间 | {timestamp} |

## 认证信息

| 项目 | 值 |
|------|-----|
| 登录接口 | {auth_url} |
| 用户名 | {username} |
| 密码 | {password} |

## 新增接口测试

### 接口1: {接口名称}

| 项目 | 值 |
|------|-----|
| HTTP方法 | {method} |
| 接口路径 | {endpoint} |
| 是否需要认证 | {auth_required} |
| 预期状态码 | {expected_code} |
| 预期响应字段 | {expected_keys} |

**请求体** (如有):
```json
{request_body}
```

**测试场景**:
1. 正常请求 - 验证接口返回正确数据
2. 参数缺失 - 验证参数校验
3. 认证失败 - 验证权限控制

## 修改接口测试

### 接口1: {接口名称}

| 项目 | 值 |
|------|-----|
| HTTP方法 | {method} |
| 接口路径 | {endpoint} |
| 修改说明 | {modification_desc} |

**测试场景**:
1. 验证修改后的功能正常
2. 验证向后兼容性
3. 验证参数变化后的处理

## 回归测试

### 接口1: {接口名称}

| 项目 | 值 |
|------|-----|
| HTTP方法 | {method} |
| 接口路径 | {endpoint} |
| 影响原因 | {reason} |

**测试场景**:
1. 验证原有功能不受影响
2. 验证关联数据正确

---
请审核以上测试用例，确认无误后回复"测试用例没问题，继续执行"
```

## 测试报告格式 (test_report.md)

```markdown
# {module_name} 模块接口测试报告

## 基本信息

| 项目地址 | {base_url} |
| 测试模块 | {module_name} |
| 测试时间 | {timestamp} |
| 测试耗时 | {duration}s |

## 测试结果摘要

| 指标 | 值 |
|------|-----|
| 总测试数 | {total} |
| 通过数 | {passed} |
| 失败数 | {failed} |
| 通过率 | {pass_rate}% |

## 详细测试结果

### 新增接口测试

| 测试名称 | 状态 | 预期 | 实际 | 说明 |
|----------|------|------|------|------|
| {test_name} | {status} | {expected} | {actual} | {message} |

### 修改接口测试

| 测试名称 | 状态 | 预期 | 实际 | 说明 |
|----------|------|------|------|------|
| {test_name} | {status} | {expected} | {actual} | {message} |

### 回归测试

| 测试名称 | 状态 | 预期 | 实际 | 说明 |
|----------|------|------|------|------|
| {test_name} | {status} | {expected} | {actual} | {message} |

## 失败详情

{如果有失败的测试，列出详细信息}

---
测试报告生成时间: {timestamp}
此文件不会被git跟踪
```

## 信息收集清单

### 必须收集的信息

| 信息项 | 说明 | 示例 |
|--------|------|------|
| project_root | 项目根目录路径 | d:\adaye-work\blog |
| base_url | 项目API基础地址 | http://localhost:8000 |
| module_name | 测试模块名称 | posts, users, orders |
| auth_type | 认证类型 | jwt, token, basic, none |
| auth_url | 登录接口地址 | /api/token/ |

### 创建账号模式

| 信息项 | 说明 | 示例 |
|--------|------|------|
| register_url | 用户注册接口地址 | /api/register/ |
| username | 测试账号用户名 | test_user |
| password | 测试账号密码 | test_password123 |

### 使用已有账号模式

| 信息项 | 说明 | 示例 |
|--------|------|------|
| username | 已有账号用户名 | admin |
| password | 已有账号密码 | admin123 |

### 接口信息

| 信息项 | 说明 | 示例 |
|--------|------|------|
| method | HTTP方法 | GET, POST, PUT, PATCH, DELETE |
| endpoint | 接口路径 | /api/posts/ |
| description | 接口描述 | 获取文章列表 |
| auth_required | 是否需要认证 | true, false |
| expected_code | 预期状态码 | 200, 201, 401 |
| expected_keys | 预期响应字段 | ["id", "title"] |

## 使用示例

### 示例1: 新建测试用例 - 阶段1

```
用户: "帮我测试posts模块的接口"

AI: "好的，请提供以下信息：
     1. 项目根目录路径
     2. 项目地址（base_url）
     3. 认证方式
     4. 是否需要创建测试账号？"

用户: "d:\adaye-work\blog, http://localhost:8000, JWT, 需要创建账号"

AI: "请提供：
     1. 注册接口地址
     2. 登录接口地址
     3. 测试账号用户名和密码
     4. 需要测试的接口列表"

用户: "/api/register/, /api/token/, test_user/test123,
       GET /api/posts/ 获取文章列表
       POST /api/posts/ 创建文章"

AI: "正在生成测试用例文档...
     已生成: d:\adaye-work\blog\posts\test_cases.md

     请审核测试用例，确认无误后回复'测试用例没问题，继续执行'"
```

### 示例2: 新建测试用例 - 阶段2

```
用户: "测试用例没问题，继续执行"

AI: "正在创建测试脚本...
     已创建: d:\adaye-work\blog\posts\test_script.py

     正在执行测试...

     测试完成！
     已生成报告: d:\adaye-work\blog\posts\test_report.md

     测试结果摘要：
     - 总测试数: 10
     - 通过: 10
     - 失败: 0
     - 通过率: 100%
```

### 示例3: 重新运行测试

```
用户: "重新跑一下posts模块的测试"

AI: "正在执行测试脚本: d:\adaye-work\blog\posts\test_script.py

     测试完成！
     已更新报告: d:\adaye-work\blog\posts\test_report.md

     测试结果摘要：..."
```

## 触发关键词

### 阶段1触发关键词
- 接口测试
- API测试
- 接口联调
- 测试新模块
- 测试新接口

### 阶段2触发关键词（确认）
- 测试用例没问题
- 可以继续
- 确认执行
- 测试用例OK

### 非首次触发关键词
- 重新跑测试
- 运行测试
- 执行测试
- 再跑一次

## 注意事项

1. **阶段分离**: 生成测试用例后必须等待用户确认，不能自动继续执行
2. **文件位置**: 测试文件必须存储在 `{project_root}/{module_name}/` 目录下
3. **Git忽略**: 所有测试文件必须添加到 `.gitignore` 中
4. **报告格式**: 报告必须是 .md 格式，便于用户阅读
5. **状态保存**: 测试脚本可重复执行，报告可覆盖更新