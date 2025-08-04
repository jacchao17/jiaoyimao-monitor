# 交易猫无畏契约商品爬虫

这是一个自动化爬虫项目，用于爬取交易猫网站上无畏契约（Valorant）的商品信息，包括价格、已用源晶（无畏点数）、皮肤数量、英雄数量等数据。

## 功能特点

- 🔍 **智能数据提取**：自动提取商品价格、已用源晶、皮肤数量、英雄数量、段位等信息
- 📊 **数据分析**：提供价格区间分布、段位分布等统计分析
- 💾 **多格式保存**：支持CSV和JSON格式数据保存
- 🛡️ **反爬虫保护**：使用随机User-Agent、请求延迟等技术避免被封
- 🌐 **双引擎支持**：提供requests和Selenium两种爬取方式
- 📈 **实时监控**：详细的日志输出，实时显示爬取进度

## 项目结构

```
交易猫自动/
├── requirements.txt          # 项目依赖
├── config.py               # 配置文件
├── jiaoyimao_scraper.py    # requests版本爬虫
├── jiaoyimao_selenium_scraper.py  # Selenium版本爬虫
├── run_scraper.py          # 运行脚本
└── README.md               # 项目说明
```

## 安装说明

### 1. 环境要求

- Python 3.7+
- Chrome浏览器（使用Selenium版本时需要）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装Chrome浏览器（可选）

如果使用Selenium版本，需要安装Chrome浏览器：
- Windows: 下载并安装 [Google Chrome](https://www.google.com/chrome/)
- 程序会自动下载对应的ChromeDriver

## 使用方法

### 方法一：使用requests版本（推荐）

```bash
python jiaoyimao_scraper.py
```

### 方法二：使用Selenium版本

```bash
python jiaoyimao_selenium_scraper.py
```

### 方法三：使用运行脚本

```bash
python run_scraper.py
```

## 数据字段说明

爬取的数据包含以下字段：

| 字段名 | 说明 | 示例 |
|--------|------|------|
| title | 商品标题 | "6橙皮 3金皮 5紫皮 51皮肤 25英雄 79卡面 680已用源晶 黄金" |
| price | 商品价格（元） | 1100.0 |
| stock | 库存数量 | 1 |
| source_crystal | 已用源晶数量 | 680 |
| orange_skin | 橙色皮肤数量 | 6 |
| gold_skin | 金色皮肤数量 | 3 |
| purple_skin | 紫色皮肤数量 | 5 |
| hero_count | 英雄数量 | 25 |
| card_count | 卡面数量 | 79 |
| rank | 段位 | "黄金" |
| product_type | 商品类型 | "QQ帐号" |
| seller_credit | 卖家信用 | "新卖家（近7天：暂无交易）" |
| crawl_time | 爬取时间 | "2024-01-01 12:00:00" |

## 配置说明

可以通过修改 `config.py` 文件来调整爬虫行为：

```python
# 爬取设置
MAX_PAGES = 5  # 最大爬取页数
DELAY_BETWEEN_PAGES = 2  # 页面间延迟（秒）

# 浏览器设置
HEADLESS_MODE = True  # 是否使用无头模式

# 数据过滤设置
MIN_PRICE = 0  # 最低价格
MAX_PRICE = 100000  # 最高价格
```

## 输出文件

程序运行后会生成以下文件：

- `jiaoyimao_products_YYYYMMDD_HHMMSS.csv` - CSV格式数据
- `jiaoyimao_products_YYYYMMDD_HHMMSS.json` - JSON格式数据

## 数据分析

程序会自动分析爬取的数据并提供以下统计信息：

- 总商品数量
- 价格范围和平均值
- 已用源晶范围和平均值
- 价格区间分布
- 段位分布

## 注意事项

1. **遵守网站规则**：请合理使用爬虫，避免对目标网站造成过大压力
2. **延迟设置**：建议保持适当的请求延迟，避免被封IP
3. **数据准确性**：爬取的数据仅供参考，实际交易请以网站显示为准
4. **法律合规**：请确保您的使用符合相关法律法规

## 故障排除

### 常见问题

1. **ChromeDriver错误**
   - 解决方案：程序会自动下载ChromeDriver，如果失败请手动安装

2. **网络连接问题**
   - 解决方案：检查网络连接，尝试使用代理

3. **页面结构变化**
   - 解决方案：更新CSS选择器或联系开发者

### 日志查看

程序会输出详细的日志信息，包括：
- 爬取进度
- 错误信息
- 数据统计

## 技术栈

- **Python 3.7+**
- **requests** - HTTP请求库
- **BeautifulSoup4** - HTML解析
- **Selenium** - 浏览器自动化
- **pandas** - 数据处理
- **fake-useragent** - 随机User-Agent

## 许可证

本项目仅供学习和研究使用，请勿用于商业用途。

## 更新日志

- v1.0.0 - 初始版本，支持基本的商品信息爬取
- 支持requests和Selenium两种爬取方式
- 添加数据分析和多格式保存功能

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件

---

**免责声明**：本项目仅用于技术学习和研究，使用者需自行承担使用风险，开发者不承担任何法律责任。 