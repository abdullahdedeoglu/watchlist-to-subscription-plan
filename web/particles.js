// Arka plandaki projektor tozu: yavasca yukari suzulen, parlayan ve goz
// kirpan kor parcaciklari. Uc katman derinlik (uzaktakiler kucuk, soluk,
// yavas); fare yaklasinca hafifce kenara kacarlar. Saf dekor - uygulamanin
// isleyisine dokunmaz. Hareket azaltma acikken hic calismaz.
(() => {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const canvas = document.createElement("canvas");
  canvas.className = "bg-particles";
  canvas.setAttribute("aria-hidden", "true");
  document.body.prepend(canvas);
  const ctx = canvas.getContext("2d");

  // Parlama bir kez cizilir, her karede kopyalanir (radial gradient her
  // karede cizmekten cok daha ucuz)
  const sprite = document.createElement("canvas");
  sprite.width = sprite.height = 64;
  const sctx = sprite.getContext("2d");
  const g = sctx.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, "rgba(255, 236, 200, 1)");
  g.addColorStop(0.12, "rgba(255, 214, 150, 1)");
  g.addColorStop(0.3, "rgba(255, 170, 80, 0.55)");
  g.addColorStop(0.55, "rgba(232, 130, 50, 0.15)");
  g.addColorStop(1, "rgba(232, 130, 50, 0)");
  sctx.fillStyle = g;
  sctx.fillRect(0, 0, 64, 64);

  let w = 0, h = 0, dpr = 1, parts = [];
  const mouse = { x: -9999, y: -9999 };

  function spawn(p, anywhere) {
    const depth = Math.random();             // 0 uzak, 1 yakin
    p.depth = depth;
    p.x = Math.random() * w;
    p.y = anywhere ? Math.random() * h : h + 20;
    p.size = 1.6 + depth * depth * 4.4;      // cizilen parlama yaricapi
    p.vy = -(0.08 + depth * 0.32);           // yukari suzulme
    p.vx = (Math.random() - 0.5) * 0.12;
    p.sway = Math.random() * Math.PI * 2;
    p.swaySpeed = 0.004 + Math.random() * 0.008;
    p.alpha = 0.5 + depth * 0.5;
    p.twinkle = Math.random() * Math.PI * 2;
    p.twinkleSpeed = 0.01 + Math.random() * 0.03;
    p.ox = 0; p.oy = 0;                      // fareden kacma ofseti
    return p;
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    w = window.innerWidth;
    h = window.innerHeight;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // yogunluk ekran alanina gore; telefonda az
    const target = Math.round(Math.min(160, Math.max(60, (w * h) / 11000)));
    while (parts.length < target) parts.push(spawn({}, true));
    parts.length = target;
  }

  window.addEventListener("resize", resize);
  window.addEventListener("pointermove", (e) => { mouse.x = e.clientX; mouse.y = e.clientY; }, { passive: true });
  document.addEventListener("pointerleave", () => { mouse.x = mouse.y = -9999; });

  let running = true;
  document.addEventListener("visibilitychange", () => {
    running = !document.hidden;
    if (running) requestAnimationFrame(frame);
  });

  let last = performance.now();
  function frame(now) {
    if (!running) return;
    // sekme arka plandan donunce sicrama olmasin
    const dt = Math.min((now - last) / 16.67, 3);
    last = now;

    ctx.clearRect(0, 0, w, h);
    ctx.globalCompositeOperation = "lighter";
    for (const p of parts) {
      p.sway += p.swaySpeed * dt;
      p.twinkle += p.twinkleSpeed * dt;
      p.x += (p.vx + Math.sin(p.sway) * 0.15) * dt;
      p.y += p.vy * dt;

      // fare 120px icindeyse yakin olanlar daha cok kacar
      const dx = p.x + p.ox - mouse.x, dy = p.y + p.oy - mouse.y;
      const d2 = dx * dx + dy * dy;
      if (d2 < 14400) {
        const f = (1 - Math.sqrt(d2) / 120) * (0.6 + p.depth * 1.6);
        const d = Math.sqrt(d2) || 1;
        p.ox += (dx / d) * f * dt;
        p.oy += (dy / d) * f * dt;
      }
      p.ox *= 0.96; p.oy *= 0.96;

      if (p.y < -20 || p.x < -20 || p.x > w + 20) spawn(p, false);

      const a = p.alpha * (0.55 + 0.45 * Math.sin(p.twinkle));
      const s = p.size * 2;
      ctx.globalAlpha = a;
      ctx.drawImage(sprite, p.x + p.ox - s, p.y + p.oy - s, s * 2, s * 2);
    }
    ctx.globalAlpha = 1;
    requestAnimationFrame(frame);
  }

  resize();
  requestAnimationFrame(frame);
})();
