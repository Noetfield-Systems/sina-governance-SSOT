import assert from "node:assert/strict";
import { test } from "node:test";
import { webcrypto } from "node:crypto";

import {
  authorized,
  readJobRequest,
  RequestError,
  workflowInstanceId,
} from "../src/control-plane.js";

if (!globalThis.crypto) globalThis.crypto = webcrypto;

const jobs = [{ id: "proof_a_native_run", machine_safe: true }];

function request(body, headers = {}) {
  return new Request("https://example.test/jobs", {
    method: "POST",
    headers: { "content-type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
}

test("parses an explicit machine-safe commissioning job", async () => {
  const parsed = await readJobRequest(
    request({ job_id: "proof_a_native_run", request_id: "req-12345678" }),
    jobs,
  );
  assert.equal(parsed.jobId, "proof_a_native_run");
  assert.equal(parsed.requestId, "req-12345678");
  assert.equal(parsed.rerunReason, null);
});

test("rejects missing or unknown jobs", async () => {
  await assert.rejects(
    readJobRequest(request({ request_id: "req-12345678" }), jobs),
    (error) => error instanceof RequestError && error.code === "job_id_required",
  );
  await assert.rejects(
    readJobRequest(
      request({ job_id: "not-real", request_id: "req-12345678" }),
      jobs,
    ),
    (error) => error instanceof RequestError && error.code === "unknown_job_id",
  );
});

test("rejects unsafe jobs and malformed idempotency keys", async () => {
  await assert.rejects(
    readJobRequest(
      request({ job_id: "unsafe", request_id: "req-12345678" }),
      [{ id: "unsafe", machine_safe: false }],
    ),
    (error) => error instanceof RequestError && error.code === "job_not_machine_safe",
  );
  await assert.rejects(
    readJobRequest(
      request({ job_id: "proof_a_native_run", request_id: "short" }),
      jobs,
    ),
    (error) => error instanceof RequestError && error.code === "invalid_request_id",
  );
});

test("authenticates Bearer tokens without comparing plaintext", async () => {
  assert.deepEqual(
    await authorized(
      new Request("https://example.test/jobs", {
        headers: { authorization: "Bearer top-secret" },
      }),
      "top-secret",
    ),
    { ok: true, unavailable: false },
  );
  assert.deepEqual(
    await authorized(
      new Request("https://example.test/jobs", {
        headers: { authorization: "Bearer wrong" },
      }),
      "top-secret",
    ),
    { ok: false, unavailable: false },
  );
  assert.deepEqual(await authorized(new Request("https://example.test/jobs"), ""), {
    ok: false,
    unavailable: true,
  });
});

test("derives a stable opaque Workflow instance id", async () => {
  const first = await workflowInstanceId("req-12345678");
  const replay = await workflowInstanceId("req-12345678");
  const other = await workflowInstanceId("req-87654321");
  assert.equal(first, replay);
  assert.notEqual(first, other);
  assert.match(first, /^commission-[a-f0-9]{48}$/);
});
