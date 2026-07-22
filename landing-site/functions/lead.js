function jsonResponse(statusCode, payload) {
  return new Response(JSON.stringify(payload), {
    status: statusCode,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "cache-control": "no-store"
    }
  });
}

function makeLeadId() {
  const random = crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `lead-${random.replace(/[^a-zA-Z0-9-]/g, "").toLowerCase()}`;
}

function sanitizeString(value) {
  if (typeof value !== "string") {
    return "";
  }

  return value.replace(/\s+/g, " ").trim().slice(0, 1200);
}

function successEnvelope(leadData) {
  return {
    ok: true,
    ...leadData
  };
}

function errorEnvelope(code, detail) {
  return {
    ok: false,
    code,
    detail
  };
}

function buildLeadPayload(request, payload) {
  const email = sanitizeString(payload.email);
  const company = sanitizeString(payload.company);
  const usecase = sanitizeString(payload.usecase);
  const goal = sanitizeString(payload.goal || payload.message || "");

  if (!email || !company || !usecase) {
    return {
      ok: false,
      code: "MISSING_REQUIRED_FIELDS",
      detail: "email, company, and usecase are required"
    };
  }

  const leadId = makeLeadId();
  const acceptedAt = new Date().toISOString();
  const source = sanitizeString(payload.source || "noetfield-runway-standalone");
  const page = sanitizeString(payload.page || "/");
  const utm = payload.utm || null;

  return {
    ok: true,
    leadId,
    acceptedAt,
    source,
    page,
    payload: {
      email,
      company,
      usecase,
      goal
    },
    utm,
    next: {
      step: "Sales follow-up queued",
      action: "manual-review",
      nextPage: "/thank-you"
    }
  };
}

async function onRequestPost(context) {
  const { request } = context;

  let payload;
  try {
    payload = await request.json();
  } catch (_error) {
    return jsonResponse(400, errorEnvelope("INVALID_JSON", "Request body must be valid JSON"));
  }

  const lead = buildLeadPayload(request, payload);
  if (!lead.ok) {
    return jsonResponse(422, lead);
  }

  return jsonResponse(200, successEnvelope(lead));
}

function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "POST, OPTIONS",
      "access-control-allow-headers": "content-type",
      "access-control-max-age": "600"
    }
  });
}

function methodNotAllowed(method) {
  return jsonResponse(405, errorEnvelope("METHOD_NOT_ALLOWED", `Method ${method} not supported for /lead`));
}

export function onRequest(context) {
  const { request } = context;

  switch (request.method) {
    case "POST":
      return onRequestPost(context);
    case "OPTIONS":
      return onRequestOptions();
    case "GET":
      return methodNotAllowed("GET");
    case "HEAD":
      return methodNotAllowed("HEAD");
    default:
      return methodNotAllowed(request.method || "UNKNOWN");
  }
}

export { onRequestPost, onRequestOptions };
