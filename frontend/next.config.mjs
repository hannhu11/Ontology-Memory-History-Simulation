import path from "node:path";
import { fileURLToPath } from "node:url";

const apiOrigin = process.env.HISTORY_API_URL || "http://127.0.0.1:8601";
const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracingRoot: __dirname,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiOrigin}/api/:path*`,
      },
      {
        source: "/assets/:path*",
        destination: `${apiOrigin}/assets/:path*`,
      },
    ];
  },
};

export default nextConfig;
