const encoder = new TextEncoder();

export function json(body, status = 200) {
  return Response.json(body, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

export function clip(value, max = 12000) {
  const text = typeof value === "string" ? value : JSON.stringify(value);
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

export function parseModelJson(text) {
  if (!text) return null;
  const trimmed = String(text).trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  try {
    return JSON.parse(trimmed);
  } catch {
    const start = trimmed.indexOf("{");
    const end = trimmed.lastIndexOf("}");
    if (start < 0 || end <= start) return null;
    try {
      return JSON.parse(trimmed.slice(start, end + 1));
    } catch {
      return null;
    }
  }
}

async function fixedHash(value) {
  return crypto.subtle.digest("SHA-256", encoder.encode(String(value || "")));
}

export async function secretMatches(provided, expected) {
  if (!expected) return false;
  const [a, b] = await Promise.all([fixedHash(provided), fixedHash(expected)]);
  return crypto.subtle.timingSafeEqual(a, b);
}

function pemToArrayBuffer(pem) {
  const b64 = pem
    .replace(/-----BEGIN [^-]+-----/g, "")
    .replace(/-----END [^-]+-----/g, "")
    .replace(/\s+/g, "");
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i += 1) bytes[i] = bin.charCodeAt(i);
  return bytes.buffer;
}

function b64url(input) {
  const bytes = input instanceof ArrayBuffer ? new Uint8Array(input) : input;
  let raw = "";
  for (const byte of bytes) raw += String.fromCharCode(byte);
  return btoa(raw).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

export function resolveGithubIdentity(env, role = "builder") {
  if (role === "verifier") {
    // Disjoint from Motor. Prefer the SG candidate app; never the denied legacy advisory app.
    const appId = String(env.VERIFIER_GITHUB_APP_ID || env.SG_CANDIDATE_APP_ID || "4330805").trim();
    const installationId = String(
      env.VERIFIER_GITHUB_INSTALLATION_ID || env.SG_CANDIDATE_INSTALLATION_ID || "147378007",
    ).trim();
    const pem = String(
      env.VERIFIER_GITHUB_APP_PRIVATE_KEY || env.SG_CANDIDATE_APP_PRIVATE_KEY || "",
    ).trim();
    if (appId === "4179901" || installationId === "143449507") {
      throw new Error("legacy_advisory_app_denied_for_verifier");
    }
    if (appId === "4275961" || installationId === "145975487") {
      throw new Error("motor_app_denied_for_verifier_identity");
    }
    if (!pem) throw new Error("VERIFIER_GITHUB_APP_PRIVATE_KEY_missing");
    return { role, appId, installationId, pem, secret_name: "VERIFIER_GITHUB_APP_PRIVATE_KEY" };
  }

  const appId = String(env.MOTOR_APP_ID || "4275961").trim();
  const installationId = String(env.MOTOR_INSTALLATION_ID || "145975487").trim();
  const pem = String(env.MOTOR_APP_PRIVATE_KEY || "").trim();
  if (appId === "4179901" || installationId === "143449507") {
    throw new Error("legacy_advisory_app_denied_for_builder");
  }
  if (appId === "4330805" || installationId === "147378007") {
    throw new Error("sg_candidate_app_denied_for_builder_identity");
  }
  if (!pem) throw new Error("MOTOR_APP_PRIVATE_KEY_missing");
  return { role: "builder", appId, installationId, pem, secret_name: "MOTOR_APP_PRIVATE_KEY" };
}

export async function mintInstallationToken(env, role = "builder") {
  const identity = resolveGithubIdentity(env, role);
  const now = Math.floor(Date.now() / 1000);
  const header = b64url(encoder.encode(JSON.stringify({ alg: "RS256", typ: "JWT" })));
  const payload = b64url(
    encoder.encode(
      JSON.stringify({ iat: now - 60, exp: now + 540, iss: Number(identity.appId) }),
    ),
  );
  const key = await crypto.subtle.importKey(
    "pkcs8",
    pemToArrayBuffer(identity.pem),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    key,
    encoder.encode(`${header}.${payload}`),
  );
  const jwt = `${header}.${payload}.${b64url(signature)}`;
  const response = await fetch(
    `https://api.github.com/app/installations/${identity.installationId}/access_tokens`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${jwt}`,
        Accept: "application/vnd.github+json",
        "User-Agent": "nf-hourly-ai-circles-v1",
        "X-GitHub-Api-Version": "2022-11-28",
      },
    },
  );
  if (!response.ok) throw new Error(`installation_token_${response.status}`);
  const body = await response.json();
  if (!body.token) throw new Error("installation_token_empty");
  return body.token;
}

export async function github(token, path, init = {}) {
  const response = await fetch(`https://api.github.com${path}`, {
    ...init,
    signal: init.signal || AbortSignal.timeout(30_000),
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "nf-hourly-ai-circles-v1",
      "X-GitHub-Api-Version": "2022-11-28",
      ...(init.headers || {}),
    },
  });
  const declaredSize = Number(response.headers.get("content-length") || 0);
  if (declaredSize > 2_000_000) throw new Error("github_response_too_large");
  const text = await response.text();
  if (text.length > 2_000_000) throw new Error("github_response_too_large");
  let body = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }
  if (!response.ok) {
    throw new Error(`github_${response.status}:${clip(body, 300)}`);
  }
  return body;
}

function providerConfig(env, name) {
  const configs = {
    deepseek: {
      kind: "chat",
      key: env.DEEPSEEK_API_KEY,
      url: "https://api.deepseek.com/v1/chat/completions",
      model: env.DEEPSEEK_MODEL || "deepseek-chat",
    },
    glm: {
      kind: "chat",
      key: env.GLM_API_KEY,
      url: "https://open.bigmodel.cn/api/paas/v4/chat/completions",
      model: env.GLM_MODEL || "glm-4-flash",
    },
    kimi: {
      kind: "chat",
      key: env.MOONSHOT_API_KEY,
      url: "https://api.moonshot.ai/v1/chat/completions",
      model: env.KIMI_MODEL || "moonshot-v1-8k",
    },
    huggingface: {
      kind: "chat",
      key: env.HF_TOKEN,
      url: "https://router.huggingface.co/v1/chat/completions",
      model: env.HF_MODEL || "Qwen/Qwen2.5-7B-Instruct",
    },
    openai: {
      kind: "responses",
      key: env.OPENAI_API_KEY || env.VERIFIER_OPENAI_API_KEY,
      url: "https://api.openai.com/v1/responses",
      model: env.OPENAI_MODEL || "gpt-5-mini",
    },
    gemini: {
      kind: "gemini",
      key: env.GEMINI_API_KEY || env.VERIFIER_GEMINI_API_KEY,
      model: env.GEMINI_MODEL || "gemini-2.5-flash-lite",
    },
    workers_ai: {
      kind: "workers_ai",
      model: env.WORKERS_AI_MODEL || "@cf/meta/llama-3.2-3b-instruct",
    },
  };
  return configs[name];
}

async function invokeProvider(env, name, system, user, maxTokens) {
  const cfg = providerConfig(env, name);
  if (!cfg) throw new Error("unknown_provider");
  if (cfg.kind === "workers_ai") {
    if (!env.AI) throw new Error("missing_AI_binding");
    const output = await env.AI.run(cfg.model, {
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
      max_tokens: maxTokens,
      temperature: 0.1,
    });
    return output?.response || output?.result?.response || JSON.stringify(output);
  }
  if (
    String(env.MODE || "").startsWith("PRODUCTION_") &&
    !String(env.COMMERCIAL_MODEL_ESCALATION_RECEIPT_ID || "").trim()
  ) {
    throw new Error("commercial_model_requires_escalation_receipt");
  }
  if (!String(cfg.key || "").trim()) throw new Error("missing_key");
  let url = cfg.url;
  let body;
  if (cfg.kind === "gemini") {
    url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(cfg.model)}:generateContent?key=${encodeURIComponent(cfg.key)}`;
    body = {
      systemInstruction: { parts: [{ text: system }] },
      contents: [{ role: "user", parts: [{ text: user }] }],
      generationConfig: { temperature: 0.1, maxOutputTokens: maxTokens },
    };
  } else if (cfg.kind === "responses") {
    body = {
      model: cfg.model,
      instructions: system,
      input: user,
      max_output_tokens: maxTokens,
    };
  } else {
    body = {
      model: cfg.model,
      temperature: 0.1,
      max_tokens: maxTokens,
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
    };
  }
  const response = await fetch(url, {
    method: "POST",
    signal: AbortSignal.timeout(45_000),
    headers: {
      ...(cfg.kind === "gemini" ? {} : { Authorization: `Bearer ${cfg.key}` }),
      "Content-Type": "application/json",
      "User-Agent": "nf-hourly-ai-circles-v1",
    },
    body: JSON.stringify(body),
  });
  const text = await response.text();
  let parsed = null;
  try {
    parsed = JSON.parse(text);
  } catch {
    parsed = null;
  }
  if (!response.ok) throw new Error(`${name}_${response.status}:${text.slice(0, 180)}`);
  if (cfg.kind === "gemini") {
    return parsed?.candidates?.[0]?.content?.parts?.map((part) => part.text || "").join("") || "";
  }
  if (cfg.kind === "responses") {
    if (parsed?.output_text) return parsed.output_text;
    return (
      parsed?.output
        ?.flatMap((item) => item.content || [])
        .map((item) => item.text || "")
        .join("") || ""
    );
  }
  return parsed?.choices?.[0]?.message?.content || parsed?.choices?.[0]?.text || "";
}

export async function runRole(env, role, preferred, system, user, maxTokens = 900) {
  const order = [preferred, ..."deepseek,glm,kimi,openai,gemini,huggingface,workers_ai".split(",")]
    .filter((name, index, all) => name && all.indexOf(name) === index);
  const errors = [];
  for (const provider of order) {
    try {
      const content = await invokeProvider(env, provider, system, clip(user, 28000), maxTokens);
      if (!String(content || "").trim()) throw new Error("empty_content");
      return { ok: true, role, provider, content: clip(content, 16000) };
    } catch (error) {
      errors.push({ provider, error: String(error?.message || error).slice(0, 220) });
    }
  }
  return { ok: false, role, provider: null, content: null, errors };
}

export async function checkPeerAndRestart(env, healthUrl, tickUrl) {
  if (!healthUrl) return { checked: false, reason: "peer_not_configured" };
  try {
    const healthResponse = await fetch(healthUrl, {
      signal: AbortSignal.timeout(10_000),
      headers: { Accept: "application/json", "User-Agent": "nf-hourly-ai-circles-v1" },
    });
    const health = await healthResponse.json();
    const fired = Date.parse(health.last_fired_at || "");
    const stale = !Number.isFinite(fired) || Date.now() - fired > 2 * 60 * 60 * 1000;
    if (!stale) return { checked: true, stale: false, last_fired_at: health.last_fired_at };
    if (!tickUrl || !env.PEER_TICK_SECRET) {
      return { checked: true, stale: true, restarted: false, reason: "restart_not_configured" };
    }
    const restart = await fetch(tickUrl, {
      method: "POST",
      signal: AbortSignal.timeout(10_000),
      headers: {
        Authorization: `Bearer ${env.PEER_TICK_SECRET}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ source: "independent_deadman" }),
    });
    return {
      checked: true,
      stale: true,
      restarted: restart.ok,
      restart_status: restart.status,
      last_fired_at: health.last_fired_at || null,
    };
  } catch (error) {
    return { checked: true, stale: true, restarted: false, error: String(error?.message || error) };
  }
}
