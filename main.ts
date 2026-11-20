// news-image-20261119 -- entry program.
//
// The entry is one image: a newspaper front page summing up the world news
// of Thursday 19 November 2026, drawn programmatically by build_image.py
// and committed beside this file as entry.png. This program's only job is
// to hand that image to the judge at $MAKEFUN_OUTPUT_DIR/entry.png
// (default /output/entry.png).

import { mkdir, copyFile, stat } from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const src = resolve(here, "entry.png");
const dst = resolve(outDir, "entry.png");

async function main(): Promise<void> {
  if (!existsSync(src)) {
    throw new Error(`entry.png missing next to main.ts: ${src}`);
  }

  // Reject anything that is not a PNG before the judge ever sees it.
  const magic = readFileSync(src).subarray(0, 8);
  const PNG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  if (!magic.equals(PNG)) {
    throw new Error(`entry.png is not a PNG file: ${src}`);
  }

  const before = await stat(src);
  if (before.size > 1_048_576) {
    throw new Error(`entry.png is ${before.size} bytes, over the 1 MiB limit`);
  }

  await mkdir(outDir, { recursive: true });
  await copyFile(src, dst);

  const after = await stat(dst);
  console.log(`entry.png: ${after.size} bytes -> ${dst}`);
}

await main();
