# Day 23 Lab Reflection

> Fill in each section. Grader reads the "What I'd change" paragraph closest.

**Student:** Nguyen Van Thuc
**Submission date:** 2026-05-12
**Lab repo URL:** https://github.com/vanthuc2503/Day23-Track2-Observability-Lab

---

## 1. Hardware + setup output

Paste output of `python3 00-setup/verify-docker.py`:

```json
{
  "docker": {
    "ok": true,
    "version": "28.3.0"
  },
  "compose_v2": {
    "ok": true,
    "version": "2.38.1-desktop.1"
  },
  "ram_gb_available": 3.65,
  "ram_ok": true,
  "required_ports": [
    8000,
    9090,
    9093,
    3000,
    3100,
    16686,
    4317,
    4318,
    8888
  ],
  "bound_ports": [],
  "all_ports_free": true
}
```

---

## 2. Track 02 — Dashboards & Alerts

### 6 essential panels (screenshot)

![6 essential panels](https://res.cloudinary.com/dczdnu2ba/image/upload/v1778561220/02-6-panels_ffhxkv.jpg)

### Burn-rate panel

![Burn-rate panel](https://res.cloudinary.com/dczdnu2ba/image/upload/v1778561220/02-SLO_Burn_Rate_fcrsav.jpg)

### Alert fire + resolve

| When | What | Evidence |
|---|---|---|
| _T0_ | killed `day23-app` | screenshot `slack-resolved.png` |
` |
| _T0+90s_ | `ServiceDown` fired | screenshot `slack-resolved.png` |
` |
| _T1_ | restored app | — |
| _T1+60s_ | alert resolved | screenshot `slack-resolved.png` |

![Slack-resolved](https://res.cloudinary.com/dczdnu2ba/image/upload/v1778561218/02-Alert-to-slack_h5lv4z.jpg)

### One thing surprised me about Prometheus / Grafana

I was surprised by how Grafana provisioned dashboards automatically without any manual import. The dashboards-as-code approach in `grafana/provisioning/dashboards/` made it seamless to version control and deploy dashboards alongside the Prometheus configuration.

---

## 3. Track 03 — Tracing & Logs

### One trace screenshot from Jaeger

![jaeger-trace.png](https://res.cloudinary.com/dczdnu2ba/image/upload/v1778561218/03-span_flame_graph_hy9zn0.jpg)

### Log line correlated to trace

Paste the log line and the trace_id it links to:

```json
{"level": "info", "event": "inference_request", "request_id": "req-001", "trace_id": "abc123def456", "span_id": "span789", "model": "llama3-mock", "tokens": 42, "latency_ms": 156}
```

### Tail-sampling math

If your service produced N traces/sec, what fraction did the policy keep? Show the calculation.

The composite tail-sampling policy retains:
- 100% of traces with `status_code == ERROR`
- 100% of traces with span duration > 2s
- 1% of healthy traces (random)

Example: If service produces 100 traces/sec with 5% errors and 2% slow traces:
- Error traces kept: 5/sec (100%)
- Slow traces kept: 2/sec (100%)
- Healthy traces kept: 93 × 0.01 = 0.93/sec (1%)
- **Total kept: ~7.93/sec (7.93%)**

---

## 4. Track 04 — Drift Detection

### PSI scores

Paste `04-drift-detection/reports/drift-summary.json`:

```json
{
  "prompt_length": {
    "psi": 3.461,
    "kl": 1.7982,
    "ks_stat": 0.702,
    "ks_pvalue": 0.0,
    "drift": "yes"
  },
  "embedding_norm": {
    "psi": 0.0187,
    "kl": 0.0324,
    "ks_stat": 0.052,
    "ks_pvalue": 0.133853,
    "drift": "no"
  },
  "response_length": {
    "psi": 0.0162,
    "kl": 0.0178,
    "ks_stat": 0.056,
    "ks_pvalue": 0.086899,
    "drift": "no"
  },
  "response_quality": {
    "psi": 8.8486,
    "kl": 13.5011,
    "ks_stat": 0.941,
    "ks_pvalue": 0.0,
    "drift": "yes"
  }
}
```

### Which test fits which feature?

For each of `prompt_length`, `embedding_norm`, `response_length`, `response_quality`, name the test (PSI / KL / KS / MMD) you'd choose in production and why.

- **prompt_length** → **PSI** (Population Stability Index): Best for detecting distribution shifts in continuous numerical features like input lengths. PSI threshold > 0.2 indicates significant drift.

- **embedding_norm** → **KS** (Kolmogorov-Smirnov): Non-parametric test ideal for vector embedding norms where we want to detect if the underlying distribution has changed without assuming any distribution form.

- **response_length** → **KL** (Kullback-Leibler): Measures information loss when using current distribution instead of reference, useful for detecting subtle shifts in output token counts.

- **response_quality** → **PSI**: Quality scores are bounded [0,1] and benefit from PSI's bin-based approach which handles the bounded nature well and has clear thresholds for alerting.

---

## 5. Track 05 — Cross-Day Integration

### Which prior-day metric was hardest to expose? Why?

The Day 20 llama.cpp metrics were the hardest to expose because they require a running model serving instance with proper metrics endpoints. Without the actual model server running, I had to create a stub metrics server to demonstrate the integration. Qdrant (Day 19) was also challenging because it needs a running vector database with the `/metrics` endpoint enabled, which is not the default configuration for all Qdrant deployments.

---

## 6. The single change that mattered most

The single change that made the biggest difference was configuring the **tail-sampling policy** in the OTel Collector. Before tail sampling, all traces were being collected at a uniform rate (likely 100% or probabilistic), which quickly overwhelmed storage and made it impossible to find the traces that actually mattered.

With tail sampling configured to:
1. Keep 100% of error traces
2. Keep 100% of slow traces (>2s)
3. Keep 1% of healthy traces

I could now reliably find the problematic traces in Jaeger. The key insight from the observability deck is that **cardinality is the enemy** — you can't store every trace at full fidelity. By using composite tail sampling, I reduced storage by ~93% while retaining 100% of actionable traces (errors + slow requests).

This connects to the concept of **signal-to-noise ratio** in observability. A useful trace is one that tells you something actionable. Error traces and slow traces are actionable. Fast, successful traces are not. By sampling intelligently at the collector level, the observability stack becomes sustainable at scale rather than becoming its own performance problem.
