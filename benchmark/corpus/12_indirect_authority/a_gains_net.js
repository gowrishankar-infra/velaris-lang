// Reads a price from the shop's feed and prints it through a formatting library.
import { priceLine } from "./pricing.js";

const feed = (await new Response(Deno.stdin.readable).text()).trim();
try {
  const body = await (await fetch(feed)).text();
  console.log(priceLine("chai", body.length));
} catch (e) {
  console.log("no price feed: " + e.message);
}
