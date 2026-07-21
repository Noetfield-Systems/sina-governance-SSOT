import { handleMethod } from "./_proxy.js";

export async function onRequest(context) {
  return handleMethod(context, "GET", "/v1/runway/runtime");
}
