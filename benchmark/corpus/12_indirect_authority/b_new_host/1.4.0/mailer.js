// mailer 1.4.0: sends a message through the mail service's API.
export async function send(to, body) {
  try {
    await (await fetch("{url}/send", { method: "POST", body: `${to}\n${body}` })).text();
    return `sent to ${to}`;
  } catch (e) {
    return `not sent: ${e.message}`;
  }
}
