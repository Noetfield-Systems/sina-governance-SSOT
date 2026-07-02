const APP_ID = "4179901";
const INSTALLATION_ID = "143449507";
const OWNER = "kazemnezhadsina144-dot";
const REPO = "sina-governance-SSOT";
const BRANCH = "main";
const SSOT_PATH = "ssot/strategy-ssot-v6-split.md";
const EXPECTED_SHA256 = "1ba4a793dba183388afd244ea21e850cad879c78824f78603e961070ae9b3af4";
const GITHUB_API = "https://api.github.com";
const SECONDARY_CF_ACCOUNT_ID = "b7282b4a5c17b84d62e3ef8866b878f8";
const ARTIFACT_DESCRIPTOR_SCHEMA = "sina-governance/verifier/brain-config-artifact-descriptor-schema-v0.1";
const KNOWLEDGE_BUNDLE_SPEC_PATH = "verifier/knowledge-bundle-spec-v0.1.md";
const BRAIN_WORKER_CODE_SPEC_PATH = "verifier/brain-worker-code-spec-v0.1.md";
const BRAIN_WORKER_BUNDLE_PATH = "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json";
const BRAIN_WORKER_CODE_PATHS = [
  "cloud/workers/sourcea-brain-chat-v1/src/index.js",
  "cloud/workers/sourcea-brain-chat-v1/src/guardrails.js",
  "cloud/workers/sourcea-brain-chat-v1/src/brain-core-gate-v1.js",
];
const ALLOWED_ARTIFACT_TYPES = new Set(["knowledge_bundle", "brain_worker_bundle"]);
const DEFAULT_CANDIDATE_REPO = `${OWNER}/${REPO}`;
const ALLOWED_CANDIDATE_REPOS = new Set([
  DEFAULT_CANDIDATE_REPO,
  `${OWNER}/SourceA`,
]);
const ARTIFACT_DESCRIPTOR_FIELDS = [
  "artifact_type",
  "artifact_path",
  "proposed_sha256",
  "base_sha256",
  "author_id",
  "subject",
  "schema_valid",
  "validator_runtime",
];
const KNOWLEDGE_BUNDLE_LIMITS = {
  maxBytes: 1_000_000,
  maxChunks: 2_000,
  maxChunkTextLength: 20_000,
};

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

async function remoteHead(token, repo = DEFAULT_CANDIDATE_REPO) {
  const response = await githubJson(`/repos/${repo}/git/ref/heads/${BRANCH}`, token);
  const sha = response?.object?.sha;
  if (!sha) throw new Error("GitHub ref response did not include object.sha");
  return sha;
}

async function remoteFileBytes(token, repo, path, ref = BRANCH) {
  const response = await githubJson(`/repos/${repo}/contents/${encodeURIComponent(path).replace(/%2F/g, "/")}?ref=${ref}`, token);
  if (response.encoding !== "base64" || !response.content) {
    throw new Error("GitHub contents response did not include base64 content");
  }
  return base64ToBytes(response.content.replace(/\s+/g, ""));
}

async function remoteSsotBytes(token) {
  return remoteFileBytes(token, DEFAULT_CANDIDATE_REPO, SSOT_PATH);
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

function validSha256(value) {
  return typeof value === "string" && /^[a-f0-9]{64}$/.test(value);
}

function validHex(value, minLength = 16) {
  return typeof value === "string" && value.length >= minLength && /^[a-f0-9]+$/.test(value);
}

function optionalString(value) {
  return typeof value === "string" && value.length > 0 ? value : null;
}

function validateArtifactDescriptor(descriptor, body = {}) {
  const failures = [];
  if (!descriptor || typeof descriptor !== "object" || Array.isArray(descriptor)) {
    return { descriptor: null, candidate_ref: null, candidate_path: null, failures: ["artifact descriptor must be a JSON object"] };
  }

  for (const field of ARTIFACT_DESCRIPTOR_FIELDS) {
    if (!(field in descriptor)) failures.push(`artifact descriptor missing ${field}`);
  }

  if (!ALLOWED_ARTIFACT_TYPES.has(descriptor.artifact_type)) {
    failures.push("artifact_type must be knowledge_bundle or brain_worker_bundle");
  }
  if (descriptor.artifact_type === "brain_worker_bundle") {
    if (!validSha256(descriptor.worker_code_sha256)) failures.push("worker_code_sha256 must be a lowercase SHA256 hex string");
    if (!validSha256(descriptor.knowledge_bundle_sha256)) {
      failures.push("knowledge_bundle_sha256 must be a lowercase SHA256 hex string");
    }
  }
  if (typeof descriptor.artifact_path !== "string" || descriptor.artifact_path.length === 0) {
    failures.push("artifact_path must be a non-empty string");
  }
  if (!validSha256(descriptor.proposed_sha256)) failures.push("proposed_sha256 must be a lowercase SHA256 hex string");
  if (!validSha256(descriptor.base_sha256)) failures.push("base_sha256 must be a lowercase SHA256 hex string");
  if (descriptor.author_id !== "sandbox") failures.push("author_id must be sandbox");
  if (descriptor.subject !== "live Worker") failures.push("subject must be live Worker");
  if (typeof descriptor.schema_valid !== "boolean") failures.push("schema_valid must be boolean");
  if (typeof descriptor.validator_runtime !== "string" || descriptor.validator_runtime.length === 0) {
    failures.push("validator_runtime must be a non-empty string");
  }
  const candidateRepo = optionalString(body.candidate_repo || descriptor.candidate_repo) || DEFAULT_CANDIDATE_REPO;
  if (!ALLOWED_CANDIDATE_REPOS.has(candidateRepo)) {
    failures.push(`candidate_repo must be one of ${[...ALLOWED_CANDIDATE_REPOS].join(", ")}`);
  }

  return {
    descriptor: {
      ...Object.fromEntries(ARTIFACT_DESCRIPTOR_FIELDS.map((field) => [field, descriptor[field]])),
      ...(descriptor.artifact_type === "brain_worker_bundle"
        ? {
            worker_code_sha256: descriptor.worker_code_sha256,
            knowledge_bundle_sha256: descriptor.knowledge_bundle_sha256,
          }
        : {}),
      candidate_repo: candidateRepo,
      candidate_ref: optionalString(body.candidate_ref || descriptor.candidate_ref),
    },
    candidate_repo: candidateRepo,
    candidate_ref: optionalString(body.candidate_ref || descriptor.candidate_ref),
    candidate_path:
      optionalString(body.candidate_path || descriptor.candidate_path) ||
      (descriptor.artifact_type === "brain_worker_bundle" ? BRAIN_WORKER_BUNDLE_PATH : null),
    failures,
  };
}

async function readArtifactDescriptor(request) {
  if (request.method !== "POST") return { descriptor: null, failures: [] };

  const contentType = request.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return { descriptor: null, failures: ["artifact descriptor POST must use application/json"] };
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return { descriptor: null, failures: ["artifact descriptor POST body must parse as JSON"] };
  }

  const descriptor = body.artifact_descriptor || body;
  return validateArtifactDescriptor(descriptor, body);
}

function validateKnowledgeBundleBytes(bytes, expectedSha256) {
  const failures = [];
  const checks = {
    bytes_utf8: false,
    json_parse: false,
    root_object: false,
    required_top_level_keys: false,
    chunks_non_empty_array: false,
    chunk_metadata_present: false,
    content_hashes_valid: false,
    size_bytes: bytes.length,
    chunks_count: 0,
  };

  if (bytes.length < 2) failures.push("candidate bundle is below minimum size");
  if (bytes.length > KNOWLEDGE_BUNDLE_LIMITS.maxBytes) failures.push("candidate bundle exceeds maximum size");

  const actualSha256Promise = sha256Hex(bytes);
  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    checks.bytes_utf8 = true;
  } catch {
    failures.push("candidate bundle bytes must decode as UTF-8");
  }

  let bundle;
  if (text !== undefined) {
    try {
      bundle = JSON.parse(text);
      checks.json_parse = true;
    } catch {
      failures.push("candidate bundle must parse as JSON");
    }
  }

  if (bundle && typeof bundle === "object" && !Array.isArray(bundle)) {
    checks.root_object = true;
  } else if (bundle !== undefined) {
    failures.push("candidate bundle root must be an object");
  }

  if (checks.root_object) {
    const legacyShape =
      typeof bundle.version === "string" &&
      bundle.version &&
      typeof bundle.generated_at === "string" &&
      bundle.generated_at &&
      validSha256(bundle.manifest_sha256);
    const sourceaShape =
      typeof bundle.bundle_version === "string" &&
      bundle.bundle_version &&
      typeof bundle.generated_at === "string" &&
      bundle.generated_at &&
      Number.isInteger(bundle.chunk_count);

    if ((legacyShape || sourceaShape) && "chunks" in bundle) {
      checks.required_top_level_keys = true;
    } else {
      failures.push("candidate bundle top-level keys invalid");
    }

    if (Array.isArray(bundle.chunks) && bundle.chunks.length > 0) {
      checks.chunks_non_empty_array = true;
      checks.chunks_count = bundle.chunks.length;
      if (bundle.chunks.length > KNOWLEDGE_BUNDLE_LIMITS.maxChunks) failures.push("candidate bundle has too many chunks");
    } else {
      failures.push("candidate bundle chunks must be a non-empty array");
    }

    let allMetadataPresent = Boolean(checks.chunks_non_empty_array);
    let allContentHashesValid = Boolean(checks.chunks_non_empty_array);
    for (const [index, chunk] of (Array.isArray(bundle.chunks) ? bundle.chunks : []).entries()) {
      if (!chunk || typeof chunk !== "object" || Array.isArray(chunk)) {
        failures.push(`chunk ${index} must be an object`);
        allMetadataPresent = false;
        allContentHashesValid = false;
        continue;
      }

      const legacyChunk =
        typeof chunk.id === "string" &&
        chunk.id &&
        typeof chunk.source === "string" &&
        chunk.source &&
        typeof chunk.title === "string" &&
        chunk.title &&
        typeof chunk.text === "string" &&
        chunk.text &&
        chunk.metadata &&
        typeof chunk.metadata === "object" &&
        !Array.isArray(chunk.metadata) &&
        typeof chunk.metadata.source_path === "string" &&
        chunk.metadata.source_path &&
        validSha256(chunk.metadata.content_sha256);

      const sourceaChunk =
        typeof chunk.id === "string" &&
        chunk.id &&
        typeof chunk.source_path === "string" &&
        chunk.source_path &&
        typeof chunk.content === "string" &&
        chunk.content &&
        validHex(chunk.content_hash) &&
        typeof chunk.lane === "string" &&
        chunk.lane &&
        typeof chunk.kind === "string" &&
        chunk.kind;

      if (!legacyChunk && !sourceaChunk) {
        failures.push(`chunk ${index} must match a supported knowledge bundle chunk shape`);
        allMetadataPresent = false;
        allContentHashesValid = false;
      }

      const text = typeof chunk.text === "string" ? chunk.text : chunk.content;
      if (typeof text === "string" && text.length > KNOWLEDGE_BUNDLE_LIMITS.maxChunkTextLength) {
        failures.push(`chunk ${index} text exceeds maximum length`);
      }
    }
    checks.chunk_metadata_present = allMetadataPresent;
    checks.content_hashes_valid = allContentHashesValid;
  }

  return actualSha256Promise.then((actualSha256) => {
    if (actualSha256 !== expectedSha256) {
      failures.push(`candidate SHA256 expected ${expectedSha256}, got ${actualSha256}`);
    }
    return { actualSha256, checks, failures };
  });
}

async function sha256FromSortedHashMap(map) {
  const sortedKeys = Object.keys(map).sort();
  const payload = JSON.stringify(Object.fromEntries(sortedKeys.map((key) => [key, map[key]])));
  return sha256Hex(new TextEncoder().encode(payload));
}

async function validateBrainWorkerBundle(token, repo, ref, descriptor) {
  const failures = [];
  const pathHashes = {};
  for (const path of [...BRAIN_WORKER_CODE_PATHS, BRAIN_WORKER_BUNDLE_PATH]) {
    const bytes = await remoteFileBytes(token, repo, path, ref);
    pathHashes[path] = await sha256Hex(bytes);
  }
  const workerMap = Object.fromEntries(BRAIN_WORKER_CODE_PATHS.map((path) => [path, pathHashes[path]]));
  const workerCodeActual = await sha256FromSortedHashMap(workerMap);
  const bundleBytes = await remoteFileBytes(token, repo, BRAIN_WORKER_BUNDLE_PATH, ref);
  const bundleValidation = await validateKnowledgeBundleBytes(bundleBytes, descriptor.knowledge_bundle_sha256);
  const proposedActual = await sha256FromSortedHashMap(pathHashes);

  if (workerCodeActual !== descriptor.worker_code_sha256) {
    failures.push(`worker_code_sha256 expected ${descriptor.worker_code_sha256}, got ${workerCodeActual}`);
  }
  if (proposedActual !== descriptor.proposed_sha256) {
    failures.push(`proposed_sha256 expected ${descriptor.proposed_sha256}, got ${proposedActual}`);
  }
  failures.push(...bundleValidation.failures);

  return {
    candidate_sha256: bundleValidation.actualSha256,
    knowledge_bundle_sha256: bundleValidation.actualSha256,
    worker_code_sha256: workerCodeActual,
    proposed_sha256: proposedActual,
    path_hashes: pathHashes,
    candidate_validation_checks: bundleValidation.checks,
    candidate_validation_failures: bundleValidation.failures,
    failures,
  };
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

async function buildReceipt(request, env, artifactDescriptorResult) {
  const failures = [];
  const artifactDescriptor = artifactDescriptorResult.descriptor;
  const hasArtifactDescriptor = Boolean(artifactDescriptor);
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
    artifact_descriptor_schema: ARTIFACT_DESCRIPTOR_SCHEMA,
    artifact_descriptor: artifactDescriptor,
    candidate_repo: artifactDescriptorResult.candidate_repo || DEFAULT_CANDIDATE_REPO,
    artifact_type: artifactDescriptor?.artifact_type || null,
    artifact_path: artifactDescriptor?.artifact_path || null,
    proposed_sha256: artifactDescriptor?.proposed_sha256 || null,
    base_sha256: artifactDescriptor?.base_sha256 || null,
    author_id: artifactDescriptor?.author_id || null,
    subject: artifactDescriptor?.subject || null,
    schema_valid: artifactDescriptor?.schema_valid ?? null,
    validator_runtime: artifactDescriptor?.validator_runtime || null,
    knowledge_bundle_spec_path: artifactDescriptor?.artifact_type === "knowledge_bundle" ? KNOWLEDGE_BUNDLE_SPEC_PATH : null,
    knowledge_bundle_spec_sha256: null,
    knowledge_bundle_spec_loaded: false,
    brain_worker_code_spec_path: artifactDescriptor?.artifact_type === "brain_worker_bundle" ? BRAIN_WORKER_CODE_SPEC_PATH : null,
    brain_worker_code_spec_sha256: null,
    brain_worker_code_spec_loaded: false,
    worker_code_sha256: artifactDescriptor?.worker_code_sha256 || null,
    knowledge_bundle_sha256: artifactDescriptor?.knowledge_bundle_sha256 || null,
    candidate_ref: artifactDescriptorResult.candidate_ref,
    candidate_path: artifactDescriptorResult.candidate_path,
    candidate_sha256: null,
    candidate_validation_checks: null,
    candidate_validation_failures: [],
    checked_at: new Date().toISOString(),
    failures,
  };

  failures.push(...artifactDescriptorResult.failures);
  if (artifactDescriptor?.artifact_type === "knowledge_bundle" || artifactDescriptor?.artifact_type === "brain_worker_bundle") {
    if (!artifactDescriptorResult.candidate_ref) failures.push("candidate_ref is required for artifact verification");
    if (!artifactDescriptorResult.candidate_path) failures.push("candidate_path is required for artifact verification");
  }

  try {
    const appJwt = await createJwt(env.GITHUB_APP_PRIVATE_KEY);
    const token = await installationToken(appJwt);
    receipt.remote_head = await remoteHead(token, DEFAULT_CANDIDATE_REPO);
    receipt.remote_ssot_sha256 = await sha256Hex(await remoteSsotBytes(token));

    if (artifactDescriptor?.artifact_type === "knowledge_bundle") {
      const specBytes = await remoteFileBytes(token, DEFAULT_CANDIDATE_REPO, KNOWLEDGE_BUNDLE_SPEC_PATH, receipt.remote_head);
      receipt.knowledge_bundle_spec_sha256 = await sha256Hex(specBytes);
      receipt.knowledge_bundle_spec_loaded = true;

      if (artifactDescriptorResult.candidate_ref && artifactDescriptorResult.candidate_path) {
        const candidateBytes = await remoteFileBytes(token, receipt.candidate_repo, artifactDescriptorResult.candidate_path, artifactDescriptorResult.candidate_ref);
        const validation = await validateKnowledgeBundleBytes(candidateBytes, artifactDescriptor.proposed_sha256);
        receipt.candidate_sha256 = validation.actualSha256;
        receipt.candidate_validation_checks = validation.checks;
        receipt.candidate_validation_failures = validation.failures;
        failures.push(...validation.failures);
      }
    }

    if (artifactDescriptor?.artifact_type === "brain_worker_bundle") {
      const specBytes = await remoteFileBytes(token, DEFAULT_CANDIDATE_REPO, BRAIN_WORKER_CODE_SPEC_PATH, receipt.remote_head);
      receipt.brain_worker_code_spec_sha256 = await sha256Hex(specBytes);
      receipt.brain_worker_code_spec_loaded = true;

      if (artifactDescriptorResult.candidate_ref) {
        const validation = await validateBrainWorkerBundle(
          token,
          receipt.candidate_repo,
          artifactDescriptorResult.candidate_ref,
          artifactDescriptor,
        );
        receipt.candidate_sha256 = validation.candidate_sha256;
        receipt.worker_code_sha256 = validation.worker_code_sha256;
        receipt.knowledge_bundle_sha256 = validation.knowledge_bundle_sha256;
        receipt.proposed_sha256 = validation.proposed_sha256;
        receipt.worker_path_hashes = validation.path_hashes;
        receipt.candidate_validation_checks = validation.candidate_validation_checks;
        receipt.candidate_validation_failures = validation.candidate_validation_failures;
        failures.push(...validation.failures);
      }
    }

    if (receipt.remote_ssot_sha256 !== EXPECTED_SHA256) {
      failures.push(`SSOT SHA256 expected ${EXPECTED_SHA256}, got ${receipt.remote_ssot_sha256}`);
    }
  } catch (error) {
    failures.push(error instanceof Error ? error.message : String(error));
  }

  if (hasArtifactDescriptor && !receipt.pass_eligible) {
    failures.push("PASS requires secondary account and edge execution proof");
  }

  if (failures.length === 0 && hasArtifactDescriptor) {
    receipt.status = "PASS";
    receipt.result = "PASS";
    receipt.pass_claimed = true;
  } else if (failures.length === 0) {
    receipt.status = "REMOTE_CHECK_ADVISORY_MATCH";
    receipt.result = "MATCH";
  } else if (hasArtifactDescriptor && failures.some((failure) => failure.includes("required") || failure.includes("not found") || failure.includes("failed: HTTP 404"))) {
    receipt.status = "BLOCKED";
    receipt.result = "BLOCKED";
  } else if (hasArtifactDescriptor) {
    receipt.status = "FAIL";
    receipt.result = "FAIL";
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
      const artifactDescriptorResult = await readArtifactDescriptor(request);
      const receipt = await buildReceipt(request, env, artifactDescriptorResult);
      await writeReceipt(env, receipt);
      return jsonResponse(receipt, ["MATCH", "PASS"].includes(receipt.result) ? 200 : 502);
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
