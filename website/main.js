(() => {
  const REPO = "Gixx/img2svg-icon-converter";
  const API = `https://api.github.com/repos/${REPO}/releases/latest`;
  const FALLBACK = `https://github.com/${REPO}/releases/latest`;

  const buttons = {
    windows: document.getElementById("btn-windows"),
    linux: document.getElementById("btn-linux"),
    macos: document.getElementById("btn-macos"),
  };
  const note = document.getElementById("release-note");

  const patterns = {
    windows: /Pixicon-windows-x64\.zip$/i,
    linux: /Pixicon-linux-x64\.tar\.gz$/i,
    macosArm: /Pixicon-macos-arm64\.zip$/i,
    macosIntel: /Pixicon-macos-x64\.zip$/i,
  };

  function preferMacAsset(assets) {
    const arm = assets.find((a) => patterns.macosArm.test(a.name));
    const intel = assets.find((a) => patterns.macosIntel.test(a.name));
    // Prefer Apple Silicon when both exist; Intel builds remain on the Releases page.
    if (arm) return { asset: arm, label: "Apple Silicon" };
    if (intel) return { asset: intel, label: "Intel" };
    return null;
  }

  function setButton(btn, href, meta) {
    if (!btn) return;
    btn.href = href;
    btn.classList.remove("is-loading", "is-missing");
    const metaEl = btn.querySelector("[data-meta]");
    if (metaEl) metaEl.textContent = meta;
  }

  function markMissing(btn) {
    if (!btn) return;
    btn.href = FALLBACK;
    btn.classList.add("is-missing");
    const metaEl = btn.querySelector("[data-meta]");
    if (metaEl) metaEl.textContent = "See releases";
  }

  Object.values(buttons).forEach((btn) => btn?.classList.add("is-loading"));

  fetch(API, {
    headers: { Accept: "application/vnd.github+json" },
  })
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then((release) => {
      const tag = release.tag_name || "latest";
      const assets = Array.isArray(release.assets) ? release.assets : [];

      const win = assets.find((a) => patterns.windows.test(a.name));
      const linux = assets.find((a) => patterns.linux.test(a.name));
      const mac = preferMacAsset(assets);

      if (win) setButton(buttons.windows, win.browser_download_url, tag);
      else markMissing(buttons.windows);

      if (linux) setButton(buttons.linux, linux.browser_download_url, tag);
      else markMissing(buttons.linux);

      if (mac) setButton(buttons.macos, mac.asset.browser_download_url, `${tag} · ${mac.label}`);
      else markMissing(buttons.macos);

      if (note) {
        const when = release.published_at
          ? new Date(release.published_at).toLocaleDateString(undefined, {
              year: "numeric",
              month: "short",
              day: "numeric",
            })
          : null;
        note.innerHTML = when
          ? `Latest: <strong>${tag}</strong> · ${when} · <a href="${FALLBACK}">all assets</a>`
          : `Latest: <strong>${tag}</strong> · <a href="${FALLBACK}">all assets</a>`;
      }
    })
    .catch(() => {
      Object.values(buttons).forEach(markMissing);
      if (note) {
        note.innerHTML = `Could not load release metadata. <a href="${FALLBACK}">Open latest release on GitHub</a>.`;
      }
    });
})();
