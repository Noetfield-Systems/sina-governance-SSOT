const APP_ID = "4179901";
const INSTALLATION_ID = "143449507";
const OWNER = "kazemnezhadsina144-dot";
const REPO = "sina-governance-SSOT";
const BRANCH = "main";
const SSOT_PATH = "ssot/strategy-ssot-v6-split.md";
const EXPECTED_SHA256 = "1ba4a793dba183388afd244ea21e850cad879c78824f78603e961070ae9b3af4";
const GITHUB_API = "https://api.github.com";
const SECONDARY_CF_ACCOUNT_ID = "b7282b4a5c17b84d62e3ef8866b878f8";

function base64Url(input) {
  const bytes = input instanceof Uint8Array ? input : new TextEncoder().encode(input);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function base64ToBytes(input) {
  const normalized = input.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

function encodeDerLength(length) {
  if (length < 0x80) return new Uint8Array([length]);

  const bytes = [];
  let value = length;
  while (value > 0) {
    bytes.unshift(value & 0xff);
    value >>= 8;
  }
  return new Uint8Array([0x80 | bytes.length, ...bytes]);
}

function der(tag, value) {
  const length = encodeDerLength(value.length);
  const output = new Uint8Array(1 + length.length + value.length);
  output[0] = tag;
  output.set(length, 1);
  output.set(value, 1 + length.length);
  return output;
}

function concatBytes(...chunks) {
  const total = chunks.reduce((size, chunk) => size + chunk.length, 0);
  const output = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    output.set(chunk, offset);
    offset += chunk.length;
  }
  return output;
}

function pkcs1ToPkcs8(pkcs1) {
  const version = der(0x02, new Uint8Array([0x00]));
  const rsaEncryptionOid = new Uint8Array([0x06, 0x09, 0x2a, 0x86, 0x48, 0x86, 0xf7, 0x0d, 0x01, 0x01, 0x01]);
  const nullParam = new Uint8Array([0x05, 0x00]);
  const algorithm = der(0x30, concatBytes(rsaEncryptionOid, nullParam));
  const privateKey = der(0x04, pkcs1);
  return der(0x30, concatBytes(version, algorithm, privateKey));
}

function pemToPkcs8(pem) {
  const isPkcs1 = pem.includes("BEGIN RSA PRIVATE KEY");
  const body = pem
    .replace(/-----BEGIN [^-]+-----/g, "")
    .replace(/-----END [^-]+-----/g, "")
    .replace(/\s+/g, "");
  const bytes = base64ToBytes(body);
  return isPkcs1 ? pkcs1ToPkcs8(bytes) : bytes;
}

async function createJwt(privateKeyPem) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: "RS256", typ: "JWT" };
  const payload = {
    iat: now - 60,
    exp: now + 540,
    iss: APP_ID,
  };
  const signingInput = `${base64Url(JSON.stringify(header))}.${base64Url(JSON.stringify(payload))}`;
  const key = await crypto.subtle.importKey(
    "pkcs8",
    pemToPkcs8(privateKeyPem),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(signingInput));
  return `${signingInput}.${base64Url(new Uint8Array(signature))}`;
}

async function githubJson(path, token, init = {}) {
  const response = await fetch(`${GITHUB_API}${path}`, {
    ...init,
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "User-Agent": "sina-governance-worker-advisory",
      "X-GitHub-Api-Version": "2022-11-28",
      ...(init.headers || {}),
    },
  });

  const text = await response.text();
  if (!response.ok) {
    throw new Error(`GitHub API ${path} failed: HTTP ${response.status}: ${text}`);
  }
  return text ? JSON.parse(text) : {};
}

async function installationToken(appJwt) {
  const response = await githubJson(`/app/installations/${INSTALLATION_ID}/access_tokens`, appJwt, {
    method: "POST",
    body: "{}",
  });
  if (!response.token) throw new Error("installation token response did not include token");
  return response.token;
}

async function remoteHead(token) {
  const response = await githubJson(`/repos/${OWNER}/${REPO}/git/ref/heads/${BRANCH}`, token);
  const sha = response?.object?.sha;
  if (!sha) throw new Error("GitHub ref response did not include object.sha");
  return sha;
}

async function remoteSsotBytes(token) {
  const response = await githubJson(`/repos/${OWNER}/${REPO}/contents/${SSOT_PATH}?ref=${BRANCH}`, token);
  if (response.encoding !== "base64" || !response.content) {
    throw new Error("GitHub contents response did not include base64 content");
  }
  return base64ToBytes(response.content.replace(/\s+/g, ""));
}

async function sha256Hex(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function edgeMetadata(request, env) {
  const edgeExecutionProven = request.url.startsWith(env.WORKER_URL) && Boolean(request.headers.get("cf-ray"));
  const secondaryAccountProven = env.CF_ACCOUNT_ID === SECONDARY_CF_ACCOUNT_ID;

  return {
    cf_account_id: env.CF_ACCOUNT_ID,
    worker_url: env.WORKER_URL,
    cf_ray: request.headers.get("cf-ray"),
    edge_request_url: request.url,
    edge_request_timestamp: new Date().toISOString(),
    cf_colo: request.cf?.colo || null,
    cf_tls_version: request.cf?.tlsVersion || null,
    edge_execution_proven: edgeExecutionProven,
    secondary_account_proven: secondaryAccountProven,
    pass_eligible: edgeExecutionProven && secondaryAccountProven,
  };
}

async function buildReceipt(request, env) {
  const failures = [];
  const receipt = {
    receipt_id: crypto.randomUUID(),
    receipt_type: "REMOTE_CHECK_ADVISORY",
    status: "REMOTE_CHECK_ADVISORY_FAIL",
    result: "FAIL",
    pass_claimed: false,
    runtime_separation: "UNCONFIRMED",
    verifier_runtime: "cloudflare_worker",
    credential: "github_app_installation_token",
    ...edgeMetadata(request, env),
    app_id: APP_ID,
    installation_id: INSTALLATION_ID,
    repo: `${OWNER}/${REPO}`,
    branch: BRANCH,
    ssot_path: SSOT_PATH,
    expected_sha256: EXPECTED_SHA256,
    remote_head: null,
    remote_ssot_sha256: null,
    checked_at: new Date().toISOString(),
    failures,
  };

  try {
    const appJwt = await createJwt(env.GITHUB_APP_PRIVATE_KEY);
    const token = await installationToken(appJwt);
    receipt.remote_head = await remoteHead(token);
    receipt.remote_ssot_sha256 = await sha256Hex(await remoteSsotBytes(token));

    if (receipt.remote_ssot_sha256 !== EXPECTED_SHA256) {
      failures.push(`SSOT SHA256 expected ${EXPECTED_SHA256}, got ${receipt.remote_ssot_sha256}`);
    }
  } catch (error) {
    failures.push(error instanceof Error ? error.message : String(error));
  }

  if (failures.length === 0) {
    receipt.status = "REMOTE_CHECK_ADVISORY_MATCH";
    receipt.result = "MATCH";
  }

  if (receipt.pass_eligible) {
    receipt.runtime_separation = "SECONDARY_CF_ACCOUNT_EDGE_PROVEN";
  }

  return receipt;
}

async function writeReceipt(env, receipt) {
  const value = JSON.stringify(receipt, null, 2);
  await env.RECEIPTS.put(`receipt:${receipt.receipt_id}`, value);
  await env.RECEIPTS.put("latest", value);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/run") {
      const receipt = await buildReceipt(request, env);
      await writeReceipt(env, receipt);
      return jsonResponse(receipt, receipt.result === "MATCH" ? 200 : 502);
    }

    if (url.pathname === "/receipt/latest") {
      const receipt = await env.RECEIPTS.get("latest");
      if (!receipt) return jsonResponse({ error: "latest receipt not found" }, 404);
      return new Response(receipt, {
        headers: {
          "content-type": "application/json; charset=utf-8",
          "cache-control": "no-store",
        },
      });
    }

    return jsonResponse({
      service: "sina-governance-ssot-worker-advisory",
      endpoints: ["/run", "/receipt/latest"],
      pass_claimed: false,
    });
  },
};
