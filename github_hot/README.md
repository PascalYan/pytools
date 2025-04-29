# GitHub热门项目自动发布工具

这个工具可以自动抓取GitHub上最热门的Python项目，并生成文章发布到微信公众号。

## 功能特点

- 自动抓取GitHub热门Python项目
- 生成格式化的文章内容
- 自动发布到微信公众号
- 支持自定义时间范围（日/周/月）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 创建`.env`文件，添加以下配置：

```
GITHUB_TOKEN=你的GitHub个人访问令牌
WECHAT_APP_ID=你的微信公众号APP_ID
WECHAT_APP_SECRET=你的微信公众号APP_SECRET
```

2. 获取GitHub Token：
   - 访问 https://github.com/settings/tokens
   - 点击 "Generate new token"
   - 选择需要的权限（至少需要 `repo` 权限）

3. 获取微信公众号配置：
   - 登录微信公众平台
   - 在"开发"->"基本配置"中获取AppID和AppSecret

## 使用方法

直接运行主程序：

```bash
python github_hot.py
```

## 注意事项

- 确保有稳定的网络连接
- GitHub API有访问限制，请合理使用
- 微信公众号发布文章需要认证账号
- 建议使用定时任务定期运行程序 