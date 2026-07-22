import { handleMethod } from "../../_proxy.js";

export async function onRequest(context) {
  const runId = String(context.params?.runId || "").trim();
  if (!runId) {
    return new Response(JSON.stringify({ ok: false, code: "RUN_ID_MISSING", detail: "runId path parameter is required." }), {
      status: 400,
      headers: {
        "content-type": "application/json; charset=utf-8",
        "access-control-allow-origin": "*",
      },
    });
  }

  const encodedRunId = encodeURIComponent(runId);
  return handleMethod(context, "GET", `/v1/runway/runs/${encodedRunId}/receipt`);
}
