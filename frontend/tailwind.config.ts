import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        lacquer: "#110f0d",
        lacquerDeep: "#090806",
        raised: "#1d1915",
        kinpaku: "#e5bd3b",
        patina: "#25b7a6",
        rice: "#f6f0e4",
        ink: "#271c16",
      },
      boxShadow: {
        hairline: "inset 0 0 0 1px rgba(229,189,59,.22)",
      },
    },
  },
  plugins: [],
};

export default config;
