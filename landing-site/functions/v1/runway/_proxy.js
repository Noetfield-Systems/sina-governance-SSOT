const DEFAULT_RUNWAY_RUNTIME_PATH_PREFIX = "/v1/runway";

function responseCorsHeaders() {
  const headers = new Headers();
  headers.set("access-control-allow-origin", "*");
  headers.set("access-control-allow-methods", "GET, POST, OPTIONS");
  headers.set(
    "access-control-allow-headers",
    "content-type, accept, x-runway-mode, x-runway-contract-version, x-runway-api-base-url, x-tenant-id, x-runway-session"
  );
  headers.set("cache-control", "no-store");
  return headers;
}

function resolveBackendBase(env, request) {
  const headerBase = String(request.headers.get("x-runway-api-base-url") || "").trim();
  const envBase = String((env && (env.RUNWAY_API_BASE_URL || env.RUNWAY_API_BASE || env.RUNWAY_KERNEL_BASE_URL)) || "").trim();
  const candidate = headerBase || envBase;

  if (!candidate) {
    throw new Error("RUNWAY_API_BASE_URL is not configured for this deployment");
  }

  if (!/^https?:\/\//.test(candidate)) {
    throw new Error("RUNWAY_API_BASE_URL must be an absolute https:// or http:// URL");
  }

  return candidate.replace(/\/+$/, "");
}

async function jsonErrorResponse(status, code, detail) {
  return new Response(JSON.stringify({ ok: false, code, detail }), {
    status,
    headers: {
      ...Object.fromEntries(responseCorsHeaders()),
      "content-type": "application/json; charset=utf-8",
    },
  });
}

async function runwayProxy(context, method, backendPath) {
  const { request, env } = context;
  let backendBase;
  try {
    backendBase = resolveBackendBase(env, request);
  } catch (error) {
    return jsonErrorResponse(412, "RUNWAY_API_BASE_URL_REQUIRED", String(error && error.message ? error.message : error));
  }

  const requestUrl = new URL(request.url);
  const backendTarget = new URL(`${backendPath}${requestUrl.search}`, `${backendBase}${DEFAULT_RUNWAY_RUNTIME_PATH_PREFIX}/`);

  const requestHeaders = new Headers(request.headers);
  requestHeaders.delete("host");
  if (requestHeaders.get("content-length") && requestHeaders.get("content-length") === "0") {
    requestHeaders.delete("content-length");
  }

  const upstreamRequest = {
    method,
    headers: requestHeaders,
    redirect: "manual",
  };

  if (method !== "GET" && method !== "HEAD") {
    upstreamRequest.body = request.body;
  }

  const upstreamResponse = await fetch(backendTarget.toString(), upstreamRequest);
  const outboundHeaders = responseCorsHeaders();
  const contentType = upstreamResponse.headers.get("content-type");
  if (contentType) {
    outboundHeaders.set("content-type", contentType);
  }

  return new Response(upstreamResponse.body, {
    status: upstreamResponse.status,
    headers: outboundHeaders,
  });
}

async function handleMethod(context, allowedMethod, backendPath) {
  const { request } = context;
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        ...Object.fromEntries(responseCorsHeaders()),
        "access-control-max-age": "600",
      },
    });
  }

  if (request.method !== allowedMethod) {
    return jsonErrorResponse(405, "METHOD_NOT_ALLOWED", "Method not allowed");
  }

  try {
    return await runwayProxy(context, request.method, backendPath);
  } catch (error) {
    return jsonErrorResponse(
      502,
      "RUNWAY_PROXY_ERROR",
      String(error && error.message ? error.message : error || "proxy failed")
    );
  }
}

export { handleMethod };
