(function (root) {
  class LiveRunwayProvider {
    constructor(config) {
      this.apiBaseUrl = (config.apiBaseUrl || "").replace(/\/$/, "");
      this.contractVersion = config.contractVersion || "runway.v1";
      this.tenantId = config.tenantId || "tenant-runway-staging";
      this.mode = "live";
      this.sessionToken = null;
      this.offline = !this.apiBaseUrl;
    }

    getModeLabel() {
      if (this.offline) return "OFFLINE";
      return "LIVE";
    }

    async ensureSession() {
      if (this.sessionToken) return this.sessionToken;
      const response = await fetch(`${this.apiBaseUrl}/v1/runway/session`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-tenant-id": this.tenantId,
        },
        body: "{}",
      });
      if (!response.ok) throw new Error(`session_${response.status}`);
      const session = await response.json();
      this.sessionToken = session.session_token;
      return this.sessionToken;
    }

    async run(scenarioName, hooks) {
      if (!this.apiBaseUrl) {
        throw new Error("RUNWAY_API_BASE_URL missing");
      }
      const sessionToken = await this.ensureSession();
      const goal =
        scenarioName === "webpage"
          ? "Build a deterministic landing page for Runway Live V1 with hero, proof, and CTA"
          : `Execute Runway scenario ${scenarioName}`;

      const createResponse = await fetch(`${this.apiBaseUrl}/v1/runway/runs`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "idempotency-key": `browser-${Date.now()}-${Math.random().toString(16).slice(2)}`,
          "x-tenant-id": this.tenantId,
          "x-runway-session": sessionToken,
        },
        body: JSON.stringify({
          scenario: "webpage-build-deploy",
          goal,
          mode: "live",
        }),
      });
      if (!createResponse.ok) throw new Error(`create_${createResponse.status}`);
      let snapshot = await createResponse.json();

      const approveResponse = await fetch(
        `${this.apiBaseUrl}/v1/runway/runs/${encodeURIComponent(snapshot.run_id)}/approve`,
        {
          method: "POST",
          headers: {
            "content-type": "application/json",
            "x-tenant-id": this.tenantId,
            "x-runway-session": sessionToken,
          },
          body: "{}",
        },
      );
      if (!approveResponse.ok) throw new Error(`approve_${approveResponse.status}`);
      snapshot = await approveResponse.json();

      const feed = [];
      let after = 0;
      const started = Date.now();

      const consumeEvent = async (event) => {
        const step = {
          status: /fail|block/i.test(event.type) ? "fail" : /escalat|retry/i.test(event.type) ? "warn" : "ok",
          step: event.step || event.type,
          phase: event.phase || event.type.split(".")[0] || "run",
          text: event.message,
          elapsedMs: Math.max(50, event.elapsed_ms || 120),
        };
        feed.push(step);
        if (hooks && typeof hooks.onStep === "function") {
          await hooks.onStep(step);
        }
        if (hooks && typeof hooks.onSnapshot === "function") {
          await hooks.onSnapshot(snapshot);
        }
      };

      // Prefer SSE; fall back to polling.
      let usedSse = false;
      if (typeof EventSource !== "undefined") {
        try {
          usedSse = await new Promise((resolve) => {
            const source = new EventSource(
              `${this.apiBaseUrl}/v1/runway/runs/${encodeURIComponent(snapshot.run_id)}/events/stream?after=0`,
            );
            let settled = false;
            const finish = (value) => {
              if (settled) return;
              settled = true;
              source.close();
              resolve(value);
            };
            source.addEventListener("runway", async (message) => {
              try {
                const event = JSON.parse(message.data);
                after = Math.max(after, event.hdir_sequence || 0);
                await consumeEvent(event);
              } catch (_) {
                /* ignore malformed */
              }
            });
            source.addEventListener("terminal", async (message) => {
              try {
                snapshot = JSON.parse(message.data);
              } catch (_) {
                /* ignore */
              }
              finish(true);
            });
            source.onerror = () => finish(false);
            setTimeout(() => finish(false), 120000);
          });
        } catch (_) {
          usedSse = false;
        }
      }

      if (!usedSse) {
        for (let i = 0; i < 240; i += 1) {
          const eventsResponse = await fetch(
            `${this.apiBaseUrl}/v1/runway/runs/${encodeURIComponent(snapshot.run_id)}/events?after=${after}&limit=100`,
            {
              headers: {
                "x-tenant-id": this.tenantId,
                "x-runway-session": sessionToken,
              },
            },
          );
          if (!eventsResponse.ok) throw new Error(`events_${eventsResponse.status}`);
          const page = await eventsResponse.json();
          for (const event of page.events || []) {
            after = Math.max(after, event.hdir_sequence || 0);
            await consumeEvent(event);
          }
          const snapResponse = await fetch(
            `${this.apiBaseUrl}/v1/runway/runs/${encodeURIComponent(snapshot.run_id)}`,
            {
              headers: {
                "x-tenant-id": this.tenantId,
                "x-runway-session": sessionToken,
              },
            },
          );
          if (snapResponse.ok) {
            snapshot = await snapResponse.json();
            if (hooks && typeof hooks.onSnapshot === "function") {
              await hooks.onSnapshot(snapshot);
            }
            if (["COMPLETED", "FAILED", "BLOCKED", "REVIEW_REQUIRED"].includes(snapshot.status)) {
              break;
            }
          }
          await new Promise((resolve) => setTimeout(resolve, 500));
        }
      }

      let receipt = null;
      try {
        const receiptResponse = await fetch(
          `${this.apiBaseUrl}/v1/runway/runs/${encodeURIComponent(snapshot.run_id)}/receipt`,
          {
            headers: {
              "x-tenant-id": this.tenantId,
              "x-runway-session": sessionToken,
            },
          },
        );
        if (receiptResponse.ok) receipt = await receiptResponse.json();
      } catch (_) {
        receipt = null;
      }

      return {
        runId: snapshot.run_id,
        source: "hdir-gateway",
        mode: "live",
        contractVersion: this.contractVersion,
        transport: usedSse ? "sse" : "poll",
        profile: {
          id: "webpage-build-deploy",
          name: "Webpage build + deploy",
          runType: "webpage-build-deploy",
          summary: goal,
          pain: "Landing pages ship without execution proof.",
          solution: "HDIR compiles, executes, verifies, and receipts the webpage lane.",
          reliability_target: Math.round((snapshot.reliability || 0.95) * 1000) / 10,
          cost_cap_usd: snapshot.estimated_cost_usd,
          expected_retries: snapshot.retries,
          expected_tokens: snapshot.jobs_total * 40,
          expected_model_calls: Math.max(1, Math.round(snapshot.jobs_total * (1 - (snapshot.t0_ratio || 0)))),
          risk_envelope: "Bounded webpage scenario with durable projection.",
          fallback_policy: "Workflow advances HDIR; cockpit only projects events.",
          provider_failover: true,
          steps: feed,
        },
        feed,
        snapshot,
        receipt,
        elapsedMs: Date.now() - started,
      };
    }
  }

  root.LiveRunwayProvider = LiveRunwayProvider;
})(window);
