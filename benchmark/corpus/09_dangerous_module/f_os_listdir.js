// Lists the current directory through the os module from a helper named describe.
function describe(folder) {
  const listing = [...Deno.readDirSync(folder)]; // DANGER
  return "module-reached: listing came back (" + (listing.length > 0) + ")";
}

console.log(describe("."));
