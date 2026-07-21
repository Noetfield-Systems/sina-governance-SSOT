(function (root) {
  // Default bootstrap is DEMO. deploy.sh overwrites this file at deploy time for LIVE staging/preview.
  root.RUNWAY_MODE = root.RUNWAY_MODE || "demo";
  root.RUNWAY_API_BASE_URL = root.RUNWAY_API_BASE_URL || "";
  root.RUNWAY_CONTRACT_VERSION = root.RUNWAY_CONTRACT_VERSION || "runway.v1";
  root.RUNWAY_TENANT_ID = root.RUNWAY_TENANT_ID || "tenant-runway-staging";
  root.__RUNWAY__ = {
    mode: root.RUNWAY_MODE,
    apiBaseUrl: root.RUNWAY_API_BASE_URL,
    contractVersion: root.RUNWAY_CONTRACT_VERSION,
    tenantId: root.RUNWAY_TENANT_ID,
    ...(root.__RUNWAY__ || {})
  };
})(window);
