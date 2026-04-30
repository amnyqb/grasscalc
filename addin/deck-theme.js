/**
 * Read PowerPoint's active deck theme via Office.js, unzip the .pptx, and
 * return ppt/theme/theme1.xml as a string. The chartsmith server's
 * theme_to_design_system tool can then ingest it directly.
 *
 * Depends on JSZip being available on `window` (loaded via <script> in
 * taskpane.html).
 */

const THEME_PATH_CANDIDATES = [
  "ppt/theme/theme1.xml",
  "ppt/theme/theme.xml",
];

/**
 * Pulls the compressed .pptx bytes from the host via getFileAsync slices.
 * Returns a Uint8Array.
 */
export async function readDeckBytes() {
  if (typeof Office === "undefined" || !Office.context?.document) {
    throw new Error("Office.js is not available; theme extraction only works inside PowerPoint.");
  }
  const file = await new Promise((resolve, reject) => {
    Office.context.document.getFileAsync(
      Office.FileType.Compressed,
      { sliceSize: 65536 },
      (r) => {
        if (r.status === Office.AsyncResultStatus.Failed) {
          reject(new Error(r.error?.message ?? "getFileAsync failed"));
        } else {
          resolve(r.value);
        }
      },
    );
  });

  try {
    const total = file.size;
    const sliceCount = file.sliceCount;
    const buf = new Uint8Array(total);
    let offset = 0;
    for (let i = 0; i < sliceCount; i++) {
      const slice = await new Promise((resolve, reject) => {
        file.getSliceAsync(i, (r) => {
          if (r.status === Office.AsyncResultStatus.Failed) {
            reject(new Error(r.error?.message ?? `getSliceAsync(${i}) failed`));
          } else {
            resolve(r.value);
          }
        });
      });
      // slice.data is either Uint8Array or array of bytes depending on host.
      const data = slice.data instanceof Uint8Array
        ? slice.data
        : new Uint8Array(slice.data);
      buf.set(data, offset);
      offset += data.length;
    }
    return buf;
  } finally {
    await new Promise((resolve) => file.closeAsync(() => resolve()));
  }
}

/**
 * Extract theme1.xml from a .pptx byte buffer.
 * Pure (doesn't touch Office.js); also used by tests.
 */
export async function extractThemeXmlFromPptx(bytes) {
  if (typeof JSZip === "undefined") {
    throw new Error("JSZip not loaded. Include it via <script> before this module.");
  }
  const zip = await JSZip.loadAsync(bytes);
  for (const path of THEME_PATH_CANDIDATES) {
    const entry = zip.file(path);
    if (entry) return await entry.async("string");
  }
  // Fallback: scan for any ppt/theme/*.xml in case Office numbered it differently.
  const candidates = [];
  zip.forEach((relPath) => {
    if (/^ppt\/theme\/theme\d*\.xml$/.test(relPath)) candidates.push(relPath);
  });
  if (candidates.length) {
    candidates.sort();
    return await zip.file(candidates[0]).async("string");
  }
  throw new Error("theme1.xml not found in .pptx");
}

/** Convenience: read deck bytes via Office.js and return theme1.xml. */
export async function readDeckTheme() {
  const bytes = await readDeckBytes();
  return await extractThemeXmlFromPptx(bytes);
}
