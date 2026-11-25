// news-image-20261125 — "Ember Strait": one-day world news image
// (Node 22, stdlib only).
//
// The entry is entry.png beside this file: a 1024x1024 newspaper front
// page summing up Wednesday 25 November 2026 in 35 dated stories across
// 6 regions (heroes: two tankers hit mines in the Strait of Hormuz, the
// KOSPI's 6.16% plunge, Ukrainian drones setting two Rosneft refineries
// ablaze; then ten illustrated cards, a map with numbered pins, and 22
// more stories). This program writes that exact image to the output
// directory, so the judge sees precisely these bytes. It refuses to
// finish unless the copy is a whole PNG inside the competition's size
// limits.
//
// Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const src = join(here, 'entry.png');
const dest = join(outDir, 'entry.png');

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message) {
  throw new Error(`entry image check failed: ${message}`);
}

const bytes = readFileSync(src);
if (bytes.length < 33) fail(`file is ${bytes.length} bytes, too short to be a PNG`);
if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) fail('not a PNG file');
if (bytes.length > 1048576) fail(`is ${bytes.length} bytes, over the 1 MiB cap`);

// IHDR sits right after the 8-byte signature: length, type "IHDR", then
// the width and height as big-endian 32-bit integers. The competition
// wants exactly 1024 by 1024 pixels, so refuse anything else here.
if (bytes.toString('ascii', 12, 16) !== 'IHDR') fail('has no IHDR chunk');
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  fail(`is ${width}x${height}, not the required 1024x1024`);
}

// A whole PNG ends with the IEND chunk: zero length, type "IEND", then a
// CRC. Refuse a truncated file instead of letting the judge see half an
// image.
const tail = bytes.subarray(bytes.length - 12);
if (tail.readUInt32BE(0) !== 0 || tail.toString('ascii', 4, 8) !== 'IEND') {
  fail('has no IEND chunk, it may be truncated');
}

mkdirSync(outDir, { recursive: true });
writeFileSync(dest, bytes);

const { size } = statSync(dest);
if (size !== bytes.length) fail(`copy mismatch: wrote ${size} of ${bytes.length} bytes`);
// Read the copy back and compare it byte for byte: the grader runs this
// program twice and both runs must write the same bytes, so prove the
// first write landed exactly before reporting success.
const written = readFileSync(dest);
if (!written.equals(bytes)) fail('copy differs from the source image');
console.log(`wrote ${dest} (${size} bytes, ${width}x${height})`);
