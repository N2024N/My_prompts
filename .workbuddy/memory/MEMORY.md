# AI Prompt Engineering Studio - 长期记忆

## 项目信息
- **项目名称**: AI Prompt Engineering Studio
- **一句话定位**: "不只是存Prompt，而是帮你测试、优化、版本管理的一站式提示词工程工具。"
- **目标用户**: AI产品经理、AI创业者、独立开发者、内容创作者
- **定价策略**: Standard $29, Pro $49, Team $99 (一次性付费，永久使用)
- **技术栈**: Python/FastAPI + Notion + DeepSeek API + Railway + Supabase

## 技术决策记录
1. **后端语言**: Python/FastAPI (AI生态完善，用户熟悉)
2. **部署平台**: Railway ($5/月起，自动HTTPS)
3. **AI供应商**: DeepSeek为主 (成本极低，质量足够)
4. **评分模型**: 固定使用DeepSeek (保证评分标准一致性)
5. **激活码管理**: Supabase免费层 (存储激活码状态)
6. **调用限制**: 不限次数 (简化计费逻辑，成本可控)
7. **模板数量**: 首版15-20个精品模板 (质量 > 数量)

## 数据库设计要点
- **5个Notion数据库**: 
  - prompts: 36d3431ec8e68076a1e7000c59505208
  - prompt_versions: 36e3431ec8e6804d9f6a000c493f4cc4
  - evaluations: 36e3431ec8e680de85b2000c8a2d278a
  - prompt_templates: 36e3431ec8e680b4b39e000c06943ed0
  - activation_codes (Supabase): 待创建
- **关键关系**: Prompt主表 → 版本历史 → 评测记录
- **模板库独立**: 内置高质量模板 + 原理讲解

## API密钥信息
- **Notion Integration Secret**: 已提供 (ntn_140109928707...)
- **DeepSeek API Key**: 已提供 (sk-a1ede235812b...)
- **Supabase URL**: https://nbdgzuuilowcaiazldve.supabase.co
- **Supabase API Key**: sb_publishable_uv2YamrT0CiUyaR9_-QHHw_hgyNVVA0
- **Railway 用户名**: n2024n
- **Gumroad**: 待设置

## 核心功能状态
- [x] 项目框架搭建
- [x] 数据库设计完成
- [x] Notion数据库创建 (已完成)
- [ ] 后端API开发 (进行中) - Notion API集成已实现，等待数据库共享
- [x] AI能力集成 (已完成) - DeepSeek API已集成并测试
- [ ] 模板内容建设 (进行中) - 首个模板已入库，第二个模板构建中
- [ ] Gumroad销售页 (待开始)

## 用户偏好记录
- 偏好现代UI，简洁布局
- 重视逻辑严密，表达流畅
- 喜欢直接、不废话的沟通风格
- 对视觉设计有较高要求
- 有付费产品开发经验

## 模板分类决策
- **首个模板分类**：商业咨询（高级课程内容研究员）
- **下一个分类**：代码生成（面向开发者用户）
- **扩展策略**：基于目标用户需求，按优先级排序：代码生成 → 文案写作 → 数据分析 → 角色扮演

## 重要日期
- 2026-05-27: 项目启动，技术决策确认，框架搭建
- 计划上线: 2026年6月中旬

## 注意事项
1. Notion API有速率限制，需优化请求频率
2. DeepSeek API成本极低，但仍需监控使用量
3. 激活码系统需防止滥用
4. 模板内容的质量是产品核心壁垒
5. Gumroad预售可验证市场需求