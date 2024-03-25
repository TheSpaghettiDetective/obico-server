## 流程
1. 安装i18next-parser
2. 配置i18n-parser.config.mjs
3. 在配置文件的目录下，执行`npx i18next --config i18n-parser.config.mjs`
4. 能在指定地点生成json。

## 问题
### obico-server无法和web_ent联通
1. 在obico-server的i18next-parser.config.mjs配置中，添加web_ent的路径，无法生效
2. 将i18next-parser.config.mjs移动到tsd-enterprise根目录下，同时npm install i18n-parser -g, 执行命令，无法生效
3. 在obico-server/frontend 和 web_ent/frontend下同时添加config并将web_ent/frontend的output指向obico-server/frontend，会覆盖


## 结论
1. 只能在obico-server和web_ent的frontend中同时添加config并执行脚本。生成的路径不能是同一个文件
2. 不能将base/en.json或者zh.json直接作为i18next-parser的输出路径，他们会直接覆盖。导致翻译数量缺少（因为他无法翻译<i18next></i18next>包裹的内容）

综上：不建议使用，如果要用，只能作为参考，执行命令后，人工去对比不同文件的差异。