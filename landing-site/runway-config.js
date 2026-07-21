(function (root) {
  function normalizeMode(value) {
    const candidate = String(value || "").toLowerCase();
    if (candidate === "live") {
      return "live";
    }

    if (candidate === "offline") {
      return "offline";
    }

    return "demo";
  }

  const params = new URLSearchParams(root.location.search || "");
  const envMode = typeof root.RUNWAY_MODE === "string" && root.RUNWAY_MODE.trim().length > 0 ? root.RUNWAY_MODE.trim().toLowerCase() : "";
  const envApiBase =
    typeof root.RUNWAY_API_BASE_URL === "string" && root.RUNWAY_API_BASE_URL.trim().length > 0
      ? root.RUNWAY_API_BASE_URL.trim()
      : "";
  const envContract =
    typeof root.RUNWAY_CONTRACT_VERSION === "string" && root.RUNWAY_CONTRACT_VERSION.trim().length > 0
      ? root.RUNWAY_CONTRACT_VERSION.trim()
      : "";
  const envTenant =
    typeof root.RUNWAY_TENANT_ID === "string" && root.RUNWAY_TENANT_ID.trim().length > 0
      ? root.RUNWAY_TENANT_ID.trim()
      : "tenant-runway-staging";
  const envRelease = typeof root.RUNWAY_HDIR_RELEASE_SHA === "string" && root.RUNWAY_HDIR_RELEASE_SHA.trim().length > 0
    ? root.RUNWAY_HDIR_RELEASE_SHA.trim()
    : "";

  const modeOverride =
    (params.get("runwayMode") || params.get("runway_mode") || params.get("mode") || envMode || "").toLowerCase();
  const apiBaseOverride =
    params.get("runwayApi")
    || params.get("runwayApiUrl")
    || params.get("runwayApiBase")
    || params.get("apiBase")
    || params.get("api_base_url")
    || params.get("runwayApiBaseUrl")
    || envApiBase
    || "";

  const contractOverride =
    params.get("runwayContract")
    || params.get("runwayContractVersion")
    || params.get("contract")
    || params.get("contractVersion")
    || envContract
    || "";

  const bootstrap = {
    mode: modeOverride || "demo",
    apiBaseUrl: apiBaseOverride || "",
    contractVersion: contractOverride || "runway.v1",
    tenantId: envTenant,
    runtime: {
      contractVersion: contractOverride || "runway.v1"
    },
    hdirReleaseSha: envRelease
  };
  bootstrap.mode = normalizeMode(bootstrap.mode);
  bootstrap.expectedMode = bootstrap.mode;

  const mergedRuntime = {
    ...bootstrap.runtime,
    apiBaseUrl: bootstrap.apiBaseUrl || "",
    mode: bootstrap.mode,
    tenantId: bootstrap.tenantId,
    hdirReleaseSha: bootstrap.hdirReleaseSha,
    expectedMode: bootstrap.mode
  };

  root.__RUNWAY__ = {
    ...bootstrap,
    ...(root.__RUNWAY__ || {}),
    ...(modeOverride ? { mode: modeOverride } : {}),
    ...(apiBaseOverride ? { apiBaseUrl: apiBaseOverride } : {})
  };

  root.RUNWAY_MODE = bootstrap.mode;
  root.RUNWAY_API_BASE_URL = bootstrap.apiBaseUrl;
  root.RUNWAY_CONTRACT_VERSION = bootstrap.contractVersion;
  root.RUNWAY_TENANT_ID = bootstrap.tenantId;
  root.RUNWAY_HDIR_RELEASE_SHA = bootstrap.hdirReleaseSha;
  root.RUNWAY_RUNWAY_API_BASE = bootstrap.apiBaseUrl;
  root.RUNWAY_EXPECTED_MODE = bootstrap.expectedMode;
  root.RUNWAY_RUNTIME = mergedRuntime;
})(window);
