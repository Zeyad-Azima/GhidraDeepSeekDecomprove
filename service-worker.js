self.addEventListener("fetch", event => {
  const req = event.request;

  console.log(">>> Request:", req.method, req.url);
  for (let [k, v] of req.headers.entries()) {
    console.log(`    ${k}: ${v}`);
  }

  // Always let the request go through normally
  event.respondWith(fetch(req));
});
