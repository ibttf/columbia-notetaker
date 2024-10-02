const path = require("path")
const HTMLPlugin = require("html-webpack-plugin")
const CopyPlugin = require("copy-webpack-plugin")

module.exports = {
  entry: {
    index: "./src/index.tsx"
  },
  mode: "production",
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: [
          "style-loader",
          "css-loader",
          {
            loader: "postcss-loader",
            options: {
              postcssOptions: {
                plugins: [
                  require("autoprefixer")() // Ensure you include valid PostCSS plugins here
                ]
              }
            }
          }
        ],
        exclude: /node_modules/
      },
      {
        test: /\.css$/i,
        exclude: /node_modules/,
        use: ["style-loader", "css-loader"]
      },
      {
        test: /\.svg$/, // Rule to handle .svg files
        use: [
          "@svgr/webpack", // Use svgr to import SVGs as React components
          "file-loader" // Fallback to file-loader for normal SVG imports
        ]
      }
    ]
  },
  plugins: [
    new CopyPlugin({
      patterns: [{ from: "manifest.json", to: "../manifest.json" }]
    }),
    ...getHtmlPlugins(["index"])
  ],
  resolve: {
    extensions: [".tsx", ".ts", ".js"]
  },
  output: {
    path: path.join(__dirname, "dist/js"),
    filename: "[name].js"
  }
}

function getHtmlPlugins(chunks) {
  return chunks.map(
    (chunk) =>
      new HTMLPlugin({
        title: "React extension",
        filename: `${chunk}.html`,
        chunks: [chunk]
      })
  )
}
