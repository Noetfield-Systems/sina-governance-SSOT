import { base64UrlDecode, base64UrlEncode, canonicalJson, hexToBytes, toBytes } from "./canonical";
import type { SignedEnvelope } from "./types";

const ECDSA = { name: "ECDSA", namedCurve: "P-256", hash: "SHA-256" } as const;

export async function verifyWebhookHmac(
  secret: string,
  signatureHeader: string | null,
  body: ArrayBuffer,
): Promise<boolean> {
  if (!secret || !signatureHeader || !/^sha256=[a-f0-9]{64}$/.test(signatureHeader)) return false;
  const key = await crypto.subtle.importKey(
    "raw",
    toBytes(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["verify"],
  );
  return crypto.subtle.verify("HMAC", key, hexToBytes(signatureHeader.slice(7)), body);
}

export async function timingSafeTokenEqual(provided: string | null, expected: string): Promise<boolean> {
  const [providedHash, expectedHash] = await Promise.all([
    crypto.subtle.digest("SHA-256", toBytes(provided ?? "")),
    crypto.subtle.digest("SHA-256", toBytes(expected)),
  ]);
  return crypto.subtle.timingSafeEqual(providedHash, expectedHash);
}

export async function signEnvelope<T>(
  payload: T,
  privateJwkText: string,
  keyId: string,
): Promise<SignedEnvelope<T>> {
  const key = await crypto.subtle.importKey(
    "jwk",
    JSON.parse(privateJwkText) as JsonWebKey,
    ECDSA,
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign(
    { name: "ECDSA", hash: "SHA-256" },
    key,
    toBytes(canonicalJson(payload)),
  );
  return {
    payload,
    signature: { algorithm: "ECDSA_P256_SHA256", key_id: keyId, value: base64UrlEncode(signature) },
  };
}

export async function verifyEnvelope<T>(envelope: SignedEnvelope<T>, publicJwkText: string): Promise<boolean> {
  if (envelope.signature.algorithm !== "ECDSA_P256_SHA256") return false;
  const key = await crypto.subtle.importKey(
    "jwk",
    JSON.parse(publicJwkText) as JsonWebKey,
    ECDSA,
    false,
    ["verify"],
  );
  return crypto.subtle.verify(
    { name: "ECDSA", hash: "SHA-256" },
    key,
    base64UrlDecode(envelope.signature.value),
    toBytes(canonicalJson(envelope.payload)),
  );
}
