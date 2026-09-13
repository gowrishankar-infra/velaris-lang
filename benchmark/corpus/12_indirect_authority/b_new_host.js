// Sends a receipt through a mail library; the program names no host itself.
import { send } from "./mailer.js";

const to = (await new Response(Deno.stdin.readable).text()).trim();
console.log(await send(to, "Your receipt: 2 items, 450"));
