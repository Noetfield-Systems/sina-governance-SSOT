(function (root) {
  class DemoRunwayProvider {
    constructor(scenarioFeed) {
      this.scenarioFeed = scenarioFeed;
      this.mode = "demo";
    }

    getModeLabel() {
      return "DEMO";
    }

    async run(scenarioName, hooks) {
      const profile = this.scenarioFeed[scenarioName] || this.scenarioFeed.decision;
      const runId = `NR-DEMO-${Date.now()}`;
      const start = Date.now();
      const feed = [];
      for (const step of profile.steps || []) {
        feed.push(step);
        if (hooks && typeof hooks.onStep === "function") {
          await hooks.onStep({
            status: step.status,
            step: step.step,
            phase: step.phase || step.step,
            text: step.text,
            elapsedMs: step.elapsedMs || 700,
            recovered: step.recovered === true,
          });
        }
        if (hooks && typeof hooks.delay === "function") {
          await hooks.delay(step.elapsedMs || 700);
        }
      }
      return {
        runId,
        source: "local-simulator",
        mode: "demo",
        profile,
        feed,
        snapshot: {
          run_id: runId,
          status: "COMPLETED",
          jobs_total: feed.length,
          jobs_completed: feed.length,
          t0_ratio: 1,
          reliability: (profile.reliability_target || 99) / 100,
          retries: profile.expected_retries || 0,
          estimated_cost_usd: profile.cost_cap_usd || 0,
          last_hdir_sequence: feed.length,
        },
        receipt: null,
        elapsedMs: Date.now() - start,
      };
    }
  }

  root.DemoRunwayProvider = DemoRunwayProvider;
})(window);
