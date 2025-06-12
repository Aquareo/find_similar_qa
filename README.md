
# find_similar_qa

项目说明，企微后台应用部署QA匹配，问题响应接口，根据query，返回问题库中最相似的几个问题

**“新版本”**有明显的**功能优化和性能提升**

---

## ✅ 优化点：

### ✅ 1. **Embedding 向量预加载（性能大提升）**

#### ✔ 新版本：

```python
question_embeddings = model.encode(questions, convert_to_tensor=True)  # 在加载时就完成
```

#### ✖ 旧版本：

```python
question_embeddings = model.encode(questions, convert_to_tensor=True)  # 每次调用 /ask 都重新 encode
```

* **优点**：新版本只在程序启动时进行一次 embedding 编码，大大节省了每次查询的时间，适合高并发服务。
* **旧版本问题**：每次请求都重新计算 `question_embeddings`，当问题量一大，严重拖慢响应速度，是造成“有点慢”的关键。

---

### ✅ 2. **更强的错误处理**

新版本 `load_qa()` 中判断了 Excel 文件的结构是否合理，提示信息更友好：

```python
if 'Question' not in df.columns or 'Answer' not in df.columns:
    raise ValueError("Excel 必须包含 'Question' 和 'Answer' 列")
```

旧版本也做了类似的判断，但新版本还把这个逻辑封装成函数 `load_qa()`，更利于 **热更新和重载设计**。

---

### ✅ 3. **模块化设计**

* 新版本的代码将 `load_qa()`、`search_qa()` 抽离出来，是良好的结构化设计。
* 旧版本将所有逻辑堆叠在 `/ask` 中，不利于复用和维护。

---

### ✅ 4. **扩展性更强**

新版本版本已经预留了：

* 企业微信 webhook 支持（含 GET 验证和 POST 消息响应）
* XML 构造输出
* 本地 `/ask` 调试接口
* 后续可以轻松添加热加载、定时同步、格式美化等

而旧版本仅限本地 `/ask`，不能部署成实际服务。

---

### ✅ 5. **代码规范更高**

* 使用 `Path(__file__).parent` 兼容部署路径
* 使用了 `FastAPI` 的 `Query` 参数验证
* 明确 `convert_to_tensor=True` 避免默认行为导致性能波动

---

## 📊 性能对比图示（关键开销差异）

| 步骤           | 新版本代码（预处理）  | 旧版本代码（每次处理）       |
| ------------ | ---------- | ---------------- |
| 读取 Excel     | 启动时        | 启动时              |
| 编码 Questions | 启动时一次性完成 ✅ | 每次请求都重新 encode ❌ |
| 编码 Query     | 每次         | 每次               |
| 相似度计算        | 每次         | 每次               |
| 总体延迟         | **低** ✅    | **高（指数增长）** ❌    |

---

## ✅ 总结一句话：

> \*\*新版本更专业、更高效、更适合部署上线服务。\*\*旧的版本仅适合“功能原型验证”，不适合生产环境或大数据量场景。

更进一步，还可以做如下优化：

* 精确接口响应时间评估（benchmark）
* 启用 `torch.no_grad()` 加速
* 多线程/异步支持
* 自动定时热加载 QA 数据

