import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  images: {
    domains: ['localhost', '127.0.0.1'],
  },
  experimental: {
    serverComponentsExternalPackages: ['canvas'],
  },
};

export default nextConfig;
