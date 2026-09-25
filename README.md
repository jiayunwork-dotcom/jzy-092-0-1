# 固定床离子交换穿透计算服务

给定床层运行工况,沿时间轴展开 Thomas 模型的出水浓度曲线,并从曲线上
读出穿透时刻与累计吸附量。仅经 HTTP 对外提供,不附带页面。

## 模型

Thomas 解的固定形式:

```
C(t)/C0 = 1 / (1 + exp(kTh * (q0*m/Q - C0*t)))
```

- `C0`  进料浓度
- `Q`   体积流量
- `q0`  床层单位吸附容量
- `kTh` Thomas 速率常数
- `m`   填料质量

指数项随时间从正变负,曲线从低往高单调爬升。时间轴终点取在穿透中点
(`q0*m/(Q*C0)`)之后再留 20 个单位的指数裕量,保证末端接近饱和,
亏量积分 `Q*C0*∫(1 - C/C0)dt` 收敛到理论容量 `q0*m`。

## 模块结构

```
app/
  thomas.py        Thomas 解逐点求值(穿透内核)
  timeaxis.py      时间轴离散
  integrate.py     浓度亏量数值积分(梯形法则,纯标准库)
  breakthrough.py  穿透时刻判定与爬升窗
  validation.py    工况入参校验
  service.py       单一工况完整计算编排
  batch.py         批量工况调度(逐条独立,互不累加)
  reference.py     预置软化床参考工况
  api.py           Flask HTTP 接口层
tests/             pytest 测试套件
```

## HTTP 接口

服务监听固定端口 **8000**。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET  | `/health` | 健康检查 |
| GET  | `/api/v1/reference-case` | 预置软化床参考工况 |
| POST | `/api/v1/breakthrough` | 单一工况:曲线 + 穿透时刻 + 累计吸附量 |
| POST | `/api/v1/breakthrough/batch` | 批量工况:逐条产出各自结果 |

### 单一工况

```bash
curl -X POST http://localhost:8000/api/v1/breakthrough \
  -H 'Content-Type: application/json' \
  -d '{"c0": 100.0, "flow": 10.0, "q0": 50.0, "k_th": 0.005, "mass": 2000.0}'
```

请求体字段:`c0`、`flow`、`q0`、`k_th`、`mass`(均须为正数,否则
返回 400 及原因),可选 `points`(采样点数,默认 400)与
`threshold`(穿透阈值,默认 0.1)。

响应要点:

```json
{
  "curve": {"time": [...], "ratio": [...], "concentration": [...]},
  "breakthrough_time": 95.6,
  "cumulative_adsorption": 99990.0,
  "capacity": 100000.0,
  "saturation_ratio": 0.9999,
  "saturated": true
}
```

### 批量工况

```bash
curl -X POST http://localhost:8000/api/v1/breakthrough/batch \
  -H 'Content-Type: application/json' \
  -d '{"cases": [
        {"c0": 100.0, "flow": 10.0, "q0": 50.0, "k_th": 0.005, "mass": 2000.0},
        {"c0": 100.0, "flow": 20.0, "q0": 50.0, "k_th": 0.005, "mass": 2000.0}
      ]}'
```

每条工况独立求解,结果按 `index` 一一对应;单条校验失败只标记该条
(`ok: false` 并附原因),不影响其余条目。

## 运行

本地(Python 3.12):

```bash
pip install -r requirements.txt
python -m app          # 监听 0.0.0.0:8000
```

Docker:

```bash
docker build -t breakthrough-service .
docker run --rm -p 8000:8000 breakthrough-service
```

## 测试

```bash
# 本地
python -m pytest -q

# 容器内(同一镜像)
docker run --rm breakthrough-service python -m pytest -q
```

测试锁住的关键关系:单位吸附容量加倍穿透时刻大致推后一倍、体积流量
加倍穿透提前、速率常数增大 10%–90% 爬升窗收窄、进料浓度为零报错、
累计吸附量趋近理论容量 `q0*m`、曲线从低往高单调爬升。
