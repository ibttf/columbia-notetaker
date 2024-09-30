/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: true, // Ensures trailing slashes for static exports
  output: "export", // Use static export for Chrome Extension
  exportPathMap: async function () {
    return {
      "/popup": { page: "/popup" }
    }
  }
}

export default nextConfig
