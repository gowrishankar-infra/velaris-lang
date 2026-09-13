// Prints the app's settings, which a settings library reads from the data directory.
import { load } from "./settings.js";

console.log("settings: " + load());
