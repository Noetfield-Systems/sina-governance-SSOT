const encoder = new TextEncoder();

export function canonicalJson(value: unknown): string {
  if (value === null || typeof value === "string" || typeof value === "boolean") {
    return JSON.stringify(value);
  }
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new TypeError("non-finite numbers are forbidden");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (typeof value === "object") {
    const object = value as Record<string, unknown>;
    const entries = Object.keys(object)
      .sort()
      .map((key) => {
        const child = object[key];
        if (child === undefined) throw new TypeError(`undefined field is forbidden: ${key}`);
        return `${JSON.stringify(key)}:${canonicalJson(child)}`;
      });
    return `{${entries.join(",")}}`;
  }
  throw new TypeError(`unsupported canonical JSON type: ${typeof value}`);
}

export function toBytes(value: string): Uint8Array<ArrayBuffer> {
  return encoder.encode(value) as Uint8Array<ArrayBuffer>;
}

export function bytesToHex(bytes: ArrayBuffer | Uint8Array): string {
  const view = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  return [...view].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

export function hexToBytes(hex: string): Uint8Array<ArrayBuffer> {
  if (hex.length % 2 !== 0 || !/^[a-f0-9]+$/i.test(hex)) throw new TypeError("invalid hex");
  const output = new Uint8Array(hex.length / 2);
  for (let index = 0; index < output.length; index += 1) {
    output[index] = Number.parseInt(hex.slice(index * 2, index * 2 + 2), 16);
  }
  return output as Uint8Array<ArrayBuffer>;
}

export function base64UrlEncode(bytes: ArrayBuffer | Uint8Array): string {
  const view = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let binary = "";
  for (const byte of view) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

export function base64UrlDecode(value: string): Uint8Array<ArrayBuffer> {
  if (!/^[A-Za-z0-9_-]+$/.test(value)) throw new TypeError("invalid base64url");
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "="));
  const output = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) output[index] = binary.charCodeAt(index);
  return output as Uint8Array<ArrayBuffer>;
}

export async function sha256Hex(value: string | ArrayBuffer | Uint8Array): Promise<string> {
  const bytes = typeof value === "string" ? toBytes(value) : value;
  return bytesToHex(await crypto.subtle.digest("SHA-256", bytes));
}
