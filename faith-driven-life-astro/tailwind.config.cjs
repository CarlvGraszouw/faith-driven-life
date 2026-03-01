/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			fontFamily: {
				sans: ['Outfit', 'sans-serif'],
				serif: ['Source Serif 4', 'serif'],
			},
		},
	},
	plugins: [require("@tailwindcss/typography"), require("daisyui")],
	daisyui: {
		themes: [
			{
				faith: {
					primary: "#d4af37",
					"primary-content": "#0a1628",
					secondary: "#00d4ff",
					"secondary-content": "#0a1628",
					accent: "#d4af37",
					neutral: "#132238",
					"base-100": "#0a1628",
					"base-200": "#132238",
					"base-300": "#1a2d47",
					"base-content": "#f0f4f8",
					info: "#00d4ff",
					success: "#22c55e",
					warning: "#eab308",
					error: "#ef4444",
				},
			},
		],
		darkTheme: "faith",
		logs: false,
	},
}
