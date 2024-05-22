# 私人在线阅读 PDF 项目

## 项目简介

这个项目主要用于私人在线阅读 PDF 文件。项目使用纯前端技术，不依赖后端服务。通过读取一个名为 `pdfList.json` 的静态 JSON 文件来获取 PDF 文件列表，并按照分类展示到网页上。

## 使用方法

1. 将你的 PDF 文件按照分类放入 `pdf/` 文件夹中。
2. 运行相应的脚本（Python、Shell 或 Batch 脚本）来自动生成 `pdfList.json` 文件。
3. 打开 `index.html`，你将看到一个按照分类整理的 PDF 文件列表。

## 自动更新 `pdfList.json`

为了使 `pdfList.json` 能够自动更新，你可以使用以下任一方法：

- Python 脚本

这些脚本可以通过任务计划器（Windows）或 cron 任务（Linux/Mac）来定期运行。

## 样式定制

你可以通过修改 `index.html` 中的 CSS 代码来定制页面样式。

## 联系信息

如果你有任何问题或建议，请随时联系。

---

**注意：** 这个项目仅用于私人用途，不建议用于商业或公开的场合。
sha256~aI516MVG1-ZAx__jq8NxD9qxnOwVf7qP7NYDwM0ZnOA
