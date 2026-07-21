import { handleMethod } from "../_proxy.js";

export async function onRequest(context) {
  return handleMethod(context, "POST", "/v1/runway/receipts/verify");
}
