import { DurableObject } from "cloudflare:workers";

interface ReplayRecord {
  expiresAt: number;
}

export class ReplayGuard extends DurableObject<Env> {
  async claim(expiresAt: number, now = Date.now()): Promise<boolean> {
    if (!Number.isSafeInteger(expiresAt) || expiresAt <= now || expiresAt > now + 86_400_000) {
      throw new RangeError("replay claim expiry must be within 24 hours");
    }
    const existing = await this.ctx.storage.get<ReplayRecord>("claim");
    if (existing && existing.expiresAt > now) return false;
    await this.ctx.storage.put("claim", { expiresAt });
    await this.ctx.storage.setAlarm(expiresAt);
    return true;
  }

  override async alarm(): Promise<void> {
    await this.ctx.storage.deleteAll();
  }
}

export async function claimReplayKey(
  namespace: DurableObjectNamespace<ReplayGuard>,
  scope: "delivery" | "permit",
  key: string,
  expiresAt: number,
): Promise<boolean> {
  if (!/^[A-Za-z0-9._:-]{16,200}$/.test(key)) throw new TypeError("replay key format is invalid");
  const stub = namespace.getByName(`${scope}:${key}`);
  return stub.claim(expiresAt);
}
