# AI Prompt Engineering Studio - 数据库设计

## 概述
本产品使用5个Notion数据库和1个Supabase表来管理所有数据。

## 1. Notion数据库结构

### 1.1 Prompt主表 (`prompts`)
存储所有Prompt的当前版本和元数据。

| 字段名 | 类型 | 说明 | 必需 |
|--------|------|------|------|
| 标题 | Title | Prompt的名称 | ✅ |
| 分类 | Select | 文案/代码/数据分析/商业咨询/学术研究/角色扮演/其他 | ✅ |
| 状态 | Select | 草稿/已发布/已归档 | ✅ |
| 当前版本号 | Rich Text | 如 "V3" | ✅ |
| 当前内容 | Text | Prompt的完整内容 | ✅ |
| 创建日期 | Date | 自动设置 | ✅ |
| 最后修改日期 | Date | 自动更新 | ✅ |
| 平均评分 | Number | 1-5星，基于用户评分 | |
| 使用次数 | Number | 手动标记或自动统计 | |
| 最后使用日期 | Date | 最近一次使用的日期 | |
| 标签 | Multi-select | 用户自定义标签 | |
| 关联模板 | Relation | 关联到模板库（如果来源于模板） | |
| 待优化提醒 | Checkbox | 如果评分<3且30天未更新，自动勾选 | |

### 1.2 版本历史表 (`prompt_versions`)
存储Prompt的所有历史版本。

| 字段名 | 类型 | 说明 | 必需 |
|--------|------|------|------|
| 关联Prompt | Relation | 关联到Prompt主表 | ✅ |
| 版本号 | Rich Text | "V1", "V2" 等 | ✅ |
| 完整内容 | Text | 该版本的完整Prompt内容 | ✅ |
| 修改说明 | Text | 本次修改的摘要（用户填写） | ✅ |
| 修改日期 | Date | 自动设置 | ✅ |
| 是否为当前版本 | Checkbox | 标记是否为当前使用的版本 | ✅ |
| 优化前评分 | Number | 优化前的AI评分（0-10） | |
| 优化后评分 | Number | 优化后的AI评分（0-10） | |
| 修改类型 | Select | 新建/优化/回滚/其他 | |

### 1.3 评测记录表 (`evaluations`)
存储每次Prompt评测的结果。

| 字段名 | 类型 | 说明 | 必需 |
|--------|------|------|------|
| 关联Prompt版本 | Relation | 关联到版本历史表 | ✅ |
| 测试模型 | Select | DeepSeek/GPT-4/Claude/手动输入 | ✅ |
| 测试用例 | Text | 用于评测的输入文本 | ✅ |
| AI输出 | Text | 模型生成的输出 | ✅ |
| 清晰度评分 | Number | 1-10分 | ✅ |
| 完整性评分 | Number | 1-10分 | ✅ |
| 可执行性评分 | Number | 1-10分 | ✅ |
| 综合评分 | Number | 1-10分 | ✅ |
| 评测日期 | Date | 自动设置 | ✅ |
| 备注 | Text | 用户备注 | |
| 评测报告 | Text | AI生成的评测摘要 | |

### 1.4 模板库 (`prompt_templates`)
存储内置的Prompt模板。

| 字段名 | 类型 | 说明 | 必需 |
|--------|------|------|------|
| 模板名称 | Title | 模板的展示名称 | ✅ |
| 分类 | Select | 文案/代码/数据分析/商业咨询/学术研究/角色扮演 | ✅ |
| 适用场景 | Text | 简短描述使用场景 | ✅ |
| 模板内容 | Text | 完整的Prompt模板 | ✅ |
| 原理讲解 | Text | 3-5句解释"为什么这个Prompt有效" | ✅ |
| 使用示例 | Text | 示例输入和预期输出 | ✅ |
| 难度等级 | Select | 初级/中级/高级 | |
| 使用次数 | Number | 被用户复制的次数 | |
| 平均评分 | Number | 用户评分 | |
| 贡献者 | Text | 模板创建者 | |
| 标签 | Multi-select | 关键词标签 | |
| 是否公开 | Checkbox | 是否在模板市场中显示 | ✅ |

### 1.5 激活码表 (`activation_codes`) - Supabase
存储用户激活码，用于验证付费用户。

| 字段名 | 类型 | 说明 | 必需 |
|--------|------|------|------|
| id | UUID | 主键 | ✅ |
| activation_code | TEXT | 激活码字符串 | ✅ |
| status | TEXT | 'unused' / 'used' / 'revoked' | ✅ |
| notion_page_id | TEXT | 关联的Notion页面ID | |
| created_at | TIMESTAMP | 创建时间 | ✅ |
| used_at | TIMESTAMP | 使用时间 | |
| email | TEXT | 购买者邮箱（可选） | |
| plan | TEXT | 'standard' / 'pro' / 'team' | ✅ |

## 2. Notion页面布局设计

### Dashboard首页
- **顶部统计卡片**：
  - 总Prompt数量
  - 本月新增Prompt
  - 平均评分
  - 待优化数量
  
- **最近修改的Prompt**（表格视图，最近5条）
- **评分最高的Top 5 Prompt**（画廊视图）
- **快捷操作按钮**：
  - 新建Prompt
  - 批量评测
  - 访问模板市场
  - 优化工坊

### 模板市场页面
- **分类导航**：文案/代码/数据分析/商业咨询/学术研究/角色扮演
- **搜索框**：按名称或标签搜索
- **模板卡片**：每张卡片显示模板名称、分类、评分、使用次数
- **详情模态窗**：点击卡片查看完整模板内容、原理讲解、使用示例

### 版本对比视图
- **左右分栏布局**：左侧V1，右侧V2
- **差异高亮**：使用文本对比算法高亮显示差异
- **操作按钮**：
  - 回滚到此版本
  - 复制内容
  - 创建新版本

## 3. API与Notion集成点

### 3.1 需要自动写入Notion的操作
1. **创建新Prompt** → 在`prompts`表创建记录，在`prompt_versions`表创建V1
2. **优化Prompt** → 在`prompt_versions`表创建新版本，更新`prompts`表的当前版本
3. **评测Prompt** → 在`evaluations`表创建记录
4. **应用模板** → 复制模板内容到新Prompt记录

### 3.2 需要从Notion读取的操作
1. **获取Prompt列表** → 读取`prompts`表
2. **获取版本历史** → 读取`prompt_versions`表（按关联Prompt过滤）
3. **获取评测历史** → 读取`evaluations`表
4. **获取模板列表** → 读取`prompt_templates`表

## 4. 字段映射示例（Notion API）

### 创建Prompt记录
```json
{
  "parent": {"database_id": "prompts_db_id"},
  "properties": {
    "标题": {
      "title": [{"text": {"content": "爆款标题生成器"}}]
    },
    "分类": {
      "select": {"name": "文案写作"}
    },
    "状态": {
      "select": {"name": "已发布"}
    },
    "当前版本号": {
      "rich_text": [{"text": {"content": "V1"}}]
    },
    "当前内容": {
      "rich_text": [{"text": {"content": "你是一名资深营销专家..."}}]
    },
    "创建日期": {
      "date": {"start": "2026-05-27"}
    },
    "平均评分": {
      "number": 4.5
    }
  }
}
```

## 5. 下一步实施步骤

1. **手动创建Notion数据库**：根据上述设计，在Notion中创建5个数据库
2. **获取数据库ID**：从Notion页面URL中提取数据库ID
3. **配置环境变量**：将数据库ID添加到后端环境变量
4. **实现Notion客户端**：使用notion-client库进行读写操作
5. **测试端到端流程**：从创建Prompt到优化、评测、版本管理全流程测试

## 6. 注意事项

1. **API速率限制**：Notion API有速率限制，需合理设计请求频率
2. **数据一致性**：当同时操作多个表时，需确保数据一致性
3. **错误处理**：网络错误或API错误时需有重试和回退机制
4. **用户权限**：确保用户只能访问自己的Notion页面数据